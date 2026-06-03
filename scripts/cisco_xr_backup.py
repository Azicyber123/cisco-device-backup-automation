from netmiko import ConnectHandler
from datetime import datetime, timedelta
import keyring
import smtplib
import requests
import logging
import os
import yaml
from pathlib import Path

# ─────────────────────────────────────────
# 🔧 CONFIGURATION
# ─────────────────────────────────────────

BASE_DIR = Path(__file__).parent.parent
BACKUP_DIR = BASE_DIR / "backups" / "xr"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "cisco_xr_backup.log"
KEEP_DAYS = 30

# Load devices
try:
    with open(BASE_DIR / "config" / "devices.yaml", "r") as f:
        config = yaml.safe_load(f)
        SWITCHES = [d for d in config.get("devices", []) if d.get("type") == "xr"]
except Exception as e:
    raise Exception(f"❌ Failed to load devices.yaml: {e}")

KEYRING_SERVICE = "cisco_backup"

# Credentials from keyring
USERNAME       = keyring.get_password(KEYRING_SERVICE, "device_username")
PASSWORD       = keyring.get_password(KEYRING_SERVICE, "device_password")

EMAIL_FROM     = keyring.get_password(KEYRING_SERVICE, "email_user")
EMAIL_PASSWORD = keyring.get_password(KEYRING_SERVICE, "email_password")

# ================== NOTIFICATION SETTINGS (CHANGE THESE) ==================
EMAIL_TO = [
    "you@company.com", 
    "team@company.com"
]  

TEAMS_WEBHOOK = "https://outlook.office.com/webhook/YOUR_WEBHOOK_URL_HERE"  

SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587

# Validation
if not USERNAME or not PASSWORD:
    raise Exception("❌ Device credentials not found! Run setup_credentials.py first.")
if not EMAIL_FROM or not EMAIL_PASSWORD:
    raise Exception("❌ Email credentials not found! Run setup_credentials.py first.")
if not SWITCHES:
    raise Exception("❌ No IOS-XR devices found in devices.yaml")

# Logging
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
log = logging.getLogger()

def send_email(subject, body):
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
            message = f"Subject: {subject}\nFrom: {EMAIL_FROM}\nTo: {', '.join(EMAIL_TO)}\n\n{body}"
            smtp.sendmail(EMAIL_FROM, EMAIL_TO, message)
        log.info("📧 Email alert sent successfully.")
    except Exception as e:
        log.error(f"📧 Failed to send email: {e}")

def send_teams(title, message, color="0076D7"):
    payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": color,
        "summary": title,
        "sections": [{
            "activityTitle": f"**{title}**",
            "activityText": message,
            "markdown": True
        }]
    }
    try:
        r = requests.post(TEAMS_WEBHOOK, json=payload, timeout=10)
        if r.status_code == 200:
            log.info("🔔 Teams notification sent successfully.")
        else:
            log.error(f"🔔 Teams notification failed: {r.status_code}")
    except Exception as e:
        log.error(f"🔔 Teams notification error: {e}")

def cleanup_old_backups():
    cutoff = datetime.now() - timedelta(days=KEEP_DAYS)
    deleted = 0
    for file in os.listdir(BACKUP_DIR):
        filepath = os.path.join(BACKUP_DIR, file)
        if file.endswith(".conf") and os.path.isfile(filepath):
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_time < cutoff:
                os.remove(filepath)
                log.info(f"🗑️  Deleted old backup: {file}")
                deleted += 1
    log.info(f"🗂️  Cleanup completed — {deleted} old backup(s) removed.")

# ─────────────────────────────────────────
# BACKUP LOGIC
# ─────────────────────────────────────────

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
summary = []

def backup_switch(host, name):
    device = {
        'device_type': 'cisco_xr',
        'host': host,
        'username': USERNAME,
        'password': PASSWORD,
        'port': 22,
        'timeout': 30,
    }
    filename = BACKUP_DIR / f"{name}_{timestamp}.conf"

    try:
        log.info(f"Connecting to {name} ({host})...")
        conn = ConnectHandler(**device)
        config = conn.send_command("show running-config formal", read_timeout=60)
        conn.disconnect()

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"! Backup of {name} ({host})\n")
            f.write(f"! Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(config)

        log.info(f"✅ SUCCESS — {name} saved to {filename}")
        summary.append({"name": name, "host": host, "status": "✅ Success"})

    except Exception as e:
        log.error(f"❌ FAILED — {name} ({host}): {e}")
        summary.append({"name": name, "host": host, "status": f"❌ Failed: {e}"})

        send_email(
            subject=f"❌ Backup FAILED: {name} ({host})",
            body=f"Device : {name}\nIP     : {host}\nError  : {e}\nTime   : {datetime.now()}"
        )
        send_teams(
            title=f"❌ Backup Failed: {name}",
            message=f"**Device:** {name}  \n**IP:** {host}  \n**Error:** {e}",
            color="FF0000"
        )

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

log.info("=" * 60)
log.info("   Cisco IOS-XR Backup Tool — Started")
log.info("=" * 60)

for sw in SWITCHES:
    backup_switch(sw["host"], sw["name"])

cleanup_old_backups()

success = [s for s in summary if "Success" in s["status"]]
failed = [s for s in summary if "Failed" in s["status"]]

log.info("=" * 60)
log.info("  BACKUP SUMMARY")
log.info("=" * 60)
for s in summary:
    log.info(f"  {s['status']:15} {s['name']} ({s['host']})")
log.info(f"  Total Devices : {len(summary)} | ✅ Success: {len(success)} | ❌ Failed: {len(failed)}")

teams_rows = "\n".join([f"- {s['status']} **{s['name']}** ({s['host']})" for s in summary])
send_teams(
    title="📦 Cisco IOS-XR Backup Summary",
    message=f"**Total:** {len(summary)}  |  ✅ **Success:** {len(success)}  |  ❌ **Failed:** {len(failed)}\n\n{teams_rows}",
    color="00C176" if not failed else "FF0000"
)

if failed:
    failed_list = "\n".join([f"  - {s['name']} ({s['host']})" for s in failed])
    send_email(
        subject=f"⚠️ Cisco IOS-XR Backup — {len(failed)} Failure(s)",
        body=f"Backup completed with errors.\n\nFailed Devices:\n{failed_list}"
    )

log.info("✅ Cisco IOS-XR Backup Process Completed.")