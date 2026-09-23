"""Use LibCal's public accessible workflow rather than the virtualized grid."""
from datetime import datetime, timedelta
from urllib.parse import urlparse
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import settings

class WebDriverService:
    def __init__(self, headless=None):
        options = Options()
        if settings.HEADLESS_MODE if headless is None else headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1440,1000")
        options.add_argument("--disable-dev-shm-usage")
        import os
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            options.add_argument("--no-sandbox")
        binary = settings.CHROME_BINARY or shutil.which("chromium")
        if binary:
            options.binary_location = binary
        driver_path = settings.CHROMEDRIVER_PATH or shutil.which("chromedriver")
        self.driver = webdriver.Chrome(service=Service(executable_path=driver_path) if driver_path else Service(), options=options)
        self.driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT_SECONDS)
        self.wait = WebDriverWait(self.driver, settings.TIMEOUT_SECONDS)
    def element(self, selector):
        return self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
    def on_host(self, host):
        parsed = urlparse(self.driver.current_url)
        if parsed.scheme != "https" or parsed.hostname != host:
            raise ValueError("Unexpected site during booking; stopping")
    def availability(self, request):
        self.driver.get(settings.BOOKING_URL)
        self.on_host("ylpl.libcal.com")
        capacity = "Space For 5-8 people" if settings.ROOM_CAPACITIES[request.room_name] > 4 else "Space For 1-4 people"
        Select(self.element("#s-lc-type")).select_by_visible_text(capacity)
        self.wait.until(lambda d: request.room_name in [o.text for o in Select(d.find_element(By.ID, "s-lc-space")).options])
        Select(self.element("#s-lc-space")).select_by_visible_text(request.room_name)
        self.element("#s-lc-go").click()
        date_select = Select(self.element("#date"))
        target = request.target_date.isoformat()
        options = {o.get_attribute("value") for o in date_select.options}
        if target not in options:
            raise ValueError("Requested date is not offered by the library (closed or outside booking window)")
        date_select.select_by_value(target)
        old = self.driver.find_element(By.ID, "s-lc-eq-checkboxes")
        self.element("#s-lc-submit-filters").click()
        # Filters navigate to a new page; wait for the old results to disappear.
        self.wait.until(EC.staleness_of(old))
        self.element("#s-lc-eq-checkboxes")
        if Select(self.element("#date")).first_selected_option.get_attribute("value") != target:
            raise ValueError("The library did not display the requested date")
        slots = {}
        for e in self.driver.find_elements(By.CSS_SELECTOR, "input.booking-checkbox"):
            start = datetime.fromisoformat(e.get_attribute("data-start"))
            end = datetime.fromisoformat(e.get_attribute("data-end"))
            if start.date() == request.target_date and end - start == timedelta(hours=1) and start.minute == 0 and e.is_enabled():
                slots[start.strftime("%H:%M")] = e
        return slots
    def select_slots(self, request, slots):
        missing = set(request.time_slots) - set(slots)
        if missing:
            raise ValueError("Unavailable start time(s): " + ", ".join(sorted(missing)))
        for t in request.time_slots:
            if not slots[t].is_selected():
                slots[t].click()
        self.element("#s-lc-submit-times").click()
    def perform_login(self, credentials):
        self.element("#username")
        self.on_host("ylpl.libapps.com")
        for selector, value in (("#username", credentials.card_number), ("#password", credentials.pin)):
            e = self.element(selector)
            e.clear()
            e.send_keys(value)
        self.element("#s-libapps-login-button").click()
        self.wait.until(lambda d: urlparse(d.current_url).hostname == "ylpl.libcal.com")
        self.on_host("ylpl.libcal.com")
    def fill_booking_form(self, party_size):
        # Live-verified with a confirmed reservation on 2026-09-19.
        # Fail closed if the library changes these controls; never guess an answer.
        self.on_host("ylpl.libcal.com")
        Select(self.element("#q16700")).select_by_visible_text(str(party_size))
        agreement = self.element('input[name="q14992[]"][value="I agree"]')
        if not agreement.is_selected():
            agreement.click()
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Submit my Booking' or normalize-space()='Submit My Booking']")))
    def submit_final_booking(self):
        self.on_host("ylpl.libcal.com")
        self.driver.find_element(By.XPATH, "//button[normalize-space()='Submit my Booking' or normalize-space()='Submit My Booking']").click()
    def check_booking_confirmation(self):
        self.on_host("ylpl.libcal.com")
        el = self.element("h1.s-lc-eq-success-title")
        return bool(el.text.strip())
    def close_driver(self):
        self.driver.quit()
