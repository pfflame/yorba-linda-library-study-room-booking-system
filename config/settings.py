"""Configuration is independent of Qinglong's current working directory."""
import os
from pathlib import Path
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / "config" / ".env", override=False)
LIBRARY_CARD_NUMBER = os.getenv("LIBRARY_CARD_NUMBER", "").strip()
LIBRARY_PIN = os.getenv("LIBRARY_PIN", "").strip()
DEFAULT_PARTY_SIZE = 2
HEADLESS_MODE = os.getenv("HEADLESS_MODE", "true").lower() == "true"
TIMEOUT_SECONDS = 30
PAGE_LOAD_TIMEOUT_SECONDS = 45
CHROME_BINARY = os.getenv("CHROME_BINARY", "")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "")
STATE_PATH = ROOT / "state" / "bookings.sqlite"
BOOKING_URL = "https://ylpl.libcal.com/r/accessible?lid=13172&gid=27150"
ROOM_CAPACITIES = {"Adult Rm. 1": 4, "Adult Rm. 2": 6, "Adult Rm. 3": 2,
                   "Adult Rm. 4": 2, "Child Rm. 1": 4, "Child Rm. 2": 4, "Teen Rm.": 4}
