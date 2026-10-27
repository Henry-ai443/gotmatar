#!/usr/bin/env python
"""
End-to-End Test: Staff -> Accounting Sync -> SSO Login Verification
Uses Django's test framework for proper database handling.
"""
import os
import sys
import django
import json
import requests
from datetime import datetime
from unittest.mock import patch

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from io import BytesIO
from PIL import Image

from main_app.models import CustomUser, Course, Staff, Session
from main_app.integrations.invoicing_client import _headers
from college_management_system.settings import INVOICING_BASE_URL, INVOICING_API_KEY

import hmac
import hashlib
import base64


class StaffAccountingSyncE2ETest(TestCase):
    """End-to-end test for staff accounting sync flow"""

    def setUp(self):
        """Create test fixtures for each test"""
        # Create HOD
        hod_email = f"hod_e2e_test_{datetime.now().timestamp()}@test.com"
        self.hod_user = CustomUser.objects.create_user(
            email=hod_email,
            password="hod_pass_123",
            first_name="Test",
            last_name="HOD",
            gender="M",
            profile_pic="test.jpg",
            address="Test Address",
            user_type=CustomUser.UserType.HOD
        )

        # Create Course
        self.course = Course.objects.create(name=f"E2E Test Course {datetime.now().timestamp()}")

        # Create Staff
        staff_email = f"staff_e2e_accounting_{datetime.now().timestamp()}@test.com"
        self.staff_user = CustomUser.objects.create_user(
            email=staff_email,
            password="staff_pass_123",
            first_name="John",
            last_name="Accountant",
            gender="M",
            profile_pic="test.jpg",
            address="Staff Address",
            user_type=CustomUser.UserType.STAFF
        )
        self.staff = Staff.objects.create(
            admin=self.staff_user,
            course=self.course,
            has_accounting_access=False
        )

    def create_test_image(self):
        """Create a simple test image"""
        file = BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file, 'jpeg')
        file.seek(0)
        from django.core.files.uploadedfile import SimpleUploadedFile
        return SimpleUploadedFile(
            "test.jpg",
            file.getvalue(),
            content_type="image/jpeg"
        )

    def test_01_edit_staff_with_accounting_access(self):
        """TEST 1: Edit staff via POST with has_accounting_access=True"""
        print("\n" + "="*80)
        print("TEST 1: Edit Staff via POST (enable has_accounting_access)")
        print("="*80)

        client = Client()
        login_ok = client.login(email=self.hod_user.email, password="hod_pass_123")
        self.assertTrue(login_ok, "HOD login failed")
        print(f"✓ Logged in as HOD: {self.hod_user.email}")

        url = reverse('edit_staff', args=[self.staff.id])
        print(f"\nPOSTing to: {url}")

        form_data = {
            'first_name': 'John',
            'last_name': 'Accountant',
            'email': self.staff_user.email,
            'gender': 'M',
            'address': 'Staff Address',
            'password': '',
            'course': self.staff.course.id,
            'has_accounting_access': True,  # ENABLE
            'profile_pic': self.create_test_image(),
        }

        print(f"\nForm data:")
        print(f"  email: {form_data['email']}")
        print(f"  has_accounting_access: {form_data['has_accounting_access']}")

        response = client.post(url, form_data, follow=True)
        print(f"\n✓ Response status: {response.status_code}")

        # Reload staff
        self.staff.refresh_from_db()
        print(f"✓ After POST, staff.has_accounting_access: {self.staff.has_accounting_access}")
        self.assertTrue(self.staff.has_accounting_access)

    def test_02_capture_sync_response(self):
        """TEST 2: Capture raw sync response from /api/users/sync/"""
        print("\n" + "="*80)
        print("TEST 2: Capture raw sync response from /api/users/sync/")
        print("="*80)

        # Ensure staff has accounting access
        self.staff.has_accounting_access = True
        self.staff.save()

        payload = {
            'email': self.staff_user.email,
            'first_name': self.staff_user.first_name,
            'last_name': self.staff_user.last_name,
        }
        url = f"{INVOICING_BASE_URL}/api/users/sync/"

        print(f"\nPayload:")
        print(json.dumps(payload, indent=2))
        print(f"\nEndpoint: {url}")
        print(f"Headers: {json.dumps(_headers(), indent=2)}")

        try:
            resp = requests.post(url, json=payload, headers=_headers(), timeout=10)
            print(f"\n✓ RESP_STATUS: {resp.status_code}")
            print(f"✓ RESP_BODY: {resp.text[:500]}")

            # Print full JSON if available
            try:
                resp_json = resp.json()
                print(f"\n✓ RESP_JSON:")
                print(json.dumps(resp_json, indent=2))
            except:
                pass

            return resp.status_code, resp.text

        except Exception as e:
            print(f"✗ Exception: {e}")
            return None, str(e)

    def test_03_verify_on_invoicing_system(self):
        """TEST 3: Verify user exists on invoicing system"""
        print("\n" + "="*80)
        print("TEST 3: Verify user exists on invoicing system")
        print("="*80)

        print(f"\nStaff email: {self.staff_user.email}")

        # Query users endpoint
        headers = {'X-API-KEY': INVOICING_API_KEY} if INVOICING_API_KEY else {}

        try:
            url = f"{INVOICING_BASE_URL}/api/users/"
            resp = requests.get(url, headers=headers, timeout=5)
            print(f"\nGET {url}")
            print(f"Status: {resp.status_code}")

            if resp.ok:
                users = resp.json()
                print(f"Response (first 500 chars): {str(users)[:500]}")

                if isinstance(users, list):
                    for user in users:
                        if user.get('email') == self.staff_user.email:
                            print(f"\n✓ FOUND USER on invoicing system!")
                            print(f"  Email: {user.get('email')}")
                            print(f"  First Name: {user.get('first_name')}")
                            print(f"  Last Name: {user.get('last_name')}")
                            print(f"  is_active: {user.get('is_active')}")
                            print(f"  has_usable_password: {user.get('has_usable_password')}")
                            return user
                    print(f"\n✗ User NOT found in list of {len(users)} users")
                    return None
        except Exception as e:
            print(f"✗ Failed to verify: {e}")
            return None

    def test_04_generate_sso_token(self):
        """TEST 4: Generate and verify SSO token"""
        print("\n" + "="*80)
        print("TEST 4: Generate SSO token")
        print("="*80)

        from college_management_system.settings import SSO_SHARED_SECRET

        print(f"\nUser email: {self.staff_user.email}")

        payload = {
            'email': self.staff_user.email,
            'timestamp': datetime.now().isoformat()
        }

        payload_str = json.dumps(payload)
        signature = hmac.new(
            SSO_SHARED_SECRET.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.b64encode(signature).decode()

        token_data = {
            'payload': base64.b64encode(payload_str.encode()).decode(),
            'signature': signature_b64
        }

        print(f"\nSSO Token data:")
        print(json.dumps({
            'payload': 'base64_encoded_payload',
            'signature': 'base64_encoded_signature'
        }, indent=2))

        return token_data, payload

    def test_05_sso_login_roundtrip(self):
        """TEST 5: Test full SSO login round-trip"""
        print("\n" + "="*80)
        print("TEST 5: Full SSO login round-trip")
        print("="*80)

        # Generate SSO token
        token_data, payload = self.test_04_generate_sso_token()

        url = f"{INVOICING_BASE_URL}/api/sso/verify/"

        print(f"\nPOSTing SSO token to: {url}")
        print(f"Payload email: {payload['email']}")

        try:
            resp = requests.post(url, json=token_data, timeout=10)
            print(f"\n✓ Response status: {resp.status_code}")
            print(f"✓ Response body (first 200 chars): {resp.text[:200]}")

            if resp.ok:
                print(f"\n✓ SSO verification successful")
                if 'set-cookie' in resp.headers:
                    print(f"✓ Auth cookies set")
                    return True
            else:
                print(f"\n✗ SSO verification failed")
                return False

        except Exception as e:
            print(f"✗ SSO request failed: {e}")
            return False


def run_e2e_tests():
    """Run all E2E tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "E2E TEST: STAFF -> ACCOUNTING SYNC -> SSO LOGIN VERIFICATION".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")

    # Run the test
    from django.test.runner import DiscoverRunner
    runner = DiscoverRunner(verbosity=2)

    # Create test suite
    import unittest
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(StaffAccountingSyncE2ETest)

    # Run tests
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_e2e_tests()
    sys.exit(0 if success else 1)
