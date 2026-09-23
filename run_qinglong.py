"""Run the configured weekly booking and email its outcome."""
import argparse
import json
from datetime import timedelta
from config.settings import ROOT
from core.date_utils import library_now, validate_request
from models.booking_request import BookingRequest
from services.authentication_service import AuthenticationService
from services.email_service import send_email, validate_recipient
from utils.logger import logger


def execute(data, test_notification=False):
    recipient = validate_recipient(data.get('notify_email'))
    if test_notification:
        send_email(recipient, 'Yorba Linda Library - Notification Setup Test',
                   'Email notifications are configured.\n\n'
                   'Schedule: Wednesday at 12:00 AM America/Los_Angeles.\n'
                   'Booking: Saturday, Child Rm. 2, 2:00-4:00 PM, 4 people.\n\n'
                   'This is a notification test only. No reservation was made by this test.')
        logger.info('Setup test notification accepted for %s', recipient)
        return 0
    request = None
    try:
        days = data.get('days_ahead')
        if type(days) is not int or days not in range(4):
            raise ValueError('days_ahead must be an integer from 0 through 3')
        if not isinstance(data.get('times'), list) or not all(isinstance(t, str) for t in data['times']):
            raise ValueError('times must be a list of hourly start times')
        if type(data.get('party_size')) is not int:
            raise ValueError('party_size must be an integer')
        now = library_now()
        target = now.date() + timedelta(days=days)
        if target.weekday() != data.get('target_weekday'):
            raise ValueError('Wrong run day: this task must run three days before the configured booking weekday')
        request = validate_request(BookingRequest(target, data['times'], data['room'], data['party_size']), now)
        request.user_credentials = AuthenticationService().load_credentials()
        from core.booking_engine import BookingEngine
        result = BookingEngine().execute_booking(request)
        code = 0 if result.success else 1
        outcome = 'CONFIRMED' if result.success else 'FAILED / NOT CONFIRMED'
        detail = result.error_message or 'The library displayed a booking confirmation.'
        if result.details.get('submission_uncertain'):
            detail += '\nCheck your library reservations before retrying; submission may have succeeded.'
    except (ValueError, KeyError) as e:
        code, outcome, detail = 2, 'SETUP / SCHEDULE ERROR', str(e)
    except Exception as e:
        code, outcome, detail = 1, 'ERROR', f'Unexpected error ({type(e).__name__}); see Qinglong logs.'
    body = f'Outcome: {outcome}\n'
    if request:
        slots = ', '.join(f'{t}-{int(t[:2])+1:02d}:00' for t in request.time_slots)
        body += (f'Date: {request.target_date}\nRoom: {request.room_name}\n'
                 f'Time: {slots} (America/Los_Angeles)\nPeople: {request.party_size}\n')
    body += f'\n{detail}\n'
    logger.info('%s', body)
    try:
        send_email(recipient, f'Yorba Linda Library - {outcome}', body)
        logger.info('Result notification accepted for %s', recipient)
    except Exception:
        logger.error('Email delivery failed. Booking outcome: %s. Do not rerun a confirmed booking.', outcome)
        return code or 3
    return code


def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-notification', action='store_true', help='Send a setup email without booking')
    args = parser.parse_args(argv)
    try:
        data = json.loads((ROOT / 'config' / 'booking.json').read_text())
        return execute(data, args.test_notification)
    except (OSError, ValueError, TypeError, RuntimeError) as e:
        logger.error('Configuration/notification error (%s)', type(e).__name__)
        return 2

if __name__ == '__main__':
    raise SystemExit(run())
