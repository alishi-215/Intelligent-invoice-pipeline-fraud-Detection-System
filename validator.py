from database import find_invoice


def check_missing_fields(data):
    required = ["VendorName", "InvoiceId", "InvoiceDate", "InvoiceTotal"]
    missing = []
    for field in required:
        if not data.get(field, {}).get("value"):
            missing.append(field)
    if missing:
        return False, f"Missing fields: {missing}"
    return True, "OK"

def check_math(data):
    items = data.get("Items", [])
    if not items:
        return True, "OK"
    
    calculated = 0
    for item in items:
        amount = item.get("amount", "0")
        amount = float(amount.replace(",", "").replace("Rs. ", ""))
        calculated += amount
    
    total = data.get("InvoiceTotal", {}).get("value", "0")
    total = float(total.replace(",", "").replace("Rs. ", ""))
    
    difference = abs(calculated - total)
    if difference > 1:
        return False, f"Math error! Items sum={calculated}, Total={total}, Difference={difference}"
    return True, "OK"

def check_confidence(data):
    THRESHOLD = 0.80
    low = []
    for field in ["VendorName", "InvoiceId", "InvoiceDate", "InvoiceTotal"]:
        conf = data.get(field, {}).get("confidence")
        if conf is not None:
            if field == "VendorName" and conf < 0.40:
                low.append(f"{field}={conf}")
            elif field != "VendorName" and conf < THRESHOLD:
                low.append(f"{field}={conf}")
    if low:
        return False, f"Low confidence: {low}"
    return True, "OK"

def check_duplicate(data):
    vendor = data.get("VendorName", {}).get("value", "")
    invoice_id = data.get("InvoiceId", {}).get("value", "")
    
    result = find_invoice(vendor, invoice_id)
    if result:
        return False, f"Duplicate! Already processed: {invoice_id}"
    return True, "OK"

def validate_invoice(data):
    checks = [
        check_missing_fields(data),
        check_math(data),
        check_confidence(data),
        check_duplicate(data),
    ]
    
    reasons = []
    for ok, reason in checks:
        if not ok:
            reasons.append(reason)
    
    if reasons:
        return "FLAGGED", " | ".join(reasons)
    return "CLEAN", "All checks passed"


if __name__ == "__main__":
    print("Validator ready!")