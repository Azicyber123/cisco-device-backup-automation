#!/usr/bin/env python3
"""
Cisco Multi-Platform Backup Orchestrator
Runs IOS, NX-OS, and IOS-XR backups sequentially.
"""

from datetime import datetime
import logging
import os
from pathlib import Path

# Base directory setup
BASE_DIR = Path(__file__).parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "cisco_all_backups.log"

# Create log directory
os.makedirs(LOG_DIR, exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

def run_script(script_name):
    """Run a backup script and log the result"""
    script_path = Path(__file__).parent / script_name
    log.info(f"🚀 Starting {script_name}")
    
    if not script_path.exists():
        log.error(f"❌ Script not found: {script_name}")
        return False
    
    try:
        exit_code = os.system(f"python \"{script_path}\"")
        if exit_code == 0:
            log.info(f"✅ Successfully completed {script_name}")
            return True
        else:
            log.warning(f"⚠️  {script_name} completed with warnings (exit code: {exit_code})")
            return False
    except Exception as e:
        log.error(f"❌ Failed to run {script_name}: {e}")
        return False

# ─────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────

if __name__ == "__main__":
    start_time = datetime.now()
    
    log.info("=" * 70)
    log.info("🚀 CISCO MULTI-PLATFORM BACKUP ORCHESTRATOR STARTED")
    log.info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 70)

    scripts = [
        "cisco_ios_backup.py",
        "cisco_nxos_backup.py",
        "cisco_xr_backup.py"
    ]

    success_count = 0
    for script in scripts:
        if run_script(script):
            success_count += 1

    end_time = datetime.now()
    duration = end_time - start_time

    log.info("=" * 70)
    log.info("🎉 ALL BACKUP JOBS COMPLETED")
    log.info(f"Completed Scripts : {success_count}/{len(scripts)}")
    log.info(f"Total Duration    : {duration}")
    log.info(f"End Time          : {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 70)

    print(f"\n✅ All Cisco backups completed! Check logs at: {LOG_FILE}")