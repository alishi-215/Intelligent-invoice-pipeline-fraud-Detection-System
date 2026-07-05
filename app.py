from flask import Flask, render_template, request, jsonify
import os
import csv
import io
import requests as req

from pipeline import process_invoice

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Google Sheets public CSV URLs
SHEET_ID = "1wvfHY8slE59_5tgo8O7r_saD2gWOvVXz0Noa7kKuVFQ"
PROCESSED_GID = "1386269789"
QUEUE_GID = "1366836044"


def fetch_sheet(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    r = req.get(url)
    if r.status_code != 200:
        return []

    # csv.reader commas inside quotes properly handle karta hai
    reader = csv.reader(io.StringIO(r.text))
    lines = list(reader)

    if len(lines) < 2:
        return []

    headers = [h.strip() for h in lines[0]]
    rows = []
    for line in lines[1:]:
        if any(v.strip() for v in line):  # empty rows skip karo
            row = dict(zip(headers, [v.strip() for v in line]))
            rows.append(row)
    return rows


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    if "invoice" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["invoice"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    status, reason = process_invoice(filepath)
    return jsonify({
        "status": status,
        "reason": reason,
        "filename": file.filename
    })


@app.route("/sheets/processed")
def sheets_processed():
    try:
        rows = fetch_sheet(PROCESSED_GID)
        return jsonify({"rows": rows})
    except Exception as e:
        return jsonify({"rows": [], "error": str(e)})


@app.route("/sheets/queue")
def sheets_queue():
    try:
        rows = fetch_sheet(QUEUE_GID)
        return jsonify({"rows": rows})
    except Exception as e:
        return jsonify({"rows": [], "error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)