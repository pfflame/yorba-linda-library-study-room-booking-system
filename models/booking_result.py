from dataclasses import dataclass, field
from datetime import datetime, timezone
@dataclass
class BookingResult:
    success: bool
    error_message: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: dict = field(default_factory=dict)
