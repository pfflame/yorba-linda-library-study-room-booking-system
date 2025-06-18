# Web driver service for browser automation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from typing import List

from utils.logger import logger
from config import settings
from models.booking_request import Credentials

class WebDriverService:
    def __init__(self, headless: bool = settings.HEADLESS_MODE):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920,1080") # Often needed for headless
            chrome_options.add_argument("--disable-gpu") # Also common for headless
            chrome_options.add_argument("--no-sandbox") # If running as root/in Docker
            chrome_options.add_argument("--disable-dev-shm-usage") # Overcome limited resource problems

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(settings.IMPLICIT_WAIT_SECONDS)
        self.driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT_SECONDS)
        logger.info(f"WebDriver initialized. Headless: {headless}")

    def navigate_to_page(self, url: str) -> None:
        logger.info(f"Navigating to {url}")
        self.driver.get(url)
        self.driver.maximize_window() # Maximize after navigation

    def select_time_slot(self, slot_label: str) -> bool:
        logger.info(f"Attempting to select time slot: {slot_label}")
        try:
            slot_element = WebDriverWait(self.driver, settings.TIMEOUT_SECONDS).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[@aria-label='{slot_label}']"))
            )
            slot_element.click()
            logger.info(f"Successfully clicked slot: {slot_label}")
            return True
        except (NoSuchElementException, TimeoutException):
            logger.warning(f"Slot NOT found/clickable: {slot_label}. Possibly unavailable.")
            return False

    def submit_times(self) -> bool:
        try:
            submit_times_btn = WebDriverWait(self.driver, settings.TIMEOUT_SECONDS).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit Times')]"))
            )
            submit_times_btn.click()
            logger.info("Submit Times button clicked.")
            return True
        except TimeoutException:
            logger.error("Submit Times button not found or clickable.")
            return False
        except Exception as e:
            logger.error(f"Unexpected error clicking Submit Times button: {e}")
            return False

    def perform_login(self, credentials: Credentials) -> bool:
        try:
            WebDriverWait(self.driver, settings.TIMEOUT_SECONDS).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            logger.info("Login form loaded.")

            cardnum_field = self.driver.find_element(By.ID, "username")
            pin_field = self.driver.find_element(By.ID, "password")

            cardnum_field.clear()
            cardnum_field.send_keys(credentials.card_number)
            pin_field.clear()
            pin_field.send_keys(credentials.pin)

            login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
            login_btn.click()
            logger.info("Login submitted.")
            return True
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"Error during login: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            return False

    def fill_booking_form(self, party_size: int) -> bool:
        try:
            WebDriverWait(self.driver, settings.TIMEOUT_SECONDS).until(
                EC.presence_of_element_located((By.ID, "q16700")) # Number of people dropdown
            )
            logger.info("Booking form details page loaded.")

            people_select_el = self.driver.find_element(By.ID, "q16700")
            select_people = Select(people_select_el)
            select_people.select_by_visible_text(str(party_size))
            logger.info(f"Selected {party_size} people.")

            agree_checkbox = self.driver.find_element(
                By.XPATH, "//input[@type='checkbox' and @name='q14992[]' and @value='I agree']"
            )
            if not agree_checkbox.is_selected():
                agree_checkbox.click()
            logger.info("Checked 'I agree' box.")
            return True
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"Error filling booking form: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error filling booking form: {e}")
            return False

    def submit_final_booking(self) -> bool:
        try:
            submit_booking_btn = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Submit my Booking')]"
            )
            submit_booking_btn.click()
            logger.info("Final booking form submitted.")
            return True
        except NoSuchElementException:
            logger.error("Submit My Booking button not found.")
            return False
        except Exception as e:
            logger.error(f"Unexpected error submitting final booking: {e}")
            return False

    def check_booking_confirmation(self) -> bool:
        try:
            success_h1 = WebDriverWait(self.driver, settings.TIMEOUT_SECONDS).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//h1[contains(@class, 's-lc-eq-success-title')]"
                ))
            )
            actual_text = success_h1.text.strip()
            logger.info(f"Booking succeeded! Confirmation heading: '{actual_text}'")
            return True
        except TimeoutException:
            logger.warning("No booking confirmation found. Booking might have failed or UI changed.")
            return False

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed.")