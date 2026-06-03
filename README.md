# Cisco Device Backup Automation (IOS / IOS-XE / NX-OS / IOS-XR)

Automated daily configuration backup solution for Cisco network devices using Netmiko. Supports multiple platforms with secure credential storage, Microsoft Teams & Email notifications.

## Features

- Supports **Cisco IOS**, **IOS-XE**, **NX-OS**, and **IOS-XR**
- Secure credential storage using **`keyring`**
- Separate backup scripts per platform
- Microsoft Teams + Email alerts (Success / Failure)
- Automatic cleanup of old backups
- Detailed logging

## Installation

```bash
git clone https://github.com/Azicyber123/cisco-device-backup-automation.git
cd cisco-device-backup-automation
pip install -r requirements.txt

##First-Time Setup

1. Setup Credentials (Run Once)

Bashpython setup_credentials.py
This securely stores:

Device username & password
Sender email & password

2. Configure Devices

Edit config/devices.yaml and add your devices with the correct type:
YAMLdevices:
  - host: "192.168.2.1"
    name: "core-sw01"
    type: "ios"        # or "iosxe"

  - host: "192.168.4.1"
    name: "nexus-sw01"
    type: "nxos"

  - host: "192.168.3.1"
    name: "xr-router01"
    type: "xr"

3. Update Notification Settings

Open any of the backup scripts (or scripts/main.py) and update:
PythonEMAIL_TO = ["your.email@company.com", "networkteam@company.com"]

TEAMS_WEBHOOK = "https://outlook.office.com/webhook/YOUR_ACTUAL_WEBHOOK_URL"
Usage

##Run individual platform backup:

Bashpython scripts/cisco_ios_backup.py
python scripts/cisco_nxos_backup.py
python scripts/cisco_xr_backup.py

##Run all platforms at once (Recommended):

Bashpython scripts/main.py

##Scheduling (Daily)

Linux (crontab):

Bash0 2 * * * /usr/bin/python3 /path/to/cisco-device-backup-automation/scripts/main.py >> /path/to/logs/cron.log 2>&1

Windows: Use Task Scheduler.

##Project Structure

textcisco-device-backup-automation/
├── backups/
│   ├── ios/
│   ├── nxos/
│   └── xr/
├── logs/
├── config/
│   └── devices.yaml
├── scripts/
│   ├── cisco_ios_backup.py
│   ├── cisco_nxos_backup.py
│   ├── cisco_xr_backup.py
│   └── main.py
├── setup_credentials.py
├── requirements.txt
└── README.md

##Security

All passwords are stored using Python keyring (system secure storage)
Never commit passwords or sensitive data

##License
MIT License