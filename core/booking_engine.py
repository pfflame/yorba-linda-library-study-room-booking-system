from typing import List
from models.booking_request import BookingRequest, Credentials
from models.booking_result import BookingResult
from core.web_driver import WebDriverService
from core.date_utils import format_dow_label
from services.authentication_service import AuthenticationService
from utils.logger import logger
from config import settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BookingEngine:
    def __init__(self):
        self.auth_service = AuthenticationService()
        logger.info("BookingEngine initialized.")

    def _generate_slot_labels(self, request: BookingRequest) -> List[str]:
        """Generates the aria-labels for clicking time slots."""
        if request.slot_labels_to_click:
            logger.debug(f"Using pre-computed slot labels: {request.slot_labels_to_click}")
            return request.slot_labels_to_click
        
        dow_label = format_dow_label(request.target_date)
        slot_labels = [
            f"{t} {dow_label} - {request.room_name} - Available"
            for t in request.time_slots
        ]
        logger.debug(f"Generated slot labels: {slot_labels}")
        return slot_labels

    def validate_booking_parameters(self, request: BookingRequest) -> bool:
        """Validates the booking request parameters."""
        if not request.target_date:
            logger.error("Target date is missing.")
            return False
        if not request.time_slots:
            logger.error("Time slots are missing.")
            return False
        if not request.room_name:
            logger.error("Room name is missing.")
            return False
        if not (1 <= request.party_size <= 10): # Assuming max 10, adjust as needed
            logger.error(f"Invalid party size: {request.party_size}")
            return False
        if not self.auth_service.validate_credentials(request.user_credentials):
            logger.error("Invalid user credentials.")
            return False
        logger.info("Booking parameters validated successfully.")
        return True

    def execute_booking(self, request: BookingRequest) -> List[BookingResult]:
        logger.info(f"Executing booking for date: {request.target_date}, room: {request.room_name}, times: {request.time_slots}")
        if not self.validate_booking_parameters(request):
            return [BookingResult(success=False, error_message="Invalid booking parameters.")]

        all_slot_labels = self._generate_slot_labels(request)
        if not all_slot_labels:
             return [BookingResult(success=False, error_message="Could not generate slot labels for booking.")]

        results: List[BookingResult] = []

        for slot_label in all_slot_labels:
            logger.info(f"Attempting to book slot: {slot_label}")
            driver_service = None  # Initialize to None for finally block
            try:
                driver_service = WebDriverService(headless=settings.HEADLESS_MODE)
                driver_service.navigate_to_page(request.booking_url)

                WebDriverWait(driver_service.driver, settings.TIMEOUT_SECONDS).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.s-lc-eq-avail"))
                )
                logger.info("Available time tiles have loaded on booking page.")

                if not driver_service.select_time_slot(slot_label):
                    logger.warning(f"Failed to select time slot: {slot_label}")
                    results.append(BookingResult(success=False, error_message=f"Failed to select time slot: {slot_label}", details={"slot": slot_label}))
                    continue # Try next slot

                if not driver_service.submit_times():
                    results.append(BookingResult(success=False, error_message="Failed to submit selected times.", details={"slot": slot_label}))
                    continue

                if not driver_service.perform_login(request.user_credentials):
                    results.append(BookingResult(success=False, error_message="Login failed.", details={"slot": slot_label}))
                    continue

                if not driver_service.fill_booking_form(request.party_size):
                    results.append(BookingResult(success=False, error_message="Failed to fill booking form details.", details={"slot": slot_label}))
                    continue

                if not driver_service.submit_final_booking():
                    results.append(BookingResult(success=False, error_message="Failed to submit final booking.", details={"slot": slot_label}))
                    continue

                if driver_service.check_booking_confirmation():
                    logger.info(f"Booking confirmed successfully for slot: {slot_label}!")
                    results.append(BookingResult(success=True, booking_id=f"CONFIRMED_VIA_UI_{slot_label.replace(' ', '_')}", details={"slot": slot_label}))
                else:
                    logger.warning(f"Booking submitted for slot {slot_label} but confirmation screen not found.")
                    results.append(BookingResult(success=False, error_message="Booking submitted but confirmation not verified.", details={"slot": slot_label}))

            except Exception as e:
                logger.error(f"An unexpected error occurred during booking for slot {slot_label}: {e}", exc_info=True)
                results.append(BookingResult(success=False, error_message=f"Unexpected error for slot {slot_label}: {str(e)}", details={"slot": slot_label}))
            finally:
                if driver_service:
                    driver_service.close_driver()
                logger.info(f"Booking execution finished for slot: {slot_label}.")
        
        logger.info(f"Overall booking execution finished. Results: {results}")
        return results