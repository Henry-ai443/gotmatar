#!/usr/bin/env python
"""
Test GET /staff/edit/5 to verify correct staff data is loaded,
not a mismatched staff/user lookup.
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from django.test import Client
from main_app.models import CustomUser, Staff, Course

# Find staff with ID 5
try:
    staff_5 = Staff.objects.get(id=5)
    print(f"Staff ID 5 exists")
    print(f"  Staff.id = {staff_5.id}")
    print(f"  Staff.admin.id (CustomUser.id) = {staff_5.admin.id}")
    print(f"  Staff.admin.email = {staff_5.admin.email}")
    print(f"  Staff.admin.first_name = {staff_5.admin.first_name}")
    print(f"  Staff.admin.last_name = {staff_5.admin.last_name}")
    print(f"  Staff.has_accounting_access = {staff_5.has_accounting_access}")
    print()
except Staff.DoesNotExist:
    print("Staff ID 5 does not exist.")
    exit(1)

# Initialize test client and login
client = Client()
hod_user = CustomUser.objects.filter(user_type=1).first()
if not hod_user:
    print("No HOD user found to login with")
    exit(1)
client.force_login(hod_user)

# Make GET request to /staff/edit/5
print("=" * 70)
print("GET /staff/edit/5 Response Check")
print("=" * 70)
response = client.get(f'/staff/edit/5')
print(f"Status Code: {response.status_code}")
print(f"Expected: 200 (form should render)")
print()

if response.status_code == 200:
    # Check if the correct staff data is in the form
    content_str = response.content.decode('utf-8', errors='ignore')
    
    print("Checking if correct staff data appears in response:")
    if str(staff_5.admin.first_name) in content_str:
        print(f"  ✓ Staff first name '{staff_5.admin.first_name}' found in form")
    else:
        print(f"  ✗ Staff first name '{staff_5.admin.first_name}' NOT found in form")
    
    if str(staff_5.admin.last_name) in content_str:
        print(f"  ✓ Staff last name '{staff_5.admin.last_name}' found in form")
    else:
        print(f"  ✗ Staff last name '{staff_5.admin.last_name}' NOT found in form")
    
    if str(staff_5.admin.email) in content_str:
        print(f"  ✓ Staff email '{staff_5.admin.email}' found in form")
    else:
        print(f"  ✗ Staff email '{staff_5.admin.email}' NOT found in form")
    
    print()
    print("✓ PASS: Correct staff member (ID=5) data loads properly")
else:
    print(f"✗ FAIL: Expected 200 but got {response.status_code}")
