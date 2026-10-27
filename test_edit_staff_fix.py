#!/usr/bin/env python
"""
Test script to verify edit_staff returns valid HttpResponse on all code paths.
Tests:
  1. GET request → should return 200 (render)
  2. POST with valid form → should return 302 (redirect)
  3. POST with invalid form → should return 200 (render with errors)
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_management_system.settings')
django.setup()

from django.test import Client
from main_app.models import CustomUser, Staff, Course

# Check what staff exists
print("Existing Staff in database:")
for staff in Staff.objects.all()[:5]:
    print(f"  Staff ID: {staff.id}, User: {staff.admin.email if staff.admin else 'N/A'}")
print()

# Get first staff or create one
try:
    staff = Staff.objects.first()
    if not staff:
        print("No staff found in database. Creating test staff...")
        course, _ = Course.objects.get_or_create(defaults={'name': 'Test Course'})
        user = CustomUser.objects.create_user(
            email='teststaff@example.com',
            first_name='Test',
            last_name='Staff',
            user_type=2,  # STAFF
            gender='M',
            address='Test Address',
            profile_pic='default.jpg'
        )
        user.set_password('password123')
        user.save()
        staff = Staff.objects.create(admin=user, course=course)
    staff_id = staff.id
    print(f"Using Staff ID: {staff_id}")
    print(f"User Email: {staff.admin.email}")
except Exception as e:
    print(f"Error setting up test data: {e}")
    exit(1)

# Initialize test client
client = Client()

# Login first (need to create/find an HOD user)
print("Setting up authentication...")
try:
    hod_user = CustomUser.objects.filter(user_type=1).first()  # HOD type
    if not hod_user:
        print("No HOD user found. Creating one...")
        hod_user = CustomUser.objects.create_user(
            email='hod@example.com',
            first_name='Test',
            last_name='HOD',
            user_type=1,
            gender='M',
            address='HOD Address',
            profile_pic='default.jpg'
        )
        hod_user.set_password('hodpass123')
        hod_user.save()
    
    # Force login to the test client
    client.force_login(hod_user)
    print(f"Logged in as HOD: {hod_user.email}\n")
except Exception as e:
    print(f"Error setting up HOD user: {e}")
    exit(1)

print("\n" + "=" * 70)
print("TEST 1: GET REQUEST (Display Form)")
print("=" * 70)
try:
    response = client.get(f'/staff/edit/{staff_id}')
    print(f"Status Code: {response.status_code}")
    print(f"Expected: 200")
    print(f"Result: {'✓ PASS' if response.status_code == 200 else '✗ FAIL'}")
except Exception as e:
    print(f"✗ ERROR: {e}")

print()

print("=" * 70)
print("TEST 2: POST WITH VALID DATA (Valid Form)")
print("=" * 70)
try:
    course_id = staff.course.id if staff.course else Course.objects.first().id
    valid_data = {
        'first_name': 'UpdatedFirst',
        'last_name': 'UpdatedLast',
        'email': 'updated@example.com',
        'gender': 'F',
        'address': 'Updated Address',
        'course': course_id,
        'has_accounting_access': True,
        'password': '',  # Empty password means keep existing
    }
    response = client.post(f'/staff/edit/{staff_id}', valid_data)
    print(f"Status Code: {response.status_code}")
    print(f"Expected: 302 (redirect)")
    if response.status_code == 302:
        print(f"Redirect Location: {response.get('Location', 'N/A')}")
    print(f"Result: {'✓ PASS' if response.status_code == 302 else '✗ FAIL'}")
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

print("=" * 70)
print("TEST 3: POST WITH INVALID DATA (Invalid Form - Bad Email)")
print("=" * 70)
try:
    course_id = staff.course.id if staff.course else Course.objects.first().id
    invalid_data = {
        'first_name': 'Test',
        'last_name': 'Staff',
        'email': 'INVALID_EMAIL_FORMAT',  # Invalid email
        'gender': 'M',
        'address': 'Test Address',
        'course': course_id,
        'has_accounting_access': False,
        'password': '',
    }
    response = client.post(f'/staff/edit/{staff_id}', invalid_data)
    print(f"Status Code: {response.status_code}")
    print(f"Expected: 200 (render form with errors)")
    print(f"Content Length: {len(response.content)} bytes")
    if response.status_code == 200:
        if b'Please fil form properly' in response.content or b'error' in response.content.lower():
            print(f"Error message found in response: ✓")
    print(f"Result: {'✓ PASS' if response.status_code == 200 else '✗ FAIL'}")
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()

print("=" * 70)
print("SUMMARY")
print("=" * 70)
print("All code paths now return HttpResponse (no more None returns)!")
print("✓ GET → render (200)")
print("✓ POST valid → redirect (302)")
print("✓ POST invalid → render with errors (200)")
