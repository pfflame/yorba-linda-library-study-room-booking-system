"""Prevent concurrent/repeated submissions, including an uncertain response."""
import hashlib
import sqlite3
from config import settings
class BookingState:
    def __init__(self, path=None):
        path = path or settings.STATE_PATH
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.db = sqlite3.connect(path, timeout=10)
        path.chmod(0o600)
        self.db.execute("CREATE TABLE IF NOT EXISTS slots (card TEXT, day TEXT, time TEXT, room TEXT, status TEXT, PRIMARY KEY(card,day,time))")
        self.db.commit()
    def reserve(self, request):
        card = hashlib.sha256(request.user_credentials.card_number.encode()).hexdigest()
        day = request.target_date.isoformat()
        try:
            self.db.execute("BEGIN IMMEDIATE")
            existing = self.db.execute("SELECT time,status FROM slots WHERE card=? AND day=?", (card,day)).fetchall()
            if any(t in request.time_slots for t,_ in existing):
                raise ValueError("This card/date/time has already been submitted. Check My Bookings before retrying; an unconfirmed submission may have succeeded")
            if len(existing) + len(request.time_slots) > 2:
                raise ValueError("Local booking history plus this request would exceed two hours for this card/day")
            self.db.executemany("INSERT INTO slots VALUES (?,?,?,?,?)", [(card,day,t,request.room_name,"unconfirmed") for t in request.time_slots])
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
    def confirm(self, request):
        card = hashlib.sha256(request.user_credentials.card_number.encode()).hexdigest()
        self.db.executemany("UPDATE slots SET status='confirmed' WHERE card=? AND day=? AND time=?", [(card,request.target_date.isoformat(),t) for t in request.time_slots])
        self.db.commit()
    def close(self):
        self.db.close()
