from config import settings
from models.booking_request import Credentials
class AuthenticationService:
    def load_credentials(self):
        credentials = Credentials(settings.LIBRARY_CARD_NUMBER, settings.LIBRARY_PIN)
        if not self.validate_credentials(credentials):
            raise ValueError("Fill LIBRARY_CARD_NUMBER and LIBRARY_PIN in config/.env or Qinglong environment variables")
        return credentials
    def validate_credentials(self, credentials):
        return credentials is not None and all(
            isinstance(value, str) and value.strip() and not value.upper().startswith(("YOUR_", "REPLACE", "TODO"))
            for value in (credentials.card_number, credentials.pin))
