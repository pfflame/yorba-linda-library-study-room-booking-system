#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
"""

try:
    # Test core imports
    from core.booking_engine import BookingEngine
    from core.web_driver import WebDriverService
    from core.date_utils import day_to_weekday_index, get_next_day_of_week, format_dow_label
    
    # Test model imports
    from models.booking_request import BookingRequest
    from models.booking_result import BookingResult
    
    # Test service imports
    from services.authentication_service import AuthenticationService
    
    # Test config imports
    from config import settings
    
    # Test utils imports
    from utils.logger import logger
    
    print("✅ All imports successful!")
    print("✅ Application is ready to run")
    print("\nTo run the application:")
    print('python main.py --day "Saturday" --times "10:00am" --room "Adult Rm. 1"')
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    exit(1)