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

    logger.info("Starting library room booking process...")

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

    logger.info(f"Booking request created: Date: {target_date}, Times: {times_list}, Room: {args.room}, Party: {args.party_size}")

    engine = BookingEngine()
    results = engine.execute_booking(booking_request)

    all_successful = True
    for result in results:
        if result.success:
            logger.info(f"Booking successful for slot: {result.details.get('slot', 'N/A')}! Result: {result}")
        else:
            all_successful = False
            logger.error(f"Booking failed for slot: {result.details.get('slot', 'N/A')}. Result: {result}")
    
    if all_successful and results:
        logger.info("All requested bookings were successful.")
    elif not results:
        logger.error("No booking attempts were made or results returned.")
    else:
        logger.warning("One or more booking attempts failed. Please check the logs above.")

if __name__ == "__main__":
    main()