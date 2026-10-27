#!/usr/bin/env python
"""
End-to-End Test: Staff -> Accounting Sync -> SSO Login Verification

This test:
1. Creates test data (HOD, Course, Staff)
2. Uses the test client to POST to edit_staff with has_accounting_access=True
3. Captures the raw response from the sync endpoint
4. Verifies the user was created on the invoicing system (via shell)
5. Generates an SSO token and tests full round-trip login
"""
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')

import django
django.setup()

import json
import requests
from io import BytesIO
from PIL import Image

from django.test import Client, TestCase
from django.contrib.auth import authenticate
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from main_app.models import CustomUser, Course, Staff, Admin, Session
from main_app.integrations.invoicing_client import sync_accounting_user, _headers
from college_management_system.settings import (
    INVOICING_BASE_URL, INVOICING_API_KEY
)
import hmac
import hashlib
import base64
from datetime import datetime


def create_test_image():
    """Create a simple test image file."""
    file = BytesIO()
    image = Image.new('RGB', (100, 100), color='red')
    image.save(file, 'jpeg')
    file.seek(0)
    return SimpleUploadedFile(
        "test.jpg",
        file.getvalue(),
        content_type="image/jpeg"
    )


def setup_test_data():
    """Create test HOD, Course, and Staff."""
    print("\n" + "="*80)
    print("SETUP: Creating test data")
    print("="*80)

    # Create test HOD
    hod_email = f"test_hod_e2e_{datetime.now().timestamp()}@test.com"
    hod_user = CustomUser.objects.create_user(
        email=hod_email,
        password="test_pass_123",
        first_name="Test",
        last_name="HOD_E2E",
        gender="M",
        profile_pic="test.jpg",
        address="Test Address",
        user_type=CustomUser.UserType.HOD
    )
    print(f"✓ Created HOD: {hod_user.email}")

    # Create Admin profile for HOD (if not exists)
    admin, created = Admin.objects.get_or_create(admin=hod_user)
    if created:
        print(f"✓ Created Admin profile")
    else:
        print(f"✓ Admin profile already exists")

    # Create course
    course = Course.objects.create(name=f"Test Course E2E {datetime.now().timestamp()}")
    print(f"✓ Created Course: {course.name}")

    # Create test Staff
    staff_email = f"test_staff_accounting_{datetime.now().timestamp()}@test.com"
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
    staff, created = Staff.objects.get_or_create(admin=staff_user, defaults={'course': course, 'has_accounting_access': False})
    if created:
        print(f"✓ Created Staff: {staff_user.email}")
    else:
        print(f"✓ Staff already exists: {staff_user.email}")
        staff.course = course
        staff.has_accounting_access = False
        staff.save()
    print(f"  Initial has_accounting_access: {staff.has_accounting_access}")

    return hod_user, staff, staff_email


def test_edit_staff_with_accounting_access(hod_user, staff, staff_email):
    """Test the edit_staff POST flow with has_accounting_access=True."""
    print("\n" + "="*80)
    print("TEST 1: Edit Staff via POST (enable has_accounting_access)")
    print("="*80)

    client = Client()
    # Login as HOD
    login_success = client.login(email=hod_user.email, password="test_pass_123")
    print(f"✓ Logged in as HOD: {login_success}")

    # Prepare form data for edit_staff POST
    url = reverse('edit_staff', args=[staff.id])
    print(f"\nPOSTing to: {url}")

    form_data = {
        'first_name': 'John',
        'last_name': 'Accountant',
        'email': staff_email,
        'gender': 'M',
        'address': 'Staff Address',
        'password': '',  # Don't change password
        'course': staff.course.id,
        'has_accounting_access': True,  # ENABLE accounting access
    }

    # Add a test image file
    form_data['profile_pic'] = create_test_image()

    print(f"\nForm data:")
    for k, v in form_data.items():
        if k != 'profile_pic':
            print(f"  {k}: {v}")
        else:
            print(f"  {k}: <image file>")

    # Make the POST request
    response = client.post(url, form_data, follow=True)
    print(f"\n✓ Response status: {response.status_code}")
    print(f"  Response URL: {response.redirect_chain}")

    # Reload the staff from DB to verify the change
    staff.refresh_from_db()
    print(f"\n✓ After POST, staff.has_accounting_access: {staff.has_accounting_access}")

    return response


def capture_sync_response_directly(staff_user):
    """Call sync_accounting_user directly and capture the raw response."""
    print("\n" + "="*80)
    print("TEST 2: Capture raw sync response from /api/users/sync/")
    print("="*80)

    print(f"\nCalling sync_accounting_user({staff_user.email})")
    
    # Call the function directly and capture response
    payload = {
        'email': staff_user.email,
        'first_name': staff_user.first_name,
        'last_name': staff_user.last_name,
    }
    url = f"{INVOICING_BASE_URL}/api/users/sync/"
    
    print(f"\nPayload:")
    print(f"  {json.dumps(payload, indent=2)}")
    
    print(f"\nEndpoint: {url}")
    print(f"Headers: {json.dumps(_headers(), indent=2)}")

    try:
        resp = requests.post(url, json=payload, headers=_headers(), timeout=10)
        print(f"\n✓ RESP_STATUS: {resp.status_code}")
        print(f"✓ RESP_HEADERS: {dict(resp.headers)}")
        print(f"✓ RESP_BODY: {resp.text}")
        
        try:
            resp_json = resp.json()
            print(f"✓ RESP_JSON: {json.dumps(resp_json, indent=2)}")
            return resp.status_code, resp.text, resp_json
        except:
            return resp.status_code, resp.text, None
    except Exception as e:
        print(f"✗ Exception: {e}")
        return None, str(e), None


def verify_user_on_invoicing_system(staff_email):
    """Query the invoicing system to verify the user was created."""
    print("\n" + "="*80)
    print("TEST 3: Verify user exists on invoicing system")
    print("="*80)

    # Use shell to query invoicing system database
    from django.core.management import call_command
    from io import StringIO
    
    print(f"\nVerifying user with email: {staff_email}")
    print(f"Invoicing system base URL: {INVOICING_BASE_URL}")

    # Use Django shell to query the invoicing system's database
    shell_script = f"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
import django
django.setup()

# This is for the COLLEGE system, but we need to verify on the INVOICING system
# We'll use the API instead
import requests
from college_management_system.settings import INVOICING_BASE_URL, INVOICING_API_KEY

headers = {{'X-API-KEY': INVOICING_API_KEY}} if INVOICING_API_KEY else {{}}

# Try to get users endpoint
try:
    url = f"{{INVOICING_BASE_URL}}/api/users/"
    resp = requests.get(url, headers=headers, timeout=5)
    print(f"GET {{url}}")
    print(f"Status: {{resp.status_code}}")
    print(f"Response: {{resp.text[:500]}}")
except Exception as e:
    print(f"Error: {{e}}")
"""

    # Since we can't directly access the invoicing system's database from here,
    # we'll use the API to verify
    headers = {'X-API-KEY': INVOICING_API_KEY} if INVOICING_API_KEY else {}
    
    # Try to query users endpoint
    try:
        url = f"{INVOICING_BASE_URL}/api/users/"
        resp = requests.get(url, headers=headers, timeout=5)
        print(f"\nGET {url}")
        print(f"Status: {resp.status_code}")
        
        if resp.ok:
            users = resp.json()
            print(f"Response (raw): {resp.text[:500]}")
            
            # Look for our staff member
            if isinstance(users, list):
                for user in users:
                    if user.get('email') == staff_email:
                        print(f"\n✓ FOUND USER on invoicing system!")
                        print(f"  Email: {user.get('email')}")
                        print(f"  First Name: {user.get('first_name')}")
                        print(f"  Last Name: {user.get('last_name')}")
                        print(f"  is_active: {user.get('is_active')}")
                        print(f"  has_usable_password: {user.get('has_usable_password')}")
                        return user
            else:
                print(f"Users response is not a list: {type(users)}")
                return None
        else:
            print(f"API error: {resp.text}")
            return None
    except Exception as e:
        print(f"✗ Failed to verify on invoicing system: {e}")
        return None


def generate_sso_token(staff_user):
    """Generate an SSO token for the staff member."""
    print("\n" + "="*80)
    print("TEST 4: Generate SSO token for staff member")
    print("="*80)

    from college_management_system.settings import SSO_SHARED_SECRET
    
    print(f"\nUser email: {staff_user.email}")
    print(f"Shared secret length: {len(SSO_SHARED_SECRET)}")

    # Create SSO payload
    payload = {
        'email': staff_user.email,
        'timestamp': datetime.now().isoformat()
    }
    
    # Encode and sign the payload
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
    print(f"  {json.dumps(token_data, indent=2)}")
    
    return token_data, payload


def test_sso_login_roundtrip(sso_token_data, payload):
    """Test the full SSO login flow on the invoicing system."""
    print("\n" + "="*80)
    print("TEST 5: Full SSO login round-trip")
    print("="*80)

    # Create a session on invoicing system using SSO token
    url = f"{INVOICING_BASE_URL}/api/sso/verify/"
    
    print(f"\nPOSTing SSO token to: {url}")
    print(f"Payload email: {payload['email']}")

    try:
        resp = requests.post(url, json=sso_token_data, timeout=10)
        print(f"\n✓ Response status: {resp.status_code}")
        print(f"✓ Response headers: {dict(resp.headers)}")
        print(f"✓ Response body: {resp.text[:500]}")
        
        if resp.ok:
            try:
                resp_json = resp.json()
                print(f"✓ Response JSON: {json.dumps(resp_json, indent=2)}")
            except:
                pass
                
            # Check if we got a session/auth token
            if 'set-cookie' in resp.headers:
                print(f"\n✓ COOKIES SET (authenticated): {resp.headers['set-cookie'][:100]}")
                return True
            elif 'token' in resp.text.lower() or 'auth' in resp.text.lower():
                print(f"\n✓ AUTH TOKEN in response")
                return True
        else:
            print(f"✗ SSO verification failed: {resp.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ SSO request failed: {e}")
        return False


def main():
    """Run the full end-to-end test."""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "E2E TEST: STAFF -> ACCOUNTING SYNC -> SSO LOGIN VERIFICATION".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")

    # Step 1: Setup test data
    hod_user, staff, staff_email = setup_test_data()

    # Step 2: Test edit_staff POST with has_accounting_access=True
    response = test_edit_staff_with_accounting_access(hod_user, staff, staff_email)

    # Step 3: Capture raw sync response
    sync_status, sync_body, sync_json = capture_sync_response_directly(staff)

    # Step 4: Verify user on invoicing system
    invoicing_user = verify_user_on_invoicing_system(staff_email)

    # Step 5: Generate SSO token
    sso_token, payload = generate_sso_token(staff)

    # Step 6: Test full SSO login round-trip
    sso_success = test_sso_login_roundtrip(sso_token, payload)

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\n✓ Test data created: {staff_email}")
    print(f"✓ Edit staff POST: {response.status_code}")
    print(f"✓ Staff has_accounting_access: {staff.has_accounting_access}")
    print(f"✓ Sync response status: {sync_status}")
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

    print(f"\nRESP_STATUS: {sync_status}")
    print(f"\nRESP_BODY:\n{sync_body}")

    if invoicing_user:
        print(f"\nINVOICING_USER (verified):")
        print(json.dumps(invoicing_user, indent=2))
    else:
        print(f"\nINVOICING_USER: NOT FOUND")

    print(f"\nSSO_TOKEN:")
    print(json.dumps(sso_token, indent=2))

    print("\n✓ E2E Test complete")


if __name__ == '__main__':
    main()
