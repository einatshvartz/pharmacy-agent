from typing import Optional, Dict, Any
from app.db import MEDICATIONS, USERS

# function for internal use only
def _find_med_by_name(name: str) -> Optional[Dict[str, Any]]:
    if not name:
        return None
    name_l = name.strip().lower()
    for m in MEDICATIONS:
        if m["name"].lower() == name_l:
            return m
    return None

# function for internal use only
def _find_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    if not user_id:
        return None
    uid = user_id.strip()
    for u in USERS:
        if u.get("user_id") == uid:
            return u
    return None


def get_user(user_id: str) -> Dict[str, Any]:
    """
    Name: get_user
    
    Purpose: Fetch a user record from the internal in-memory DB by user_id (stateless, read-only).
    
    Inputs:
       - user_id: string

    Output:
      - Success: {"found": True, "user": {"user_id": ..., "name": ..., "prescriptions": [...]}}
    
    In case of error:
      - Not found: {"found": False, "error": {"code": "UNKNOWN_USER", "message": "..."}}

    """
    user = _find_user_by_id(user_id)
    if not user:
        return {
            "found": False,
            "error": {"code": "UNKNOWN_USER", "message": f"User '{user_id}' not found"},
        }

    # Return a sanitized copy
    return {
        "found": True,
        "user": {
            "user_id": user.get("user_id"),
            "name": user.get("name"),
            "prescriptions": list(user.get("prescriptions", [])),
        },
    }


def get_medication_by_name(name: str) -> Dict[str, Any]:
    """
    Name: get_medication_by_name

    Purpose: Fetch a medication record from the internal in-memory database by exact medication name

    Inputs:
       - name: string

    Output:
        {"found": True, "medication": {...full medication object...}}
    
    In case of error:
        {"found": False, "error": {"code": "NOT_FOUND", "message": "..."}}
    """
    med = _find_med_by_name(name)
    if not med:
        return {
            "found": False,
            "error": {"code": "NOT_FOUND", "message": f"Medication '{name}' not found"},
        }
    return {"found": True,
            "medication": {
                    "name": med.get("name"),
                    "active_ingredient": med.get("active_ingredient"),
                    "requires_prescription": bool(med.get("requires_prescription")),
                    "dosage_instruction": dict(med.get("dosage_instruction", {})),
                    "usage_instructions": med.get("usage_instructions"),
                    "safety_instructions": med.get("safety_instructions"),
                    "stock": med.get("stock"),
            },
    }

def check_stock(name: str) -> Dict[str, Any]:
    """
    Name: check_stock

    Purpose: Check current stock quantity for a medication by exact name (case-insensitive).

    Input:
      - name: string (name of medication in DB)

    Output:
      - Success: {"found": True, "name": "<canonical name>", "stock": <int>}
    
    In case of error:
      - Not found: {"found": False, "error": {"code": "NOT_FOUND", "message": "..."}}
    """
    med = _find_med_by_name(name)
    if not med:
        return {
            "found": False,
            "error": {"code": "NOT_FOUND", "message": f"Medication '{name}' not found"},
        }

    return {
        "found": True,
        "name": med.get("name"),
        "stock": int(med.get("stock", 0)),
    }


def check_prescription(user_id: str, name: str) -> Dict[str, Any]:
    """
    Name: check_prescription
    
    Purpose:
      Professional combined check:
      1) Does the medication require a prescription?
      2) Does the user have a prescription for this medication?

    Input:
      - user_id: string
      - name: string (medication name)

    Output (success):
      {
        "ok": True,
        "name": "<canonical medication name>",
        "requires_prescription": bool,
        "user_has_prescription": bool
      }

    In case of error:
      - Unknown user:
        {"ok": False, "error": {"code": "UNKNOWN_USER", "message": "..."}}
      - Medication not found:
        {"ok": False, "error": {"code": "NOT_FOUND", "message": "..."}}
    """
    user = _find_user_by_id(user_id)
    if not user:
        return {
            "ok": False,
            "error": {"code": "UNKNOWN_USER", "message": f"User '{user_id}' not found"},
        }

    med = _find_med_by_name(name)
    if not med:
        return {
            "ok": False,
            "error": {"code": "NOT_FOUND", "message": f"Medication '{name}' not found"},
        }

    canonical_name = med.get("name")
    requires = bool(med.get("requires_prescription"))
    prescriptions = user.get("prescriptions", [])

    # Compare case-insensitively for robustness
    presc_set = {str(x).strip().lower() for x in prescriptions}
    user_has = str(canonical_name).strip().lower() in presc_set

    return {
        "ok": True,
        "name": canonical_name,
        "requires_prescription": requires,
        "user_has_prescription": user_has,
    }

