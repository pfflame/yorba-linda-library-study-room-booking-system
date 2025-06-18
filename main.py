from core.booking_engine import BookingEngine
from core.date_utils import get_next_day_of_week
from models.booking_request import BookingRequest
from services.authentication_service import AuthenticationService
from utils.logger import logger
from config import settings
import argparse

def main():
    parser = argparse.ArgumentParser(description="Yorba Linda Library Study Room Booking Bot")
    parser.add_argument("--day", type=str, required=True, help="Day of the week to book (e.g., Saturday, Monday)")
    parser.add_argument("--times", type=str, required=True, help='Comma-separated list of times (e.g., "10:00am,11:00am")')
    parser.add_argument("--room", type=str, required=True, help='Room name (e.g., "Adult Rm. 1")')
    parser.add_argument("--party-size", type=int, default=settings.DEFAULT_PARTY_SIZE, help="Number of people for the booking")
    
    args = parser.parse_args()

    auth_service = AuthenticationService()
    try:
        credentials = auth_service.load_credentials()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return

    try:
        target_date = get_next_day_of_week(args.day)
        times_list = [t.strip() for t in args.times.split(',')]
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return

    booking_request = BookingRequest(
        target_date=target_date,
        time_slots=times_list,
        room_name=args.room,
        party_size=args.party_size,
        user_credentials=credentials
    )

    engine = BookingEngine()
    results = engine.execute_booking(booking_request)

    # Summary logging only
    successful_bookings = [r for r in results if r.success]
    failed_bookings = [r for r in results if not r.success]
    
    if successful_bookings:
        logger.info(f"✅ Successfully booked {len(successful_bookings)} time slot(s) for {args.room} on {target_date}")
    
    if failed_bookings:
        logger.error(f"❌ Failed to book {len(failed_bookings)} time slot(s)")
    
    if not results:
        logger.error("❌ No booking attempts were made")

if __name__ == "__main__":
    main()