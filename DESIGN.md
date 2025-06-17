# Library Study Room Booking System - Design Document

## Executive Summary

This document outlines the design improvements for the Yorba Linda Library study room booking automation system. The current implementation is a monolithic Python script that uses Selenium to automate web interactions. This design proposes a more robust, maintainable, and scalable architecture.

## Current State Analysis

### Strengths
- **Functional**: Successfully automates the booking process
- **Simple**: Single-file implementation is easy to understand
- **Logging**: Good logging implementation for debugging

### Critical Issues Identified

#### 1. Security Vulnerabilities
- **Hardcoded credentials**: Library card number and PIN are embedded in source code
- **Windows-specific log path**: Hardcoded path breaks cross-platform compatibility
- **No credential encryption**: Sensitive data stored in plain text

#### 2. Architecture Problems
- **Monolithic design**: Single 225-line function violates single responsibility principle
- **Tight coupling**: Web automation logic mixed with business logic
- **No error recovery**: Script fails completely if any step encounters issues
- **Brittle selectors**: XPath selectors will break if UI changes

#### 3. Maintainability Issues
- **No configuration management**: All settings hardcoded
- **Limited extensibility**: Adding new features requires modifying core logic
- **No testing framework**: No unit tests or integration tests
- **Poor separation of concerns**: Date logic, web automation, and booking logic intertwined

## Proposed Architecture

### 1. Modular Design

```
library_booking/
├── config/
│   ├── settings.py
│   └── credentials.env
├── core/
│   ├── booking_engine.py
│   ├── date_utils.py
│   └── web_driver.py
├── models/
│   ├── booking_request.py
│   └── booking_result.py
├── services/
│   ├── authentication_service.py
│   ├── room_selection_service.py
│   └── notification_service.py
├── utils/
│   ├── logger.py
│   └── retry_handler.py
├── tests/
│   ├── unit/
│   └── integration/
├── main.py
└── requirements.txt
```

### 2. Core Components

#### Configuration Management
- **Environment-based settings**: Separate configs for dev/prod
- **Encrypted credential storage**: Use environment variables or secure vaults
- **Flexible logging**: Configurable log levels and destinations

#### Booking Engine (Core Business Logic)
```python
class BookingEngine:
    def __init__(self, config: BookingConfig)
    def create_booking_request(self, day: str, times: List[str], room: str) -> BookingRequest
    def execute_booking(self, request: BookingRequest) -> BookingResult
    def validate_booking_parameters(self, request: BookingRequest) -> bool
```

#### Web Driver Service
```python
class WebDriverService:
    def __init__(self, headless: bool = True)
    def navigate_to_booking_page(self) -> None
    def select_time_slots(self, slots: List[TimeSlot]) -> bool
    def authenticate(self, credentials: Credentials) -> bool
    def submit_booking_form(self, form_data: BookingFormData) -> bool
```

#### Authentication Service
```python
class AuthenticationService:
    def load_credentials(self) -> Credentials
    def validate_credentials(self, credentials: Credentials) -> bool
    def encrypt_credentials(self, credentials: Credentials) -> str
```

### 3. Data Models

#### BookingRequest
```python
@dataclass
class BookingRequest:
    target_date: datetime.date
    time_slots: List[str]
    room_name: str
    party_size: int
    user_credentials: Credentials
```

#### BookingResult
```python
@dataclass
class BookingResult:
    success: bool
    booking_id: Optional[str]
    error_message: Optional[str]
    timestamp: datetime.datetime
```

## Key Improvements

### 1. Security Enhancements
- **Environment variables**: Store credentials in `.env` files
- **Credential encryption**: Encrypt sensitive data at rest
- **Input validation**: Sanitize all user inputs
- **Secure logging**: Never log sensitive information

### 2. Reliability Features
- **Retry mechanism**: Automatic retry with exponential backoff
- **Graceful degradation**: Continue booking available slots if some fail
- **Health checks**: Validate system state before booking attempts
- **Rollback capability**: Cancel partial bookings on failure

### 3. Monitoring & Observability
- **Structured logging**: JSON-formatted logs for better parsing
- **Metrics collection**: Track success rates, response times
- **Alert system**: Notify users of booking failures
- **Audit trail**: Complete history of booking attempts

### 4. Configuration Management
```yaml
# config.yaml
booking:
  default_party_size: 6
  max_retry_attempts: 3
  timeout_seconds: 30
  
webdriver:
  headless: true
  implicit_wait: 10
  page_load_timeout: 30
  
logging:
  level: INFO
  format: json
  file_path: ./logs/booking.log
```

### 5. Error Handling Strategy
- **Custom exceptions**: Specific exception types for different failure modes
- **Circuit breaker pattern**: Prevent cascading failures
- **Fallback mechanisms**: Alternative booking strategies
- **User notifications**: Email/SMS alerts for critical failures