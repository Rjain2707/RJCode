import requests
import json
import datetime
import re
import os


#new push

# ---------------- CONFIG ----------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GITHUB_EVENT_NAME = os.getenv("GITHUB_EVENT_NAME")  # 'push' or 'schedule'

KEYWORDS = [
    "bonus",
    "buyback",
    "buy back",
    "split",
    "right issue"
    
    
    
]

API_URL = "https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w"

# --------------- HELPERS ----------------

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def fetch_bse_announcements():
    today = datetime.datetime.now().strftime("%Y%m%d")
    params = {
        "strCat": "-1",
        "strPrevDate": today,
        "strScrip": "",
        "strSearch": "P",
        "strToDate": today,
        "strType": "C"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.bseindia.com/",
        "Origin": "https://www.bseindia.com"
    }

    log("Fetching BSE announcements...")
    response = requests.get(API_URL, headers=headers, params=params)
    if response.text.startswith("<"):
        log("BSE blocked request (HTML returned)")
        raise Exception("BSE blocked request (HTML returned)")

    data = response.json()
    announcements = data.get("Table", [])
    log(f"Fetched {len(announcements)} announcements")
    return announcements

def contains_keyword(text):
    if not text:
        return False
    text_lower = text.lower()
    for k in KEYWORDS:
        if k.lower() in text_lower:
            return True
    return False

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"<.*?>", "", text)
    text = text.replace("&nbsp;", " ")
    return text.strip()

def truncate(text, max_len=800):
    return text if len(text) <= max_len else text[:max_len] + "..."

def escape(text):
    if not text:
        return ""
    return text.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]")

def get_pdf_link(attachment_name):
    if not attachment_name:
        return None
    return f"https://www.bseindia.com/xml-data/corpfiling/AttachLive/{attachment_name}"

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHANNEL_ID:
        log("Telegram token or channel ID not set!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            log("✅ Telegram message sent successfully")
        else:
            log(f"❌ Failed to send telegram message: {r.text}")
    except Exception as e:
        log(f"❌ Telegram send error: {str(e)}")

# --------------- MAIN ----------------

def main():
    log(f"Script started (GITHUB_EVENT_NAME={GITHUB_EVENT_NAME})")

    # Send welcome/start message on every push
    if GITHUB_EVENT_NAME == "push":
        send_telegram("*BSE Alert Bot Started*\nI will monitor announcements and send updates every 30 minutes.")

    announcements = fetch_bse_announcements()
    sent_count = 0

    for ann in announcements:
        subject = ann.get("NEWSSUB", "")
        if not contains_keyword(subject):
            log(f"Skipping announcement (no keyword match): {subject}")
            continue

        details = ann.get("NEWS_DT") or ann.get("NEWSDTL") or ann.get("MOREDETAILS")
        details = clean_text(details)
        pdf = get_pdf_link(ann.get("ATTACHMENTNAME"))

        msg = f"*BSE Announcement*\n"
        msg += f"🏢 *{escape(ann.get('SLONGNAME'))}*\n"
        msg += f"📰 *{escape(subject)}*\n"

        if details:
            msg += f"\n📄 {escape(truncate(details))}"

        msg += f"\n⏰ {ann.get('DT_TM', '')}"

        if pdf:
            msg += f"\n🔗 [View PDF]({pdf})"

        log(f"Sending announcement: {subject}")
        send_telegram(msg)
        sent_count += 1

    if sent_count == 0:
        log("No new announcements matching keywords.")
        if GITHUB_EVENT_NAME == "schedule":
            send_telegram("No new BSE announcements matching your keywords in the last 30 minutes.")

    log(f"Script finished. Total sent: {sent_count}")

if __name__ == "__main__":
    main()
