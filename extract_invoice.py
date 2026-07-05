"""
DAY 1 - Step 1: Extract structured data from ONE invoice
using Azure Document Intelligence (prebuilt-invoice model).

Setup (run once):
    pip install azure-ai-documentintelligence

Then fill in your ENDPOINT and KEY below (from Azure portal ->
your Document Intelligence resource -> "Keys and Endpoint").

Run:
    python extract_invoice.py invoices/invoice_01.pdf
"""

import sys
import json
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

# ====== FILL THESE IN ======
ENDPOINT = ""
KEY = ""
# ===========================


def get_field(fields, name):
    """Safely pull a field's value + confidence from the result."""
    f = fields.get(name)
    if not f:
        return None, None
    value = (
        f.get("valueString")
        or f.get("content")
        or (f.get("valueCurrency") or {}).get("amount")
        or f.get("valueDate")
    )
    return value, f.get("confidence")


# ← NAYA FUNCTION: address hata ke sirf naam rakho
def clean_vendor_name(value):
    if not value:
        return value
    return value.split("\n")[0].strip()


def extract_invoice(pdf_path):
    client = DocumentIntelligenceClient(
        endpoint=ENDPOINT, credential=AzureKeyCredential(KEY)
    )

    with open(pdf_path, "rb") as f:
        poller = client.begin_analyze_document(
            "prebuilt-invoice",
            body=f,
        )
    result = poller.result().as_dict()

    doc = result["documents"][0]
    fields = doc["fields"]

    # --- Pull out the fields we care about ---
    extracted = {}
    for field_name in ["VendorName", "InvoiceId", "InvoiceDate", "DueDate", "InvoiceTotal"]:
        value, confidence = get_field(fields, field_name)

        # ← NAYA: VendorName se address alag karo
        if field_name == "VendorName":
            value = clean_vendor_name(value)

        extracted[field_name] = {"value": value, "confidence": confidence}

    # --- Line items (nested structure) ---
    items = []
    items_field = fields.get("Items", {})
    for item in items_field.get("valueArray", []):
        obj = item.get("valueObject", {})
        items.append({
            "description": (obj.get("Description") or {}).get("content"),
            "quantity": (obj.get("Quantity") or {}).get("content"),
            "unit_price": (obj.get("UnitPrice") or {}).get("content"),
            "amount": (obj.get("Amount") or {}).get("content"),
        })
    extracted["Items"] = items

    return extracted


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_invoice.py <path-to-invoice.pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    print(f"Analyzing {pdf_path} ...\n")

    data = extract_invoice(pdf_path)

    print(json.dumps(data, indent=2, default=str))

    out_path = pdf_path.rsplit(".", 1)[0] + "_extracted.json"
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"\nSaved -> {out_path}")

    print("\n--- Confidence summary ---")
    for name in ["VendorName", "InvoiceId", "InvoiceDate", "InvoiceTotal"]:
        c = data[name]["confidence"]
        flag = "OK" if (c or 0) >= 0.80 else "LOW -> would go to review queue"
        print(f"{name:14} {data[name]['value']!s:30} conf={c}  [{flag}]")