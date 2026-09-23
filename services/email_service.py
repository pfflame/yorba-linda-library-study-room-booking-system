"""Deliver only to the requested recipient through Qinglong's SMTP transport."""
import json
import re
import subprocess
from config.settings import ROOT

def validate_recipient(recipient):
    if not isinstance(recipient, str) or not re.fullmatch(r"[^\s@,;<>]+@[^\s@,;<>]+\.[^\s@,;<>]+", recipient):
        raise ValueError("notify_email must contain one valid email address")
    return recipient

def send_email(recipient, subject, body):
    validate_recipient(recipient)
    result = subprocess.run(
        ['node', str(ROOT / 'services' / 'email_notify.cjs')],
        input=json.dumps({'to': recipient, 'subject': subject, 'body': body}),
        text=True, capture_output=True, timeout=60, check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("SMTP notification was not accepted; booking outcome remains unchanged")
