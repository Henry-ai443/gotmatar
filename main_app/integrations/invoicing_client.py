import logging
from typing import List, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def _headers():
    headers = {}
    api_key = getattr(settings, "INVOICING_API_KEY", None)
    if api_key:
        headers["X-API-KEY"] = api_key
    return headers


def sync_student(student) -> Optional[dict]:
    """Send student data to invoicing system. Returns parsed JSON on success, None on failure."""
    url = f"{getattr(settings, 'INVOICING_BASE_URL', 'http://127.0.0.1:8001')}/api/students/sync/"
    # Map local gender codes to the invoicing system's expected string values.
    # The invoicing system expects 'male'/'female' while this project stores 'M'/'F'.
    GENDER_MAP = {"M": "male", "F": "female"}
    # Ensure required fields are present. The invoicing system currently requires a non-null date_of_birth.
    if not getattr(student, 'date_of_birth', None):
        logger.warning("Skipping sync for %s: missing date_of_birth", getattr(student, 'registration_number', student))
        return {"skipped": True, "reason": "missing date_of_birth"}

    payload = {
        "registration_number": student.registration_number,
        "surname": student.admin.last_name,
        "firstname": student.admin.first_name,
        # translate gender convention between systems
        "gender": GENDER_MAP.get(student.admin.gender, student.admin.gender),
        "current_class": student.course.name if student.course else None,
        "parent_mobile_number": "",
        # invoice system expects ISO date string for date_of_birth
            "date_of_birth": student.date_of_birth.isoformat() if student.date_of_birth else None,
            "date_of_admission": student.admin.created_at.date().isoformat() if getattr(student.admin, 'created_at', None) else None,
    }
    try:
        resp = requests.post(url, json=payload, headers=_headers(), timeout=10)
        if not resp.ok:
            print(f"Response status: {resp.status_code}")
            print(f"Response body: {resp.text}")
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return {"status_code": resp.status_code}
    except requests.exceptions.RequestException as e:
        logger.exception("Failed to sync student %s: %s", student, e)
        return None


def sync_accounting_user(user):
    payload = {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }
    url = f"{getattr(settings, 'INVOICING_BASE_URL', 'http://127.0.0.1:8001')}/api/users/sync/"
    try:
        resp = requests.post(url, json=payload, headers=_headers(), timeout=10)
        if not resp.ok:
            print(f"Response status: {resp.status_code}")
            print(f"Response body: {resp.text}")
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return {"status_code": resp.status_code}
    except requests.exceptions.RequestException as e:
        logger.exception("Failed to sync accounting user %s: %s", user, e)
        return None


def create_invoice(student, session, term, class_for, items: List[dict], balance_from_previous_term: float = 0.0) -> Optional[dict]:
    url = f"{getattr(settings, 'INVOICING_BASE_URL', 'http://127.0.0.1:8001')}/api/invoices/"
    payload = {
        "registration_number": student.registration_number,
        "session": session,
        "term": term,
        "class_for": class_for,
        "items": items,
        "balance_from_previous_term": balance_from_previous_term,
    }
    try:
        resp = requests.post(url, json=payload, headers=_headers(), timeout=10)
        if not resp.ok:
            print(f"Response status: {resp.status_code}")
            print(f"Response body: {resp.text}")
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return {"status_code": resp.status_code}
    except requests.exceptions.RequestException as e:
        logger.exception("Failed to create invoice for %s: %s", student, e)
        return None


def get_invoices_for_student(registration_number: str) -> Optional[list]:
    url = f"{getattr(settings, 'INVOICING_BASE_URL', 'http://127.0.0.1:8001')}/api/invoices/"
    params = {"registration_number": registration_number}
    try:
        resp = requests.get(url, params=params, headers=_headers(), timeout=10)
        if not resp.ok:
            print(f"Response status: {resp.status_code}")
            print(f"Response body: {resp.text}")
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        logger.exception("Failed to fetch invoices for %s: %s", registration_number, e)
        return None


def get_invoice_detail(invoice_id: int) -> Optional[dict]:
    url = f"{getattr(settings, 'INVOICING_BASE_URL', 'http://127.0.0.1:8001')}/api/invoices/{invoice_id}/"
    try:
        resp = requests.get(url, headers=_headers(), timeout=10)
        if not resp.ok:
            print(f"Response status: {resp.status_code}")
            print(f"Response body: {resp.text}")
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        logger.exception("Failed to fetch invoice %s: %s", invoice_id, e)
        return None
