# Yorba Linda Library Study Room Booking System

An automated booking system for Yorba Linda Library study rooms using Python and Selenium WebDriver.

## Features

- **Automated Booking**: Book study rooms for specific dates and times
- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Robust Error Handling**: Comprehensive error handling and logging
- **Secure Credentials**: Environment-based credential management
- **Flexible Configuration**: Configurable settings via environment variables
- **Comprehensive Logging**: JSON and text format logging with rotation

## Project Structure

```
library_booking/
├── config/
│   ├── .env.example          # Environment variables template
│   ├── __init__.py
│   └── settings.py           # Configuration settings
├── core/
│   ├── __init__.py
│   ├── booking_engine.py     # Main booking logic
│   ├── date_utils.py         # Date manipulation utilities
│   └── web_driver.py         # Selenium WebDriver service
├── models/
│   ├── __init__.py
│   ├── booking_request.py    # Booking request data model
│   └── booking_result.py     # Booking result data model
├── services/
│   ├── __init__.py
│   └── authentication_service.py  # Credential management
├── tests/
│   ├── __init__.py
│   ├── integration/          # Integration tests
│   └── unit/                 # Unit tests
├── utils/
│   ├── __init__.py
│   └── logger.py             # Logging configuration
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Setup

### Prerequisites

- Python 3.7+
- Chrome browser
- ChromeDriver (automatically managed by Selenium 4.0+)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd yorba-linda-library-study-room-booking-system
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp config/.env.example config/.env
   ```
   
   Edit `config/.env` and add your library credentials:
   ```env
   LIBRARY_CARD_NUMBER=your_card_number
   LIBRARY_PIN=your_pin
   ```

4. **Create logs directory**:
   ```bash
   mkdir -p logs
   ```

## Usage

### Basic Usage

```bash
python main.py --day "Saturday" --times "10:00am,11:00am" --room "Adult Rm. 1" --party-size 6
```

### Command Line Arguments

- `--day`: Day of the week to book (e.g., "Saturday", "Monday")
- `--times`: Comma-separated list of times (e.g., "10:00am,11:00am,2:00pm")
- `--room`: Room name (e.g., "Adult Rm. 1")
- `--party-size`: Number of people (default: 6)

### Examples

```bash
# Book a single time slot
python main.py --day "Saturday" --times "10:00am" --room "Adult Rm. 1"

# Book multiple time slots
python main.py --day "Sunday" --times "1:00pm,2:00pm,3:00pm" --room "Adult Rm. 2" --party-size 4

# Book for next Monday
python main.py --day "Monday" --times "9:00am" --room "Adult Rm. 1" --party-size 2
```

## Configuration

### Environment Variables

All configuration is managed through environment variables in `config/.env`:

```env
# Required: Library Credentials
LIBRARY_CARD_NUMBER=your_card_number
LIBRARY_PIN=your_pin

# Optional: WebDriver Settings
HEADLESS_MODE=true

# Optional: Logging Settings
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE_PATH=./logs/booking.log
```

### Default Settings

- **Party Size**: 6 people
- **Timeout**: 30 seconds for web operations
- **Headless Mode**: Enabled (browser runs in background)
- **Log Level**: INFO
- **Log Format**: JSON

## Architecture

### Core Components

1. **BookingEngine**: Orchestrates the entire booking process
2. **WebDriverService**: Handles all browser automation
3. **AuthenticationService**: Manages credential loading and validation
4. **Date Utilities**: Handles date calculations and formatting

### Data Models

- **BookingRequest**: Contains all booking parameters
- **BookingResult**: Contains booking outcome and details
- **Credentials**: Secure credential storage

### Error Handling

- Comprehensive exception handling at all levels
- Graceful degradation for partial failures
- Detailed error logging with context
- Safe credential handling (no logging of sensitive data)

## Logging

The system provides comprehensive logging:

- **File Logging**: Rotated log files in `./logs/`
- **Console Logging**: Real-time output
- **JSON Format**: Structured logging for analysis
- **Multiple Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Security

- **Environment Variables**: Credentials stored in `.env` files
- **No Hardcoded Secrets**: All sensitive data externalized
- **Safe Logging**: Credentials never logged
- **Input Validation**: All inputs validated before processing

## Troubleshooting

### Common Issues

1. **ChromeDriver Issues**:
   - Ensure Chrome browser is installed
   - Selenium 4.0+ manages ChromeDriver automatically

2. **Login Failures**:
   - Verify library card number and PIN in `.env`
   - Check if library website is accessible

3. **Booking Failures**:
   - Verify room names and time formats
   - Check if requested times are available
   - Review logs for detailed error information

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=DEBUG
```

Run with visible browser:
```env
HEADLESS_MODE=false
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run unit tests only
python -m pytest tests/unit/

# Run integration tests only
python -m pytest tests/integration/
```

### Code Style

The project follows PEP 8 guidelines. Use tools like `black` and `flake8` for formatting and linting.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

See LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Open an issue with detailed information