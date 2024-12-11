import os
import sys
import signal
import logging
from ruamel.yaml import YAML

# Initialize YAML handler
yaml = YAML()

logger = logging.getLogger(__name__)

settings_filename = "overlay-settings.yml"

def shutdown_gracefully(signal, frame):
    logger.info("Shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_gracefully)

# Create default settings yaml file
settings = f"""# Settings for overlay configurations
# This script will create show status overlay ymls that Kometa can use to create new, airing, ended, canceled and returning overlays.  
# These overlays files will create dates on the poster overlays. Setting the script to run daily will update airing/return dates.
# I put the script folder in my Kometa directory and set a cron/task job to run main.py daily prior to kometa running.
# Then I link the yaml files to run in my Kometa config.

# TMDB_Discover settings pull series info to find air dates, etc.  Using the default settings
# limits the "junk" show results that are pulled for a library with mainly US, English language shows.  
# You will get less "No TVDB/TMDB id" errors in Kometa.

# If you have an anime library or a TV show library with lots of non English shows, it may be best
# to NOT use watch_region or with_original_language settings.

libraries:                          # Plex library (SHOWS ONLY) names to create Kometa overlays for.
  TV Shows:                         # Change, add, or remove - Need at least one library.
    is_anime: False                 # Removes TMDB with_original_language:'en' setting for use with Anime libraries or libraries with non English shows.         
    use_watch_region: True          # Removes TMDB watch_region and watch_monetization settings.
  4k TV Shows:
    is_anime: False
    use_watch_region: True
  Anime:
    is_anime: True
    use_watch_region: True

# These settings are used across all status overlays.  
# This creates a consistent overlay across all shows.    
overlay_settings:                  
  days_ahead: 28                            # Days ahead for Returning Next (30 Days Max).
  overlay_save_folder:                      # Kometa overlay folders (leave blank for script folder).
  font:                                     # Kometa must have permissions for this folder. Will default to included font in 'scriptparentfolder/fonts/Inter-Medium.ttf'.
  font_size: 45                             # Font size for overlay text.
  font_color: "#FFFFFF"                     # Font color (kometa requires #RGB, #RGBA, #RRGGBB or #RRGGBBAA, e.g., #FFFFFF).
  horizontal_align: center                  # Horizontal alignment (e.g., center, left, right).
  vertical_align: top                       # Vertical alignment (e.g., top, bottom, etc.).
  horizontal_offset: 0                      # Horizontal offset in pixels.
  vertical_offset: 38                       # Vertical offset in pixels.
  back_width: 475                           # Width of the overlay background.
  back_height: 55                           # Height of the overlay background.
  back_radius: 30                           # Corner radius for rounded backgrounds.
  ignore_blank_results: "true"              # Kometa error processing (true or false).

  # TMDB DISCOVER SETTINGS #                SEE TMDB API FOR MORE DETAILS - THESE SETTINGS ARE IDEAL.
  timezone: America/New_York                # TMDB DISCOVER - UTC timezone standards (default American/New_York).
  with_status: 0                            # TMDB DISCOVER - Returning Series: 0 Planned: 1 In Production: 2 Ended: 3 Canceled: 4 Pilot: 5.
  watch_region: US                          # TMDB DISCOVER - Default US - Must be valid TMDB region code.
  with_original_language: en                # TMDB DISCOVER - Default is en (English) - Must Be valid TMDB language code.
  limit: 500                                # TMDB DISCOVER - API Results limit. Default is 500.
  with_watch_monetization_types: flatrate|free|ads|rent|buy  # TMDB DISCOVER - Options: flaterate, free, ads, rent, buy - can use ,(and) or |(or) as separators.

# You can decide here if you want to use each overlay, change font or backdrop color for individual overlays, or change the text.
use_overlays:
  upcoming_series:
    use: True                               # Use this overlay: True or False.
    back_color: "#FC4E03"                   # Default is "#fc4e03" - Overlay color override for this overlay only.
    text: "U P C O M I N G"                 # Change to desired spacing/text.
    font_color: "#FFFFFF"                   # font color override for this overlay only (Kometa requires #RGB, #RGBA, #RRGGBB or #RRGGBBAA).
    
  new_series:
    use: True
    back_color: "#008001"                   # Default is "#008001".
    text: "N E W  S E R I E S"
    font_color: "#FFFFFF"

  new_airing_next:
    use: True
    back_color: "#008001"                   # Default is "#008001".
    text: "N E W - A I R S"                 # Displays as N E W - A I R S 12/22 on overlays.
    font_color: "#FFFFFF"

  airing_series:
    use: True
    back_color: "#003880"                   # Default is "#003880".
    text: "A I R I N G"
    font_color: "#FFFFFF"

  airing_today:
    use: True
    back_color: "#003880"                   # Default is "#003880".
    text: "A I R S  T O D A Y"
    font_color: "#FFFFFF"

  airing_next:
    use: True
    back_color: "#003880"                   # Default is "#003880".
    text: "A I R I N G "                    # Displays as A I R I N G  12/23 on overlays.
    font_color: "#FFFFFF"

  ended_series:
    use: True
    back_color: "#000000"                   # Default is "#000000.
    text: "E N D E D"
    font_color: "#FFFFFF"

  canceled_series:
    use: True
    back_color: "#CF142B"                   # Default is "#CF1428".
    text: "C A N C E L E D"
    font_color: "#FFFFFF"

  returning_series:
    use: True
    back_color: "#103197"                   # Default is "#103197".
    text: "R E T U R N I N G"
    font_color: "#FFFFFF" 

  returns_next:
    use: True
    back_color: "#103197"                   # Default is "#103197"
    text: "R E T U R N S "                  # Displays as R E T U R N S  12/23 on overlays.
    font_color: "#FFFFFF"     
    """

def create_settings_file(main_directory):

    # Create the settings.yaml file in the same directory as the script.
    settings_file_path = os.path.join(main_directory, settings_filename)
    
    try:
        with open(settings_file_path, 'w') as file:
            file.write(settings)
        logger.info(f"Created settings file at '{settings_file_path}'")
    
    except Exception as e:
        logger.error(f"Error creating settings file: {e}")

def load_settings(main_directory, log_message=True):

    #Load the settings.yaml file. If it doesn't exist, create it.
    settings_file_path = os.path.join(main_directory, settings_filename)

    if not os.path.exists(settings_file_path):
        logger.info(f"Settings file not found at '{settings_file_path}', creating a new one.")
        create_settings_file(main_directory)

    try:
        with open(settings_file_path, 'r') as file:
            if log_message:
                logger.info(f"Loading settings from '{settings_file_path}'")
            return yaml.load(file)
    
    except Exception as e:
        logger.error(f"Error loading settings file: {e}")
        raise  # Re-raise exception after logging
