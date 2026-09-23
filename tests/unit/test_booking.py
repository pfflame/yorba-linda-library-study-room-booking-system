import unittest
from datetime import date, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from core.date_utils import PACIFIC, parse_time, validate_request, get_next_day_of_week
from core.state import BookingState
from models.booking_request import BookingRequest, Credentials
from models.booking_result import BookingResult
from services.authentication_service import AuthenticationService
from core.booking_engine import BookingEngine
from main import main

class ValidationTests(unittest.TestCase):
    def validate(self, **kwargs):
        fields=dict(target_date=date(2026,9,21),time_slots=['10:00am','11:00am'],room_name='Adult Rm. 1',party_size=2)
        fields.update(kwargs)
        return validate_request(BookingRequest(**fields),datetime(2026,9,19,10,0,tzinfo=PACIFIC))
    def test_time_formats(self):
        for v,w in [('09:00','09:00'),('1:00 pm','13:00'),('12:00am','00:00'),('12:00pm','12:00')]:
            self.assertEqual(parse_time(v),w)
        for v in ('13:00pm','9:30','25:00','9am',''):
            with self.assertRaises(ValueError): parse_time(v)
    def test_normalizes(self):
        self.assertEqual(self.validate().time_slots,['10:00','11:00'])
    def test_window_and_closure(self):
        for v in (date(2026,9,18),date(2026,9,20),date(2026,9,23)):
            with self.assertRaises(ValueError): self.validate(target_date=v)
        self.validate(target_date=date(2026,9,22))
    def test_capacity_duration(self):
        for kw in ({'party_size':5},{'party_size':0},{'time_slots':['09:00','10:00','11:00']},{'time_slots':['09:00','9:00am']},{'room_name':'Unknown'}):
            with self.assertRaises(ValueError): self.validate(**kw)
        self.validate(room_name='Adult Rm. 2',party_size=6)
        for room, size in [('Adult Rm. 2',7),('Adult Rm. 3',3),('Adult Rm. 4',3)]:
            with self.assertRaises(ValueError): self.validate(room_name=room,party_size=size)
    def test_hours_and_past(self):
        for t in ('08:00','20:00'):
            with self.assertRaises(ValueError): self.validate(time_slots=[t])
        for t in ('09:00','10:00','17:00'):
            with self.assertRaises(ValueError): self.validate(target_date=date(2026,9,19),time_slots=[t])
    def test_today(self):
        self.assertEqual(get_next_day_of_week('Saturday',date(2026,9,19)),date(2026,9,19))
    def test_credentials(self):
        for c in (None,Credentials('',''),Credentials('YOUR_CARD_NUMBER_HERE','YOUR_PIN_HERE')):
            self.assertFalse(AuthenticationService().validate_credentials(c))
        self.assertNotIn('secret',repr(Credentials('secret','secret')))
    def test_timestamp(self):
        self.assertIsNot(BookingResult(True).timestamp,BookingResult(True).timestamp)

class StateTests(unittest.TestCase):
    def test_duplicates_daily_limit_and_uncertainty(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'state.sqlite'
            state=BookingState(path)
            req=BookingRequest(date(2026,9,21),['09:00'],'Adult Rm. 1',2,Credentials('card','pin'))
            state.reserve(req)
            state.close()
            state=BookingState(path)
            with self.assertRaises(ValueError): state.reserve(req)
            req.room_name='Adult Rm. 2'
            with self.assertRaises(ValueError): state.reserve(req)
            req.time_slots=['10:00']
            state.reserve(req)
            state.confirm(req)
            req.time_slots=['11:00']
            with self.assertRaises(ValueError): state.reserve(req)
            req.user_credentials=Credentials('other','pin')
            state.reserve(req)
            state.close()

class EngineTests(unittest.TestCase):
    def request(self):
        return BookingRequest(date(2026,9,21),['10:00'],'Adult Rm. 1',2,Credentials('card','pin'))
    @patch('core.booking_engine.validate_request')
    @patch('core.booking_engine.WebDriverService')
    def test_dry_run_never_submits(self, cls, validate):
        b=cls.return_value
        b.availability.return_value={'10:00':object()}
        self.assertTrue(BookingEngine().execute_booking(self.request(),dry_run=True).success)
        b.select_slots.assert_not_called()
        b.perform_login.assert_not_called()
        b.submit_final_booking.assert_not_called()
        b.close_driver.assert_called_once()
    @patch('core.booking_engine.validate_request')
    @patch('core.booking_engine.WebDriverService')
    def test_unavailable_never_logs_in(self, cls, validate):
        cls.return_value.availability.return_value={}
        self.assertFalse(BookingEngine().execute_booking(self.request()).success)
        cls.return_value.perform_login.assert_not_called()
    @patch('core.booking_engine.BookingState')
    @patch('core.booking_engine.validate_request')
    @patch('core.booking_engine.WebDriverService')
    def test_uncertain_not_retried(self, cls, validate, state):
        b=cls.return_value
        b.availability.return_value={'10:00':object()}
        b.submit_final_booking.side_effect=RuntimeError('secret page data')
        result=BookingEngine().execute_booking(self.request())
        self.assertFalse(result.success)
        self.assertTrue(result.details['submission_uncertain'])
        self.assertNotIn('secret',result.error_message)
        state.return_value.reserve.assert_called_once()
        state.return_value.confirm.assert_not_called()
        b.submit_final_booking.assert_called_once()
    @patch('main.validate_request')
    @patch('main.AuthenticationService')
    @patch('core.booking_engine.BookingEngine')
    def test_cli_failure(self, cls, auth, validate):
        cls.return_value.execute_booking.return_value=BookingResult(False,error_message='unavailable')
        self.assertEqual(main(['--date','2026-09-21','--times','10:00','--room','Adult Rm. 1']),1)

if __name__=='__main__': unittest.main()
