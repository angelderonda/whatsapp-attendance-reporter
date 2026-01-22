---

# 📘 Automated WhatsApp Attendance Reporter

This project is a Python solution designed to automate attendance notifications. It synchronizes data from **Google Sheets**, evaluates multiple absence types (Unjustified and Justified), and dispatches personalized, formatted messages via **WhatsApp Web** using Playwright.

---

## 1️⃣ Prerequisites

### 1.1 Python Installation

1. Download Python from [python.org](https://www.python.org).
2. **Crucial:** During installation, check the box **"Add Python to PATH"**.
3. Verify the installation:

```bash
python --version
```

*Requires Python 3.8 or higher.*

### 1.2 Browser & Sessions

* The script uses **Chromium** (via Playwright) to manage WhatsApp Web.
* It uses a persistent session; you only need to link your device via QR code once.

---

## 2️⃣ Environment Setup

Setting up a **Virtual Environment** ensures that the project dependencies are isolated and do not conflict with other software on your system.

### 2.1 Create and Activate Virtual Environment

Open your terminal in the project root folder:

**On Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2.2 Install Dependencies

With the environment activated, run:

```bash
pip install -r requirements.txt
playwright install chromium
```

---

## 3️⃣ Google Cloud Configuration

### 3.1 Enable APIs

1. Go to the [Google Cloud Console](https://console.cloud.google.com).
2. Create a new project.
3. Enable **Google Sheets API** and **Google Drive API**.

### 3.2 Credentials

1. Create a **Service Account** and download the **JSON Key**.
2. **Rename** the file to `credentials.json` and place it in the project root.
3. **Share** your Google Sheet with the Service Account email as **Viewer**.

---

## 4️⃣ Configuration

### 4.1 `config/config.json`

Define your automation rules and message templates. A sample is provided in `config/config-sample.json`.

```json
{
  "auth": {
    "scopes": ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"],
    "credentials_file": "credentials.json"
  },
  "spreadsheet": {
    "name": "Attendance_Sheet",
    "sheet_name": "January 2026"
  },
  "data_mapping": {
    "id_column": "Name",
    "positive_value": "Yes",
    "justified_value": "Justified",
    "negative_value": "No"
  },
  "patterns": {
    "date_regex": "(\\d{1,4}[-/]\\d{1,2}[-/]\\d{1,4})|(\\d{1,2}[-/]\\d{1,2})"
  },
  "messages": {
    "header_with_absences": "Hello {nombre}, here is your attendance report:",
    "footer_with_absences": "Please remember to justify your absences.",
    "no_absences": "Hello {nombre}, you had perfect attendance in {mes}!",
    "label_unjustified": "*❌ Unjustified Absences:*",
    "label_justified": "*✅ Justified Absences:*"
  }
}
```

---

## 5️⃣ Project Structure

This project follows a clean architecture to separate code, configuration, and data:

```text
whatsapp-attendance-reporter/
├── src/                        # Source code
│   └── attendance_reporter.py
├── config/                     # Configuration files
│   ├── config.json             # Actual config (Private)
│   └── config-sample.json      # Template for users
├── data/                       # Local data and logs
│   ├── attendance-example.xlsx # Visual reference
│   └── logs.txt                # Auto-generated history
├── .gitignore                  # Prevents uploading sensitive data
├── LICENSE                     # MIT License
├── README.md                   # Documentation
└── requirements.txt            # Python dependencies
```

---

## 6️⃣ Running the Script

Ensure your virtual environment is active and you are in the project root directory, then execute:

```bash
python src/attendance_reporter.py
```

### Execution Flow:

1. **GSHEETS:** Fetches attendance records from the cloud.
2. **BROWSER:** Launches Chromium and opens WhatsApp Web.
3. **WAITING:** Loads existing session or waits for QR scan.
4. **SENDING:** Dispatches personalized reports with bold headers and bullets.
5. **DONE:** Updates `data/logs.txt` and closes session.

---

## 7️⃣ Security & Recommendations

* **Persistence:** Session data is saved in `./user_session/`. Scan once, stay logged in.
* **Normalization:** Matches "Ángel" with "angel" automatically.
* **Privacy:** `credentials.json`, `config.json`, and `user_session/` are ignored by git to protect your data.
---