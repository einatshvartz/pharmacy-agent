# test_tools.py
from app.tools import get_user, get_medication_by_name, check_stock, check_prescription


def run_get_user_tests() -> None:
    print("=== get_user tests ===")

    print("\n[1] Existing user u001")
    print(get_user("u001"))

    print("\n[2] Existing user with whitespace '  u002  '")
    print(get_user("  u002  "))

    print("\n[3] Unknown user u999")
    print(get_user("u999"))

    print("\n[4] Empty user_id")
    print(get_user(""))


def run_get_medication_by_name_tests() -> None:
    print("\n=== get_medication_by_name tests ===")

    print("\n[1] Existing medication 'Paracetamol'")
    print(get_medication_by_name("Paracetamol"))

    print("\n[2] Existing medication with case/space '  cEtIrIzInE  '")
    print(get_medication_by_name("  cEtIrIzInE  "))

    print("\n[3] Existing medication 'Amoxicillin' (prescription expected True)")
    res = get_medication_by_name("Amoxicillin")
    print(res)
    if res.get("found"):
        print("requires_prescription:", res["medication"].get("requires_prescription"))

    print("\n[4] Not found 'DoesNotExist'")
    print(get_medication_by_name("DoesNotExist"))

    print("\n[5] Empty name")
    print(get_medication_by_name(""))

def run_check_stock_tests() -> None:
    print("\n=== check_stock tests ===")

    print("\n[1] In stock 'Paracetamol' (expect 42)")
    print(check_stock("Paracetamol"))

    print("\n[2] Out of stock 'Cetirizine' (expect 0)")
    print(check_stock("Cetirizine"))

    print("\n[3] Case/space '  iBuPrOfEn  ' (expect 18)")
    print(check_stock("  iBuPrOfEn  "))

    print("\n[4] Not found 'DoesNotExist'")
    print(check_stock("DoesNotExist"))

    print("\n[5] Empty name")
    print(check_stock(""))

def run_check_prescription_tests():
    print("\n=== check_prescription tests ===")

    print("\n[1] Prescription med + user HAS prescription (u001, Amoxicillin) => requires True, user_has True")
    print(check_prescription("u001", "Amoxicillin"))

    print("\n[2] Prescription med + user DOES NOT have prescription (u002, Amoxicillin) => requires True, user_has False")
    print(check_prescription("u002", "Amoxicillin"))

    print("\n[3] Non-prescription med + user no prescription needed (u002, Paracetamol) => requires False, user_has False")
    print(check_prescription("u002", "Paracetamol"))

    print("\n[4] Medication not found (u001, DoesNotExist) => ok False, NOT_FOUND")
    print(check_prescription("u001", "DoesNotExist"))

    print("\n[5] User not found (u999, Paracetamol) => ok False, UNKNOWN_USER")
    print(check_prescription("u999", "Paracetamol"))

    print("\n[6] Case/space robustness (u001, '  aMoXiCiLlIn  ') => requires True, user_has True")
    print(check_prescription("u001", "  aMoXiCiLlIn  "))


if __name__ == "__main__":
    run_get_user_tests()
    run_get_medication_by_name_tests()
    run_check_stock_tests()
    run_check_prescription_tests()
