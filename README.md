# Yorba Linda Library Study Room Booking System

A production-ready automation tool for booking Yorba Linda Library study rooms. This system eliminates the manual process of checking availability and booking rooms through the library's website.

## What This Does

This tool automatically:
- Logs into the Yorba Linda Library booking system
- Finds available study room time slots
- Books multiple time slots in sequence
- Provides clear feedback on successful and failed bookings

## Key Features

- **Simple Command Line Interface**: Book rooms with a single command
- **Multiple Time Slots**: Book consecutive hours automatically
- **Secure Credential Storage**: Your library card info stays in environment files
- **Smart Error Handling**: Continues booking other slots even if one fails
- **Clean Output**: Shows only what matters - success/failure summaries

## Quick Start

1. **Install Python 3.7+** and Chrome browser
2. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd yorba-linda-library-study-room-booking-system
   pip install -r requirements.txt
   ```
3. **Add your credentials**:
   ```bash
   cp config/.env.example config/.env
   # Edit config/.env with your library card number and PIN
   ```
4. **Book a room**:
   ```bash
   python main.py --day "Saturday" --times "10:00am,11:00am" --room "Adult Rm. 1"
   ```

## Configuration

Edit `config/.env` with your library information:

```env
# Required: Your library credentials
LIBRARY_CARD_NUMBER=1234567890123
LIBRARY_PIN=1234

# Optional: Run browser in background (recommended)
HEADLESS_MODE=true

# Optional: Logging preferences
LOG_LEVEL=INFO
```

**Note**: ChromeDriver is automatically managed by Selenium 4.0+ - no manual installation needed.

## How to Use

### Basic Command
```bash
python main.py --day "Saturday" --times "10:00am,11:00am" --room "Adult Rm. 1"
```

### Options
- `--day`: Which day to book ("Saturday", "Sunday", "Monday", etc.)
- `--times`: Time slots separated by commas ("10:00am,11:00am,2:00pm")
- `--room`: Room name ("Adult Rm. 1", "Adult Rm. 2", etc.)
- `--party-size`: Number of people (default: 6)

### Common Examples

```bash
# Book 3 hours on Saturday morning
python main.py --day "Saturday" --times "9:00am,10:00am,11:00am" --room "Adult Rm. 1"

# Book Sunday afternoon for 4 people
python main.py --day "Sunday" --times "1:00pm,2:00pm" --room "Adult Rm. 2" --party-size 4

# Book single slot for Monday
python main.py --day "Monday" --times "3:00pm" --room "Adult Rm. 1"
```

### What You'll See
```
✅ Successfully booked 2 time slot(s) for Adult Rm. 1 on 2024-01-15
❌ Failed to book 1 time slot(s)
```

## Troubleshooting

### Common Issues

**"Login failed" or credential errors:**
- Double-check your library card number and PIN in `config/.env`
- Make sure you can log in manually on the library website

**"Room not found" or booking failures:**
- Verify the exact room name (check the library website)
- Ensure the time slots are available
- Try booking fewer time slots at once

**Browser or ChromeDriver issues:**
- Make sure Chrome browser is installed
- Try setting `HEADLESS_MODE=false` to see what's happening

### Debug Mode

To see detailed logs:
```env
LOG_LEVEL=DEBUG
HEADLESS_MODE=false
```

## How It Works

The system uses Selenium WebDriver to automate the library's booking website:

1. **Loads your credentials** from the `.env` file
2. **Opens the library booking page** (in background by default)
3. **Logs in** with your library card number and PIN
4. **Finds and clicks** each requested time slot
5. **Fills out the booking form** with party size
6. **Submits the booking** and confirms success
7. **Reports results** for each time slot attempted

## Project Structure

```
├── config/           # Configuration and credentials
├── core/             # Main booking logic and web automation
├── models/           # Data structures for requests and results
├── services/         # Authentication and credential management
├── utils/            # Logging utilities
├── main.py           # Command-line interface
└── requirements.txt  # Python dependencies
```

## Security & Privacy

- **Your credentials stay local** in the `.env` file on your computer
- **No data is sent anywhere** except to the library's official website
- **Credentials are never logged** or stored in log files
- **Browser runs in background** by default for privacy

## Requirements

- **Python 3.7+**
- **Chrome browser** (ChromeDriver auto-managed)
- **Valid Yorba Linda Library card**

## Dependencies

Only one external dependency:
- `python-dotenv` - for loading environment variables

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test your changes
4. Submit a pull request

## License

See LICENSE file for details.