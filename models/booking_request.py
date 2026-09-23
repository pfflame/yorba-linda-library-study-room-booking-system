from dataclasses import dataclass, field
from datetime import date
@dataclass
class Credentials:
    card_number: str = field(repr=False)
    pin: str = field(repr=False)
@dataclass
class BookingRequest:
    target_date: date
    time_slots: list[str]
    room_name: str
    party_size: int = 2
    user_credentials: Credentials | None = field(default=None, repr=False)
