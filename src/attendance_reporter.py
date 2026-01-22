import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import os
import json
import time
import logging
import unicodedata
import urllib.parse
from playwright.sync_api import sync_playwright

# --- LOGGING SETUP ---

def setup_logger():
    """Configures dual logging to console and logs.txt file."""
    logger = logging.getLogger("WhatsAppReporter")
    logger.setLevel(logging.INFO)

    file_formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
    console_formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S')

    file_handler = logging.FileHandler('data/logs.txt', encoding='utf-8')
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

logger = setup_logger()

def log_event(status, message):
    """Prints aligned status messages to terminal and log file."""
    formatted_msg = f"{status:<10} | {message}"
    logger.info(formatted_msg)

# --- UTILS ---

def normalize_text(text):
    """Strips accents and standardizes text for dictionary keys."""
    if not text: return ""
    text = unicodedata.normalize('NFD', str(text))
    text = "".join([c for c in text if unicodedata.category(c) != 'Mn'])
    return text.lower().strip()

def load_config(config_path="config/config.json"):
    """Loads configuration from JSON file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- DATA SOURCE ---

def fetch_gsheet_data(config):
    """Downloads data from the specified Google Sheet."""
    try:
        log_event("GSHEETS", f"Connecting to: {config['spreadsheet']['name']}")
        creds_path = config["auth"]["credentials_file"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            creds_path, config["auth"]["scopes"]
        )
        client = gspread.authorize(creds)
        spreadsheet = client.open(config["spreadsheet"]["name"])
        worksheet = spreadsheet.worksheet(config["spreadsheet"]["sheet_name"])

        raw_data = worksheet.get_all_values()
        df = pd.DataFrame(raw_data)

        df = df.replace('', pd.NA).dropna(how='all').dropna(axis=1, how='all').fillna('')
        df.columns = [str(c).strip() for c in df.iloc[0]]
        df = df[1:].reset_index(drop=True)

        log_event("SUCCESS", f"Retrieved {len(df)} records.")
        return df
    except Exception as e:
        log_event("ERROR", f"Failed to fetch data: {e}")
        return None

# --- WHATSAPP ENGINE ---

def run_whatsapp_automation(df_raw, config):
    """Main loop for WhatsApp delivery using Playwright."""
    contacts = {normalize_text(k): v for k, v in config["contacts"].items()}
    msg_cfg = config["messages"]
    sheet_name = config["spreadsheet"]["sheet_name"]
    id_col = config["data_mapping"]["id_column"]

    # Mapping values from config
    pos_val = str(config["data_mapping"]["negative_value"]).lower().strip()
    jus_val = str(config["data_mapping"]["justified_value"]).lower().strip()

    date_pattern = config["patterns"]["date_regex"]
    date_cols = [col for col in df_raw.columns if re.search(date_pattern, str(col))]

    log_event("ENGINE", f"Tracking {len(date_cols)} date columns.")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="./user_session",
            headless=False
        )
        page = context.new_page()

        log_event("BROWSER", "Opening WhatsApp Web...")
        page.goto("https://web.whatsapp.com")

        log_event("WAITING", "User authentication required...")
        page.wait_for_selector('div[contenteditable="true"]', timeout=60000)

        for _, row in df_raw.iterrows():
            name = row.get(id_col)
            if not name: continue

            name_norm = normalize_text(name)
            if name_norm not in contacts:
                log_event("SKIPPING", f"No contact for: {name}")
                continue

            # Filtering logic for report categories
            unjustified_absences = [col for col in date_cols if str(row[col]).strip().lower() == pos_val]
            justified_absences = [col for col in date_cols if str(row[col]).strip().lower() == jus_val]

            # Message construction
            if unjustified_absences or justified_absences:
                report_body = ""
                if unjustified_absences:
                    report_body += "*Unjustified Absence:*\n" + "\n".join([f"• {a}" for a in unjustified_absences]) + "\n\n"
                if justified_absences:
                    report_body += "*Justified Absence:*\n" + "\n".join([f"• {a}" for a in justified_absences]) + "\n\n"

                msg = (
                    f"{msg_cfg['header_with_absences'].format(name=name)}\n\n"
                    f"{report_body}"
                    f"{msg_cfg['footer_with_absences']}"
                )
            else:
                msg = msg_cfg['no_absences'].format(name=name, month=sheet_name)

            encoded_msg = urllib.parse.quote(msg)

            for phone in contacts[name_norm]:
                try:
                    clean_phone = re.sub(r'\D', '', str(phone))
                    log_event("SENDING", f"To: {name:<15} | +{clean_phone}")

                    target_url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_msg}"
                    page.goto(target_url)

                    page.wait_for_selector('div[contenteditable="true"]', timeout=30000)
                    time.sleep(2)

                    page.keyboard.press("Enter")
                    log_event("DONE", f"Sent to {name}")

                    time.sleep(4)

                except Exception as e:
                    log_event("FAILURE", f"Phone {phone}: {e}")

        context.close()

# --- MAIN EXECUTION ---

if __name__ == "__main__":
    border = "-" * 65
    print(border)
    print("      WHATSAPP ATTENDANCE REPORTER      ")
    print(border)

    try:
        settings = load_config()
        attendance_df = fetch_gsheet_data(settings)

        if attendance_df is not None:
            run_whatsapp_automation(attendance_df, settings)
            print(border)
            log_event("FINISHED", "Process completed successfully.")
        else:
            log_event("HALTED", "Data retrieval failed.")

    except Exception as e:
        log_event("CRITICAL", f"System failure: {e}")