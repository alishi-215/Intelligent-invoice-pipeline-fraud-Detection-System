# 🧾 InvoiceIQ — Intelligent Invoice Processing Pipeline with Fraud Detection

An AI-powered invoice processing pipeline that automatically extracts, validates, detects fraud, and routes invoices to Google Sheets — zero manual effort.

## 🚀 What it Does

- **Extracts** structured data from invoice PDFs using Azure Document Intelligence
- **Validates** every invoice with 4 automated checks
- **Detects fraud** using Azure OpenAI GPT reasoning
- **Routes** clean invoices to Processed Sheet and flagged ones to Review Queue via n8n

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| PDF Extraction | Azure Document Intelligence |
| Fraud Reasoning | Azure OpenAI (GPT) |
| Validation Engine | Python |
| Database | SQLite |
| Workflow Automation | n8n |
| Output | Google Sheets |
| Dashboard | Flask |

## ⚙️ How it Works

1. Upload invoice PDF
2. Azure Document Intelligence extracts fields
3. Validation engine runs 4 checks:
   - Missing fields
   - Math errors
   - Confidence scoring
   - Duplicate detection
4. Azure OpenAI catches near-duplicates
5. n8n routes results to Google Sheets automatically

## 🔧 Setup

```bash
pip install -r requirements.txt
```

Create `.env` file:
```
AZURE_DI_ENDPOINT=your_endpoint
AZURE_DI_KEY=your_key
AZURE_OAI_ENDPOINT=your_oai_endpoint
AZURE_OAI_KEY=your_oai_key
AZURE_OAI_DEPLOYMENT=your_deployment
WEBHOOK_URL=your_n8n_webhook
SHEET_ID=your_sheet_id
```

Run:
```bash
python app.py
```

## 📊 Results

- 80%+ reduction in manual processing time
- Duplicate fraud detection
- Math error detection
- Confidence-based routing
