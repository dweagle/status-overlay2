import os
import sys
import signal
import logging
from logging.handlers import RotatingFileHandler
from validate_settings import validate_settings
from settings import create_settings_file
from overlay_generator import create_library_yaml

main_directory = '/config'
log_directory = os.path.join(main_directory, "logs")
settings_file_path = os.path.join(main_directory, "overlay-settings.yml")

# Create font folder
font_src = "/app/font"
font_dest = "/config/font"
# Copy font directory to /config if it doesn't exist
if not os.path.exists(font_dest):
    shutil.copytree(font_src, font_dest)
    
def shutdown_gracefully(signal, frame):
    logger.info("Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_gracefully)

def log_setup():
    #Setup log formatter and handler with rotation
    
    # Define the log directory inside the script directory
    log_path = os.path.join(log_directory, "status.log")  # Log file path
    need_roll = not os.path.isfile(log_path)

    # Ensure the log directory exists
    os.makedirs(log_directory, exist_ok=True)

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set logging level to INFO

    # Create a RotatingFileHandler with a backup count of 5 (status.log, status.log.1, ..., status.log.5)
    log_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=5)
    
    # Define log format
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)-8s %(message)s', "%m/%d/%Y %H:%M")
    log_handler.setFormatter(log_formatter)

    # Add handler to the logger
    logger.addHandler(log_handler)

    # Add a StreamHandler for console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    if need_roll:
        logger.info(f"Log folder created at '{log_directory}'")
    else:
        log_handler.doRollover()

    # Log an initial message
    logger.info(f"Logging started. Logs located at '{log_path}'.")

# Call the log setup function
log_setup()

# Create logger instance
logger = logging.getLogger(__name__)

def main():
    try:
        settings_file_path = os.path.join(main_directory, "overlay-settings.yml")

        # Check if the settings file exists; if not, create it
        if not os.path.exists(settings_file_path):
            logger.info(f"Settings file not found at '{settings_file_path}'.")
            logger.info("Creating default settings file.")
            create_settings_file(main_directory)

            # After creating the settings file, give instructions and exit
            logger.info("Please edit the 'overlay-settings.yml' to your preffered Kometa settings and rerun the script.")
            return  # Exit the script after creating the settings file
        
        # Validate the settings before proceeding
        logger.info("Validating settings file...")
        if not validate_settings(main_directory):
            logger.error("Validation failed. Please fix the issues in the settings file and rerun the script.")
            return  # Exit if validation fails

        # Generate overlay files after validation succeeds
        logger.info("")
        logger.info("Validation successful. Generating overlay files for Kometa.")
        logger.info("")
        create_library_yaml(main_directory)
        logger.info("All library overlay files created. Returning to schedule.")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
