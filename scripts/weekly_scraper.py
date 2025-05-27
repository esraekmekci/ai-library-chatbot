import schedule
import time
import subprocess
import logging
from datetime import datetime

logging.basicConfig(
    filename="weekly_runner.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

SCRIPT_PATH = "../backend/index_setup.py"

def run_index_setup():
    logging.info("Starting index setup script...")
    try:
        result = subprocess.run(["python", SCRIPT_PATH], capture_output=True, text=True)
        logging.info("Script completed.")
        logging.info("Output:\n" + result.stdout)
        if result.stderr:
            logging.warning("Errors:\n" + result.stderr)
    except Exception as e:
        logging.error(f"Error occurred: {e}")

# every monday at 02:00
schedule.every().monday.at("02:00").do(run_index_setup)

logging.info("Scheduler started. Waiting for Monday 02:00...")

while True:
    schedule.run_pending()
    time.sleep(60)
