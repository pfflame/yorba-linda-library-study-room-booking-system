import argparse
from datetime import date, timedelta
from config import settings
from core.date_utils import get_next_day_of_week, library_now, validate_request
from models.booking_request import BookingRequest
from services.authentication_service import AuthenticationService
from utils.logger import logger

def main(argv=None):
    parser = argparse.ArgumentParser(description="Yorba Linda study room booking (Pacific time)")
    dates = parser.add_mutually_exclusive_group()
    dates.add_argument("--day", help="Next occurrence of a weekday, including today")
    dates.add_argument("--date", type=date.fromisoformat, help="Exact YYYY-MM-DD")
    dates.add_argument("--days-ahead", type=int, choices=range(4), help="0 through 3 calendar days ahead")
    parser.add_argument("--times", help="One or two 1-hour start times, e.g. 09:00,10:00")
    parser.add_argument("--room", help="Exact room name")
    parser.add_argument("--party-size", type=int, default=settings.DEFAULT_PARTY_SIZE)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Check requested availability; do not log in or submit")
    mode.add_argument("--availability", action="store_true", help="List available start times; no credentials needed")
    mode.add_argument("--list-rooms", action="store_true")
    args = parser.parse_args(argv)
    if args.list_rooms:
        for name, capacity in settings.ROOM_CAPACITIES.items():
            print(f"{name}: capacity {capacity}")
        return 0
    if not args.room or not any((args.day, args.date, args.days_ahead is not None)):
        parser.error("--room and one of --date, --day or --days-ahead are required")
    if not args.availability and not args.times:
        parser.error("--times is required unless using --availability")
    try:
        target = args.date or (get_next_day_of_week(args.day) if args.day else library_now().date() + timedelta(days=args.days_ahead))
        request = BookingRequest(target, args.times.split(",") if args.times else [], args.room, args.party_size)
        if args.availability:
            if not 0 <= (target-library_now().date()).days <= 3 or target.weekday()==6:
                raise ValueError("Choose an open date within 3 days")
            if args.room not in settings.ROOM_CAPACITIES:
                raise ValueError("Unknown room; use --list-rooms")
        else:
            validate_request(request)
        if not (args.dry_run or args.availability):
            request.user_credentials = AuthenticationService().load_credentials()
        from core.booking_engine import BookingEngine
        result = BookingEngine().execute_booking(request, args.dry_run, args.availability)
        if not result.success:
            logger.error("%s", result.error_message)
            return 1
        logger.info("%s: %s on %s %s", result.details["mode"], request.room_name, target, ",".join(request.time_slots))
        return 0
    except ValueError as e:
        logger.error("Configuration/input error: %s", e)
        return 2
if __name__ == "__main__":
    raise SystemExit(main())
