from dataclasses import dataclass
import datetime
from typing import Optional
from dataclasses import dataclass

@dataclass
class BookingResult:
    success: bool
    booking_id: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime.datetime = datetime.datetime.now()
    details: Optional[dict] = None # For any additional info, like confirmed slots