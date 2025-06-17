# Configuration settings will be loaded here
import os
from dotenv import load_dotenv

# Load environment variables from .env file in the config directory
dotenv_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=dotenv_path)


LIBRARY_CARD_NUMBER = os.getenv("LIBRARY_CARD_NUMBER")
LIBRARY_PIN = os.getenv("LIBRARY_PIN")

# Default booking parameters
DEFAULT_PARTY_SIZE = 6
MAX_RETRY_ATTEMPTS = 3
TIMEOUT_SECONDS = 30

# WebDriver settings
HEADLESS_MODE = os.getenv("HEADLESS_MODE", "True").lower() == "true"
IMPLICIT_WAIT_SECONDS = 10
PAGE_LOAD_TIMEOUT_SECONDS = 30

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "json") # 'json' or 'text'
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "./logs/booking.log")