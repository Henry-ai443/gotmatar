#!/usr/bin/env python
"""
E2E Test: Staff Accounting Sync - Simplified Version
Tests the actual HTTP request to the invoicing system without Django ORM.
"""
import sys
import json
import requests
import hmac
import hashlib
import base64
from datetime import datetime
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

INVOICING_BASE_URL = os.getenv('INVOICING_BASE_URL', 'http://127.0.0.1:8001')
INVOICING_API_KEY = os.getenv('INVOICING_API_KEY', '')
SSO_SHARED_SECRET = os.getenv('SSO_SHARED_SECRET', '')

def _headers():
    headers = {}
    if INVOICING_API_KEY:
        headers["X-API-KEY"] = INVOICING_API_KEY
    return headers


def test_accounting_sync():
    """Test the accounting sync endpoint."""
    print("\n" + "="*80)
    print("TEST 1: ACCOUNTING USER SYNC")
    print("="*80)

    # Test user credentials
    test_email = f"e2e_test_{datetime.now().timestamp()}@college.test"
    
    payload = {
        'email': test_email,
        'first_name': 'John',
        'last_name': 'Accountant',
    }
    
    url = f"{INVOICING_BASE_URL}/api/users/sync/"
    headers = _headers()
    
    print(f"\nRequest:")
    print(f"  URL: POST {url}")
    print(f"  Headers: {json.dumps(headers, indent=4)}")
    print(f"  Body: {json.dumps(payload, indent=4)}")

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"\nResponse:")
        print(f"  Status: {resp.status_code}")
        print(f"  Headers:")
        for k, v in dict(resp.headers).items():
            if k.lower() != 'content-length':
                print(f"    {k}: {v[:100]}")
        print(f"  Body:\n{resp.text}")
        
        # Parse JSON if possible
        try:
            resp_json = resp.json()
            print(f"\n  JSON:")
            print(json.dumps(resp_json, indent=4))
        except:
            pass
        
        # Check success
        if resp.ok:
            print(f"\n✓ SYNC SUCCESS (status {resp.status_code})")
            return resp.status_code, resp.text, test_email
        else:
            print(f"\n✗ SYNC FAILED (status {resp.status_code})")
            return resp.status_code, resp.text, test_email
            
    except requests.exceptions.RequestException as e:
        print(f"\n✗ REQUEST FAILED: {e}")
        return None, str(e), test_email


def verify_user_on_invoicing(email):
    """Query invoicing system to verify user was created."""
    print("\n" + "="*80)
    print("TEST 2: VERIFY USER ON INVOICING SYSTEM")
    print("="*80)

    url = f"{INVOICING_BASE_URL}/api/users/"
    headers = _headers()
    
    print(f"\nRequest:")
    print(f"  URL: GET {url}")
    print(f"  Headers: {json.dumps(headers, indent=4)}")

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        
        print(f"\nResponse:")
        print(f"  Status: {resp.status_code}")
        
        if resp.ok:
            try:
                users = resp.json()
                print(f"  Total users returned: {len(users) if isinstance(users, list) else 'N/A'}")
                
                if isinstance(users, list):
                    for user in users:
                        if user.get('email') == email:
                            print(f"\n✓ USER FOUND!")
                            print(json.dumps(user, indent=4))
                            return True, user
                    
                    print(f"\n✗ USER NOT FOUND - showing last 3 users:")
                    for user in users[-3:]:
                        print(f"  - {user.get('email', 'N/A')}")
                    return False, None
                else:
                    print(f"  Body: {resp.text[:200]}")
                    return False, None
            except json.JSONDecodeError:
                print(f"  Body: {resp.text[:500]}")
                return False, None
        else:
            print(f"  Error: {resp.status_code}")
            print(f"  Body: {resp.text[:200]}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"\n✗ REQUEST FAILED: {e}")
        return False, None


def test_sso_login(email):
    """Test SSO login generation and verification."""
    print("\n" + "="*80)
    print("TEST 3: SSO LOGIN VERIFICATION")
    print("="*80)

    print(f"\nGenerating SSO token for: {email}")
    print(f"Shared secret length: {len(SSO_SHARED_SECRET)}")

    # Create SSO payload
    payload = {
        'email': email,
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
    
    print(f"\nSSO Token:")
    print(json.dumps(token_data, indent=4))
    
    # Try to verify with invoicing system
    url = f"{INVOICING_BASE_URL}/api/sso/verify/"
    headers = _headers()
    
    print(f"\nRequest:")
    print(f"  URL: POST {url}")
    print(f"  Headers: {json.dumps(headers, indent=4)}")
    print(f"  Body: {json.dumps(token_data, indent=4)}")

    try:
        resp = requests.post(url, json=token_data, headers=headers, timeout=10)
        
        print(f"\nResponse:")
        print(f"  Status: {resp.status_code}")
        print(f"  Headers:")
        for k, v in dict(resp.headers).items():
            if k.lower() not in ['content-length', 'date']:
                print(f"    {k}: {v[:100]}")
        
        # Check for auth indicators
        has_cookie = 'set-cookie' in resp.headers
        has_token = 'token' in resp.text.lower()
        
        print(f"  Has session cookie: {has_cookie}")
        print(f"  Has auth token: {has_token}")
        print(f"  Body:\n{resp.text[:300]}")
        
        if resp.ok and (has_cookie or has_token):
            print(f"\n✓ SSO VERIFICATION SUCCESS")
            return True
        else:
            print(f"\n✗ SSO VERIFICATION FAILED")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n✗ REQUEST FAILED: {e}")
        return False


def main():
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "E2E TEST: STAFF ACCOUNTING SYNC".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")

    print(f"\nInvoicing Base URL: {INVOICING_BASE_URL}")
    print(f"API Key: {'***' + INVOICING_API_KEY[-8:] if INVOICING_API_KEY else 'NONE'}")
    
    # Step 1: Sync accounting user
    sync_status, sync_body, test_email = test_accounting_sync()
    
    # Step 2: Verify user on invoicing system
    user_found, user_data = verify_user_on_invoicing(test_email)
    
    # Step 3: Test SSO login
    sso_success = test_sso_login(test_email)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\n✓ Test email: {test_email}")
    print(f"✓ Sync response status: {sync_status}")
    print(f"✓ User found on invoicing system: {user_found}")
    print(f"✓ SSO login successful: {sso_success}")
    
    print("\n" + "="*80)
    print("RAW EVIDENCE")
    print("="*80)
    print(f"\nREQ_PAYLOAD (sync_accounting_user):")
    print(json.dumps({
        'email': test_email,
        'first_name': 'John',
        'last_name': 'Accountant'
    }, indent=2))
    
    print(f"\nRESP_STATUS: {sync_status}")
    print(f"\nRESP_BODY:\n{sync_body}")
    
    if user_data:
        print(f"\nINVOICING_USER (verified):")
        print(json.dumps(user_data, indent=2))
    
    print(f"\nSSO_LOGIN_SUCCESS: {sso_success}")
    
    print("\n✓ E2E Test complete")


if __name__ == '__main__':
    main()
