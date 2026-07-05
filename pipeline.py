import os
import json
import requests
from extract_invoice import extract_invoice
from validator import validate_invoice
from llm_checker import check_near_duplicate
from database import save_invoice, find_invoice, setup_db

WEBHOOK_URL = "https://lishy.app.n8n.cloud/webhook/invoice-pipeline"


def process_invoice(pdf_path):
    print(f"\n Processing: {pdf_path}")
    
    # Step 1: Extract
    print("Step 1: Extracting data...")
    data = extract_invoice(pdf_path)
    
    # Step 2: Validate
    print("Step 2: Validating...")
    status, reason = validate_invoice(data)
    
    # Step 3: LLM check (sirf clean invoices pe)
    if status == "CLEAN":
        print("Step 3: LLM near-duplicate check...")
        vendor = data.get("VendorName", {}).get("value", "")
        amount = data.get("InvoiceTotal", {}).get("value", "")
        invoice_id = data.get("InvoiceId", {}).get("value", "")
        date = data.get("InvoiceDate", {}).get("value", "")
        
        previous = find_invoice(vendor, None)
        ok, llm_reason = check_near_duplicate(
            {"vendor": vendor, "invoice_number": invoice_id, 
             "amount": amount, "date": date},
            previous
        )
        if not ok:
            status = "FLAGGED"
            reason = llm_reason

    # Step 4: Database save
    if status == "CLEAN":
        vendor = data.get("VendorName", {}).get("value", "")
        invoice_id = data.get("InvoiceId", {}).get("value", "")
        invoice_date = data.get("InvoiceDate", {}).get("value", "")
        due_date = data.get("DueDate", {}).get("value", "")
        total = data.get("InvoiceTotal", {}).get("value", "0")
        save_invoice(vendor, invoice_id, invoice_date, due_date, total, "processed")

    # Step 5: n8n ko bhejo
    try:
        vendor = data.get("VendorName", {}).get("value", "")
        invoice_id = data.get("InvoiceId", {}).get("value", "")
        amount = data.get("InvoiceTotal", {}).get("value", "")
        requests.post(WEBHOOK_URL, json={
            "vendor": vendor,
            "invoice_number": invoice_id,
            "amount": amount,
            "status": status,
            "reason": reason
        })
        print(f"Sent to n8n: {status}")
    except Exception as e:
        print(f"n8n error: {e}")

    # Step 6: Result
    print(f"Result: {status} | {reason}")
    return status, reason


if __name__ == "__main__":
    setup_db()
    
    invoices_folder = "E:/Intelligent Invoice Processing pipeline/day1_starter_kit/invoices"
    
    for filename in os.listdir(invoices_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(invoices_folder, filename)
            process_invoice(pdf_path)
            print("-" * 50)