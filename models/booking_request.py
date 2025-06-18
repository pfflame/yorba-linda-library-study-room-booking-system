from dataclasses import dataclass
import datetime
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Credentials:
    card_number: str
    pin: str

@dataclass
class BookingRequest:
    target_date: datetime.date
    time_slots: List[str]  # e.g. ["10:00am", "2:00pm"]
    room_name: str         # e.g. "Adult Rm. 1"
    party_size: int
    user_credentials: Credentials
    booking_url: str = "https://ylpl.libcal.com/spaces?lid=13172&gid=27150"
    # Optional: if specific slot labels are pre-computed
    slot_labels_to_click: Optional[List[str]] = None