import os
import subprocess
import sys
import signal
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time
import logging

# Gracefully shutdown function
def shutdown_gracefully(signal, frame):
    logger.info("Gracefully shutting down...")
    scheduler.shutdown()  # Shut down the scheduler
    sys.exit(0)  # Exit the script

# Register
signal.signal(signal.SIGTERM, shutdown_gracefully)

# Configure logger
logging.getLogger('apscheduler').setLevel(logging.ERROR)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)-8s %(message)s', "%m/%d/%Y %H:%M")
ch.setFormatter(formatter)
logger.addHandler(ch)

# Define the path to the scripts folder and main.py script
scripts_folder = '/app'
main_script = os.path.join(scripts_folder, 'main.py')

# Define the path to the configuration folder and settings file
config_folder = '/config'
settings_file_path = os.path.join(config_folder, 'overlay-settings.yml')

# Function to run the main.py script
def run_main():
    try:
        # Run the main.py script using subprocess
        subprocess.run([sys.executable, main_script], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running {main_script}: {e}")

if __name__ == "__main__":
    # Check for the RUN_NOW environment variable
    run_now = os.getenv("RUN_NOW", "false").strip().lower() == "true"

    # Check if the settings file exists
    settings_missing = not os.path.exists(settings_file_path)

    if settings_missing:
        run_main()
        logger.info("The scheduler will continue with the configured schedule.")
    elif run_now:
        logger.info("RUN_NOW is set to true. Running the script immediately...")
        run_main()
        logger.info("Reverting to scheduled runs.")

    # Now, get the schedule from the environment variable or use a default
    schedule = os.getenv("SCHEDULE", "07:00").strip()  # Default to 07:00 if not provided

    # Ensure the time format is correct by removing extra spaces and splitting
    time_parts = schedule.split(":")
    if len(time_parts) != 2:
        logger.warning("Invalid schedule format. Using default time: 07:00.")
        logger.warning("Fix the 'SCHEDULE' environment setting in Docker. HH:MM required.")
        schedule = "07:00"
        time_parts = schedule.split(":")

    hour, minute = time_parts
    hour = hour.zfill(2)  # Pad single-digit hour with leading zero
    logger.info(f"Scheduling the job to run at: {hour}:{minute}.")

    # Set up the scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_main,
        CronTrigger(hour=hour, minute=minute),
        id="run_main_job",
        replace_existing=True,
    )

    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler is running.")

    # Keep the script running to allow the scheduler to trigger main.py
    try:
        while True:
            time.sleep(60)  # Sleep to reduce CPU usage
            logger.info(f"Checking schedule...Next run at {hour}:{minute}.")
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
