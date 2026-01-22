# 📘 Automated WhatsApp Attendance Reporter

This project is a Python solution designed to automate light attendance notifications. It synchronizes data from **Google Sheets**, evaluates multiple absence types (Unjustified and Justified), and dispatches personalized, formatted messages via **WhatsApp Web** using Playwright.

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

## 3️⃣ Google Cloud Configuration (One-time Setup)

### 3.1 Enable APIs

1. Go to the [Google Cloud Console](https://console.cloud.google.com).
2. Create a new project.
3. Navigate to **APIs & Services > Library** and enable:
* **Google Sheets API**
* **Google Drive API**



### 3.2 Credentials

1. Go to **IAM & Admin > Service Accounts** and create a service account.
2. Click on the account -> **Keys** tab -> **Add Key** -> **Create new key (JSON)**.
3. **Rename** the downloaded file to `credentials.json` and place it in the project root.

### 3.3 Share the Spreadsheet

1. Open your Google Sheet.
2. Click **Share** and add the service account email (e.g., `bot@project.iam.gserviceaccount.com`).
3. Set permission to **Viewer** (or Editor if you plan to write data back later).

---

## 4️⃣ Configuration

### 4.1 `config.json`

Define your automation rules and message templates:

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
  "contacts": {
    "Angel Garcia": ["+34600000000"],
    "Antonio Calvente": ["+34611111111"]
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

## 5️⃣ Key Features

* **Session Persistence:** Browser data is saved in `./user_session/`. Scan the QR code once and stay logged in.
* **Custom Absence Labels:** Define how "Justified" vs "Unjustified" absences appear in the message.
* **Advanced Formatting:** Automatically builds messages with bold headers and bullet points.
* **Name Normalization:** Intelligent matching that ignores accents and casing (e.g., "Música" matches "musica").
* **Dual Logging:** Real-time console status and persistent history in `logs.txt`.

---

## 6️⃣ Running the Script

Ensure your virtual environment is active, then execute:

```bash
python attendance_reporter.py
```

### Execution Flow:

1. **GSHEETS:** Connects and downloads attendance records.
2. **BROWSER:** Launches Chromium and opens WhatsApp Web.
3. **WAITING:** Waits for QR scan (first time) or loads existing session.
4. **SENDING:** Iterates through students, builds custom reports, and sends messages.
5. **DONE:** Closes browser and updates logs.

---

## 7️⃣ Project Structure

```text
├── attendance_reporter.py # Main Python script
├── config.json            # Configuration and message templates
├── credentials.json       # Google Cloud Service Account Key (Private)
├── requirements.txt       # Python dependencies
├── logs.txt               # Execution history
└── user_session/          # Persistent WhatsApp login data
```