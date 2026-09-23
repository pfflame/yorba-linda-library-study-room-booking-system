# Yorba Linda Library Study Room Booking System

Python 3.11+ / Selenium automation for the library's **accessible LibCal booking flow**.
Reviewed and tested against the live booking system on September 19, 2026.
An authorized end-to-end test completed login, filled the booking form, and received
a confirmation for Adult Rm. 1 on September 21, 2026, 12–1 PM Pacific (one person).
Qinglong task #6 is enabled for Wednesdays at midnight Pacific. It requests
Child Rm. 2 for Saturday 2–4 PM for four people and emails the result to
`pfflame@gmail.com`. If form controls change, the script stops instead of guessing.

## Library rules

Official sources: [study room guidelines](https://ylpl.org/studyrooms2/) and
[booking interface](https://ylpl.libcal.com/r/accessible?lid=13172&gid=27150).

- Reservations may be made up to **3 calendar days ahead**.
- At most **2 hours per day**, in one-hour increments beginning on the hour.
- Regular hours: Monday–Thursday 9 AM–8 PM; Friday–Saturday 9 AM–5 PM;
  Sunday closed. Actual date/slot availability is checked for holiday closures.
- All date calculations use **America/Los_Angeles**, including daylight saving time.
- Adult Rm. 1; Child Rm. 1, 2; and Teen Rm. hold up to 4 people.
  Adult Rm. 2 holds up to 6 people; Adult Rm. 3 and 4 hold up to 2.
  The site's broad capacity filters are not the actual per-room occupancy limits.
- Check in with library staff before entering. The library's limits also apply to
  bookings made outside this tool and to everyone in your group.

## Setup

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp config/.env.example config/.env
chmod 600 config/.env
```

Fill **only your own local** `config/.env`:

```dotenv
LIBRARY_CARD_NUMBER=
LIBRARY_PIN=
HEADLESS_MODE=true
CHROME_BINARY=/usr/bin/chromium
CHROMEDRIVER_PATH=/usr/bin/chromedriver
```

The card number is the library login name; the password is called a PIN by the site.
Credential templates are deliberately blank. Qinglong environment variables override this
file. For a desktop install, remove the two browser path settings to let Selenium
find/download a compatible driver. On Debian containers install `chromium` and
`chromium-driver` together so versions match. Do not commit credentials, booking
preferences, or `state/` to Git.

## Commands

```sh
# Room names/capacities, without network or credentials
python main.py --list-rooms

# List availability; never log in or submit
python main.py --days-ahead 3 --room 'Adult Rm. 1' --availability

# Check specific slots; never log in, select checkboxes, or submit
python main.py --days-ahead 3 --room 'Adult Rm. 1' --times '09:00,10:00' --dry-run

# Actual booking (requires your credentials)
python main.py --days-ahead 3 --room 'Adult Rm. 1' --times '09:00,10:00' --party-size 2
```

Choose exactly one of `--date YYYY-MM-DD`, `--day Wednesday`, or `--days-ahead 0..3`.
`--day` includes today; a weekday outside the three-day window is rejected.
Times accept `09:00` or `9:00am`. Each start time represents exactly one hour.
All requested slots must be available before any are submitted.

Exit codes: **0** success (or successful availability/dry-run), **1** unavailable or
browser/booking failure, **2** invalid inputs or missing setup. Qinglong receives a
nonzero exit code on failure. Logs go to stdout for Qinglong to capture; credentials
and raw browser exceptions are not logged. The scheduled runner emails successes
and failures. Exit **3** means booking succeeded but email delivery failed; do not
repeat the booking to resend an email.

## NAS / Qinglong

Host project directory:
`/volume3/Codebase/yorba-linda-library-study-room-booking-system`

Container mount:
`/ql/data/scripts/yorba-linda-library-study-room-booking-system`

The NAS Qinglong Dockerfile installs a matching `chromium-driver` and the pinned
Python dependencies in `/opt/ylpl-venv`. Its Compose file mounts the host project.
Both settings survive container recreation. Python runs with `-E` so Qinglong's injected `PYTHONPATH` cannot override the isolated dependencies. The existing tennis booking mount is
preserved.

The configured task is **Yorba Linda Library - Saturday 2-4 PM - Child Room 2**,
ID **6**, enabled with cron **`0 0 * * 3`** in **America/Los_Angeles**.
The first scheduled run is September 23, 2026 at 12:00 AM Pacific, targeting
September 26, 2026, 2–4 PM. Midnight release is not guaranteed by the published
library rules; unavailable slots produce a failure notification.

`config/booking.json` contains:

```json
{
  "days_ahead": 3,
  "target_weekday": 5,
  "times": ["14:00", "15:00"],
  "room": "Child Rm. 2",
  "party_size": 4,
  "notify_email": "pfflame@gmail.com"
}
```

`target_weekday` uses Monday=0 through Sunday=6. The runner rejects runs on the
wrong day instead of creating a reservation for an unintended date.

Qinglong task command:

```sh
bash /ql/data/scripts/yorba-linda-library-study-room-booking-system/run_qinglong.sh
```

The shell wrapper loads Qinglong's generated environment, then uses the isolated
Python runtime. Email uses Qinglong's existing `SMTP_SERVICE`, `SMTP_EMAIL`,
`SMTP_PASSWORD`, and optional `SMTP_NAME` through its installed Nodemailer.
The recipient is explicitly taken from `notify_email`; global `SMTP_TO` is not used.
Only email is sent, without triggering other Qinglong notification channels.
No SMTP password is copied into this project. Delivery failures never retry the
reservation. SMTP acceptance was verified with a setup-test message on September 19.

To test notification delivery without making a reservation:

```sh
docker exec qinglong bash /ql/data/scripts/yorba-linda-library-study-room-booking-system/run_qinglong.sh --test-notification
```

NAS read-only check:

```sh
docker exec qinglong /opt/ylpl-venv/bin/python -E /ql/data/scripts/yorba-linda-library-study-room-booking-system/main.py --days-ahead 3 --room 'Adult Rm. 1' --availability
```

## Duplicate submission protection

`state/bookings.sqlite` records a hashed card identity, date, start time, room, and
confirmation status immediately before the final booking click. A confirmed or
unconfirmed submission prevents another attempt for that card/date/time, even if
the process crashes or the room changes. SQLite transactions also enforce a local
two-hour-per-card/day limit across concurrent runs. This is not a replacement for
the library's account-wide rules or a record of manual bookings.

If a submission is unconfirmed, **inspect your library bookings before retrying**.
Do not delete the state database to force a retry. Only reconcile the particular
record after verifying whether a reservation exists. No automatic final-submit
retry or automatic cancellation is performed.

## Validation

```sh
python -m unittest discover -s tests -v
```

19 tests cover the Wednesday-to-Saturday schedule, notification-only isolation,
success/failure notifications, mail delivery errors, recipient validation, input validation, Pacific-time booking windows, closed days/capacities,
credential placeholders, per-result timestamps, exit codes, dry-run isolation,
unavailable slots, persistent duplicate protection, and uncertain final submission.
Automated unit tests do not create reservations. In addition, the user-authorized
live test described above verified the authenticated flow and final confirmation.
The test reservation remains active for the user to cancel.
