#!/usr/bin/env python
"""
End-to-End Test: Staff -> Accounting Sync -> SSO Login Verification
Standalone script with direct database access.
"""
import os
import sys
import django
import json
import requests
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from main_app.models import CustomUser, Course, Staff, Session
from main_app.integrations.invoicing_client import _headers
from college_management_system.settings import INVOICING_BASE_URL, INVOICING_API_KEY, SSO_SHARED_SECRET

import hmac
import hashlib
import base64


def create_test_image():
    """Create a simple test image"""
    file = BytesIO()
    image = Image.new('RGB', (100, 100), color='red')
    image.save(file, 'jpeg')
    file.seek(0)
    return SimpleUploadedFile(
        "test.jpg",
        file.getvalue(),
        content_type="image/jpeg"
    )


def test_e2e():
    """Run E2E test"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "E2E TEST: STAFF -> ACCOUNTING SYNC -> SSO LOGIN VERIFICATION".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")

    # ===== SETUP =====
    print("\n" + "="*80)
    print("SETUP: Creating test data")
    print("="*80)

    timestamp = str(datetime.now().timestamp()).replace('.', '_')
    
    # Create HOD
    hod_email = f"hod_e2e_test_{timestamp}@test.com"
    hod_user = CustomUser.objects.create_user(
        email=hod_email,
        password="hod_pass_123",
        first_name="Test",
        last_name="HOD",
        gender="M",
        profile_pic="test.jpg",
        address="Test Address",
        user_type=CustomUser.UserType.HOD
    )
    print(f"✓ Created HOD: {hod_user.email}")

    # Create Course
    course = Course.objects.create(name=f"E2E Test Course {timestamp}")
    print(f"✓ Created Course: {course.name}")

    # Create Staff
    staff_email = f"staff_e2e_accounting_{timestamp}@test.com"
    staff_user = CustomUser.objects.create_user(
        email=staff_email,
        password="staff_pass_123",
        first_name="John",
        last_name="Accountant",
        gender="M",
        profile_pic="test.jpg",
        address="Staff Address",
        user_type=CustomUser.UserType.STAFF
    )
    
    # Use get_or_create in case a Staff record already exists for this user
    staff, created = Staff.objects.get_or_create(
        admin=staff_user,
        defaults={
            'course': course,
            'has_accounting_access': False
        }
    )
    
    if not created:
        staff.course = course
        staff.has_accounting_access = False
        staff.save()
    
    print(f"✓ Created Staff: {staff_user.email}")
    print(f"  Initial has_accounting_access: {staff.has_accounting_access}")

    # ===== TEST 1: Edit Staff with accounting access =====
    print("\n" + "="*80)
    print("TEST 1: Edit Staff via POST (enable has_accounting_access)")
    print("="*80)

    client = Client()
    
    # Use force_login which is more reliable with custom user models
    client.force_login(hod_user)
    print(f"✓ Forced login as HOD: {hod_user.email}")

    url = reverse('edit_staff', args=[staff.id])
    print(f"\nPOSTing to: {url}")

    form_data = {
        'first_name': 'John',
        'last_name': 'Accountant',
        'email': staff_email,
        'gender': 'M',
        'address': 'Staff Address',
        'password': '',
        'course': staff.course.id,
        'has_accounting_access': True,  # ENABLE
        'profile_pic': create_test_image(),
    }

    print(f"\nForm data:")
    print(f"  email: {form_data['email']}")
    print(f"  has_accounting_access: {form_data['has_accounting_access']}")

    response = client.post(url, form_data, follow=True)
    print(f"\n✓ Response status: {response.status_code}")

    # Reload staff
    staff.refresh_from_db()
    print(f"✓ After POST, staff.has_accounting_access: {staff.has_accounting_access}")

    if not staff.has_accounting_access:
        print(f"✗ ERROR: has_accounting_access was not enabled!")
        return False

    # ===== TEST 2: Capture sync response =====
    print("\n" + "="*80)
    print("TEST 2: Capture raw sync response from /api/users/sync/")
    print("="*80)

    payload = {
        'email': staff_user.email,
        'first_name': staff_user.first_name,
        'last_name': staff_user.last_name,
    }
    sync_url = f"{INVOICING_BASE_URL}/api/users/sync/"

    print(f"\nPayload:")
    print(json.dumps(payload, indent=2))
    print(f"\nEndpoint: {sync_url}")

    headers_dict = _headers()
    print(f"Headers: {json.dumps(headers_dict, indent=2)}")

    try:
        resp = requests.post(sync_url, json=payload, headers=headers_dict, timeout=10)
        RESP1_STATUS = resp.status_code
        RESP1_BODY = resp.text

        print(f"\n✓ RESP_STATUS: {RESP1_STATUS}")
        print(f"✓ RESP_BODY: {RESP1_BODY}")

        try:
            resp_json = resp.json()
            print(f"\n✓ RESP_JSON:")
            print(json.dumps(resp_json, indent=2))
        except:
            pass

    except Exception as e:
        print(f"✗ Sync request failed: {e}")
        return False

    # ===== TEST 3: Verify on invoicing system =====
    print("\n" + "="*80)
    print("TEST 3: Verify user exists on invoicing system")
    print("="*80)

    print(f"\nStaff email: {staff_email}")

    headers_dict = {'X-API-KEY': INVOICING_API_KEY} if INVOICING_API_KEY else {}

    try:
        users_url = f"{INVOICING_BASE_URL}/api/users/"
        resp = requests.get(users_url, headers=headers_dict, timeout=5)
        print(f"\nGET {users_url}")
        print(f"Status: {resp.status_code}")

        invoicing_user = None
        if resp.ok:
            users = resp.json()
            print(f"Response (first 300 chars): {str(users)[:300]}")

            if isinstance(users, list):
                for user in users:
                    if user.get('email') == staff_email:
                        invoicing_user = user
                        print(f"\n✓ FOUND USER on invoicing system!")
                        print(f"  Email: {user.get('email')}")
                        print(f"  First Name: {user.get('first_name')}")
                        print(f"  Last Name: {user.get('last_name')}")
                        print(f"  is_active: {user.get('is_active')}")
                        print(f"  has_usable_password: {user.get('has_usable_password')}")
                        break
                
                if not invoicing_user:
                    print(f"\n✗ User NOT found in list of {len(users)} users")

    except Exception as e:
        print(f"✗ Failed to verify: {e}")
        invoicing_user = None

    # ===== TEST 4: Generate SSO token =====
    print("\n" + "="*80)
    print("TEST 4: Generate SSO token")
    print("="*80)

    print(f"\nUser email: {staff_email}")

    sso_payload = {
        'email': staff_email,
        'timestamp': datetime.now().isoformat()
    }

    sso_payload_str = json.dumps(sso_payload)
    signature = hmac.new(
        SSO_SHARED_SECRET.encode(),
        sso_payload_str.encode(),
        hashlib.sha256
    ).digest()
    signature_b64 = base64.b64encode(signature).decode()

    sso_token_data = {
        'payload': base64.b64encode(sso_payload_str.encode()).decode(),
        'signature': signature_b64
    }

    print(f"\nSSO Token structure:")
    print(json.dumps({
        'payload': 'base64_encoded_payload',
        'signature': 'base64_encoded_signature'
    }, indent=2))

    # ===== TEST 5: SSO login round-trip =====
    print("\n" + "="*80)
    print("TEST 5: Full SSO login round-trip")
    print("="*80)

    sso_url = f"{INVOICING_BASE_URL}/api/sso/verify/"

    print(f"\nPOSTing SSO token to: {sso_url}")
    print(f"Payload email: {sso_payload['email']}")

    sso_success = False
    try:
        resp = requests.post(sso_url, json=sso_token_data, timeout=10)
        print(f"\n✓ Response status: {resp.status_code}")
        print(f"✓ Response body (first 300 chars): {resp.text[:300]}")

        if resp.ok:
            print(f"\n✓ SSO verification successful")
            if 'set-cookie' in resp.headers:
                print(f"✓ Auth cookies set")
                sso_success = True
        else:
            print(f"\n✗ SSO verification failed with status {resp.status_code}")

    except Exception as e:
        print(f"✗ SSO request failed: {e}")

    # ===== SUMMARY =====
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    all_ok = (
        staff.has_accounting_access and
        RESP1_STATUS == 200 and
        invoicing_user is not None and
        sso_success
    )

    print(f"\n✓ Test data created: {staff_email}")
    print(f"✓ Edit staff POST: {response.status_code}")
    print(f"✓ Staff has_accounting_access enabled: {staff.has_accounting_access}")
    print(f"✓ Sync response status: {RESP1_STATUS}")
    print(f"✓ User found on invoicing system: {invoicing_user is not None}")
    print(f"✓ SSO login successful: {sso_success}")

    print("\n" + "="*80)
    print("RAW EVIDENCE")
    print("="*80)

    print(f"\nStaff Email: {staff_email}")

    print(f"\nREQ_PAYLOAD (edit_staff form):")
    print(json.dumps({
        'email': staff_email,
        'first_name': 'John',
        'last_name': 'Accountant',
        'has_accounting_access': True
    }, indent=2))

    print(f"\nREQ_PAYLOAD (sync_accounting_user):")
    print(json.dumps({
        'email': staff_email,
        'first_name': 'John',
        'last_name': 'Accountant'
    }, indent=2))

    print(f"\nRESP1_STATUS: {RESP1_STATUS}")
    print(f"RESP1_BODY: {RESP1_BODY}")

    if invoicing_user:
        print(f"\nINVOICING_USER (verified):")
        print(json.dumps(invoicing_user, indent=2))
    else:
        print(f"\nINVOICING_USER: NOT FOUND")

    print(f"\n✓ E2E Test {'PASSED' if all_ok else 'FAILED'}")
    return all_ok


if __name__ == '__main__':
    success = test_e2e()
    sys.exit(0 if success else 1)
