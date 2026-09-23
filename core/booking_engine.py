from core.date_utils import validate_request
from core.state import BookingState
from core.web_driver import WebDriverService
from models.booking_result import BookingResult
from services.authentication_service import AuthenticationService
from utils.logger import logger

class BookingEngine:
    def execute_booking(self, request, dry_run=False, availability_only=False):
        driver = None
        state = None
        submitted = False
        try:
            if not availability_only:
                validate_request(request)
            if not (dry_run or availability_only) and not AuthenticationService().validate_credentials(request.user_credentials):
                raise ValueError("Library credentials are missing")
            driver = WebDriverService()
            slots = driver.availability(request)
            logger.info("Available 1-hour start times for %s on %s: %s", request.room_name, request.target_date, ", ".join(sorted(slots)) or "none")
            if availability_only:
                return BookingResult(True, details={"available": sorted(slots), "mode": "availability"})
            missing = set(request.time_slots) - set(slots)
            if missing:
                raise ValueError("Unavailable start time(s): " + ", ".join(sorted(missing)))
            if dry_run:
                return BookingResult(True, details={"mode": "dry-run", "times": request.time_slots})
            driver.select_slots(request, slots)
            driver.perform_login(request.user_credentials)
            driver.fill_booking_form(request.party_size)
            # Record before the irreversible click. An ambiguous response is never retried.
            state = BookingState()
            state.reserve(request)
            submitted = True
            driver.submit_final_booking()
            if not driver.check_booking_confirmation():
                raise ValueError("Booking confirmation is missing")
            state.confirm(request)
            return BookingResult(True, details={"mode": "booked", "times": request.time_slots})
        except ValueError as e:
            return BookingResult(False, error_message=str(e), details={"submission_uncertain": submitted})
        except Exception as e:
            # Browser errors may contain page data; do not log their full contents.
            message = "Booking outcome uncertain; check My Bookings before retrying" if submitted else "Browser step failed; check connectivity, credentials, or changed form controls"
            return BookingResult(False, error_message=f"{message} ({type(e).__name__})", details={"submission_uncertain": submitted})
        finally:
            if state:
                state.close()
            if driver:
                try:
                    driver.close_driver()
                except Exception:
                    logger.warning("Browser cleanup failed")
