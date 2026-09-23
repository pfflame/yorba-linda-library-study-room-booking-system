import unittest
from datetime import datetime
from unittest.mock import patch
from core.date_utils import PACIFIC
from models.booking_result import BookingResult
from services.email_service import validate_recipient, send_email
from run_qinglong import execute

CONFIG = dict(days_ahead=3, target_weekday=5, times=['14:00','15:00'], room='Child Rm. 2', party_size=4, notify_email='pfflame@gmail.com')
class NotificationTests(unittest.TestCase):
    def test_recipient_validation(self):
        for bad in ('x@example.com\nBcc:x@z.com','a@b.com,c@d.com','',None):
            with self.assertRaises(ValueError): validate_recipient(bad)
    @patch('run_qinglong.send_email')
    @patch('core.booking_engine.BookingEngine')
    def test_notification_test_never_books(self,engine,email):
        self.assertEqual(execute(CONFIG,True),0)
        engine.assert_not_called()
        self.assertIn('No reservation',email.call_args.args[2])
    @patch('run_qinglong.send_email')
    @patch('run_qinglong.library_now',return_value=datetime(2026,9,23,0,0,tzinfo=PACIFIC))
    @patch('run_qinglong.AuthenticationService')
    @patch('core.booking_engine.BookingEngine')
    def test_saturday_request_and_success_email(self,engine,auth,now,email):
        engine.return_value.execute_booking.return_value=BookingResult(True)
        self.assertEqual(execute(CONFIG),0)
        request=engine.return_value.execute_booking.call_args.args[0]
        self.assertEqual(str(request.target_date),'2026-09-26')
        self.assertEqual(request.time_slots,['14:00','15:00'])
        self.assertEqual(request.party_size,4)
        self.assertIn('CONFIRMED',email.call_args.args[1])
        email.side_effect=RuntimeError('failed')
        self.assertEqual(execute(CONFIG),3)
    @patch('run_qinglong.send_email')
    @patch('run_qinglong.library_now',return_value=datetime(2026,9,23,0,0,tzinfo=PACIFIC))
    @patch('run_qinglong.AuthenticationService')
    @patch('core.booking_engine.BookingEngine')
    def test_failure_email(self,engine,auth,now,email):
        engine.return_value.execute_booking.return_value=BookingResult(False,error_message='Unavailable start time(s): 14:00')
        self.assertEqual(execute(CONFIG),1)
        self.assertIn('Unavailable',email.call_args.args[2])
    @patch('run_qinglong.send_email')
    @patch('run_qinglong.library_now',return_value=datetime(2026,9,19,0,0,tzinfo=PACIFIC))
    @patch('core.booking_engine.BookingEngine')
    def test_wrong_day_does_not_book(self,engine,now,email):
        self.assertEqual(execute(CONFIG),2)
        engine.assert_not_called()
        email.assert_called_once()
    @patch('services.email_service.subprocess.run')
    def test_mailer_failure_propagates(self,proc):
        proc.return_value.returncode=1
        with self.assertRaises(RuntimeError): send_email('pfflame@gmail.com','test','body')
        self.assertEqual(proc.call_args.kwargs['timeout'],60)

if __name__=='__main__': unittest.main()
