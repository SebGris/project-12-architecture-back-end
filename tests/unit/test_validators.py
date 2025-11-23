"""Unit tests for CLI validators module (security & input validation).

Tests covered:
- validate_email_callback(): Email format validation
- validate_phone_callback(): French phone number validation
- validate_password_callback(): Strong password policy enforcement
- validate_first_name_callback(): First name validation
- validate_last_name_callback(): Last name validation
- validate_location_callback(): Location validation
- validate_attendees_callback(): Positive integer validation
- validate_username_callback(): Username validation
- validate_company_name_callback(): Company name validation
- ID validation callbacks (client, user, event, contract, sales contact)
- Amount validation (positive amounts, payment limits)
- Date validation (event dates, future dates)
- Business logic validators (user department, payment amounts)

Implementation notes:
- Minimal mocks (only for department validation - 4 simple user mocks)
- Tests Typer callback validators
- Validates business rules enforcement and input sanitization
"""

import pytest
import typer
from datetime import datetime, timedelta
from decimal import Decimal
from src.cli import validators
from src.models.user import Department


class TestValidateEmail:
    """Test validate_email_callback function."""

    @pytest.mark.parametrize(
        "email",
        [
            "user@example.com",
            "test.user@example.com",
            "user+tag@example.co.uk",
        ],
    )
    def test_validate_email_valid(self, email):
        """GIVEN valid email / WHEN validated / THEN returns email"""
        assert validators.validate_email_callback(email) == email

    @pytest.mark.parametrize("email", ["invalid", "invalid@", "@example.com"])
    def test_validate_email_invalid(self, email):
        """GIVEN invalid email / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validators.validate_email_callback(email)


class TestValidatePhone:
    """Test validate_phone_callback function."""

    @pytest.mark.parametrize(
        "phone", ["0612345678", "01 23 45 67 89", "+33612345678"]
    )
    def test_validate_phone_valid(self, phone):
        """GIVEN valid phone / WHEN validated / THEN returns phone"""
        assert validators.validate_phone_callback(phone) == phone

    @pytest.mark.parametrize("phone", ["123", "abcdefghij"])
    def test_validate_phone_invalid(self, phone):
        """GIVEN invalid phone / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validators.validate_phone_callback(phone)


class TestValidatePassword:
    """Test validate_password_callback function."""

    @pytest.mark.parametrize(
        "password",
        [
            "SecurePass123!",
            "MyP@ssw0rd",
            "Test1234!",
            "12345678",
        ],
    )
    def test_validate_password_valid(self, password):
        """GIVEN valid password (>= 8 chars) / WHEN validated / THEN returns password"""
        assert validators.validate_password_callback(password) == password

    def test_validate_password_too_short(self):
        """GIVEN password < 8 chars / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter) as exc_info:
            validators.validate_password_callback("Short1")

        assert "au moins 8 caractères" in str(exc_info.value)


class TestValidateFirstName:
    """Test validate_first_name_callback function."""

    @pytest.mark.parametrize("name", ["Jean", "Marie-Claire", "Anne"])
    def test_validate_first_name_valid(self, name):
        """GIVEN valid first name / WHEN validated / THEN returns name"""
        assert validators.validate_first_name_callback(name) == name

    def test_validate_first_name_too_short(self):
        """GIVEN too short name / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validators.validate_first_name_callback("A")


class TestValidateLastName:
    """Test validate_last_name_callback function."""

    @pytest.mark.parametrize("name", ["Dupont", "Martin-Dubois", "De La Fontaine"])
    def test_validate_last_name_valid(self, name):
        """GIVEN valid last name / WHEN validated / THEN returns name"""
        assert validators.validate_last_name_callback(name) == name

    def test_validate_last_name_too_short(self):
        """GIVEN too short name / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validators.validate_last_name_callback("D")


class TestValidateLocation:
    """Test validate_location_callback function."""

    @pytest.mark.parametrize(
        "location", ["Paris", "New York", "Centre de conférence", "AB"]
    )
    def test_validate_location_valid(self, location):
        """GIVEN valid location / WHEN validated / THEN returns location"""
        assert validators.validate_location_callback(location) == location

    def test_validate_location_empty(self):
        """GIVEN empty location / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter) as exc_info:
            validators.validate_location_callback("")

        assert "requis" in str(exc_info.value)

    def test_validate_location_too_long(self):
        """GIVEN location > 255 chars / WHEN validated / THEN raises BadParameter"""
        long_location = "A" * 256
        with pytest.raises(typer.BadParameter) as exc_info:
            validators.validate_location_callback(long_location)

        assert "255 caractères" in str(exc_info.value)


class TestValidateAttendees:
    """Test validate_attendees_callback function."""

    def test_validate_attendees_valid(self):
        """GIVEN positive integer or zero / WHEN validated / THEN returns integer"""
        assert validators.validate_attendees_callback(0) == 0  # Zero is valid
        assert validators.validate_attendees_callback(1) == 1
        assert validators.validate_attendees_callback(100) == 100
        assert validators.validate_attendees_callback(999) == 999

    def test_validate_attendees_negative(self):
        """GIVEN negative integer / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter) as exc_info:
            validators.validate_attendees_callback(-5)

        assert "positif" in str(exc_info.value)


class TestValidateUsername:
    """Test validate_username_callback function."""

    @pytest.mark.parametrize(
        "username",
        [
            "user123",
            "john_doe",
            "admin-user",
            "test_user_123",
        ],
    )
    def test_validate_username_valid(self, username):
        """GIVEN valid username / WHEN validated / THEN returns username"""
        assert validators.validate_username_callback(username) == username

    def test_validate_username_too_short(self):
        """GIVEN username < 4 chars / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validators.validate_username_callback("abc")

    def test_validate_username_invalid_chars(self):
        """GIVEN username with invalid chars / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validators.validate_username_callback("user@123")


class TestValidateCompanyName:
    """Test validate_company_name_callback function."""

    @pytest.mark.parametrize("name", ["Acme Corp", "Tech Solutions", "ABC Company"])
    def test_validate_company_name_valid(self, name):
        """GIVEN valid company name / WHEN validated / THEN returns name"""
        assert validators.validate_company_name_callback(name) == name

    def test_validate_company_name_empty(self):
        """GIVEN empty company name / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validators.validate_company_name_callback("")

    def test_validate_company_name_whitespace(self):
        """GIVEN only whitespace / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validators.validate_company_name_callback("   ")


class TestValidateIdCallbacks:
    """Test ID validation callbacks using parametrize for DRY principle."""

    @pytest.mark.parametrize(
        "validator_func,valid_ids,invalid_ids",
        [
            # Sales contact ID: accepts 0 (auto-assign) and positive integers
            (
                validators.validate_sales_contact_id_callback,
                [0, 1, 999],
                [-1],
            ),
            # Support contact ID: accepts 0 (optional) and positive integers
            (
                validators.validate_support_contact_id_callback,
                [0, 1, 999],
                [-1],
            ),
            # Client ID: only positive integers (0 not allowed)
            (
                validators.validate_client_id_callback,
                [1, 999],
                [0, -1],
            ),
            # Contract ID: only positive integers
            (
                validators.validate_contract_id_callback,
                [1, 999],
                [0, -1],
            ),
            # Event ID: only positive integers
            (
                validators.validate_event_id_callback,
                [1, 999],
                [0],
            ),
            # User ID: only positive integers
            (
                validators.validate_user_id_callback,
                [1, 999],
                [0],
            ),
        ],
        ids=[
            "sales_contact_id",
            "support_contact_id",
            "client_id",
            "contract_id",
            "event_id",
            "user_id",
        ],
    )
    def test_id_validators_valid(self, validator_func, valid_ids, invalid_ids):
        """GIVEN valid ID values / WHEN validated / THEN returns ID unchanged"""
        for valid_id in valid_ids:
            assert validator_func(valid_id) == valid_id

    @pytest.mark.parametrize(
        "validator_func,valid_ids,invalid_ids",
        [
            (
                validators.validate_sales_contact_id_callback,
                [0, 1, 999],
                [-1],
            ),
            (
                validators.validate_support_contact_id_callback,
                [0, 1, 999],
                [-1],
            ),
            (
                validators.validate_client_id_callback,
                [1, 999],
                [0, -1],
            ),
            (
                validators.validate_contract_id_callback,
                [1, 999],
                [0, -1],
            ),
            (
                validators.validate_event_id_callback,
                [1, 999],
                [0],
            ),
            (
                validators.validate_user_id_callback,
                [1, 999],
                [0],
            ),
        ],
        ids=[
            "sales_contact_id",
            "support_contact_id",
            "client_id",
            "contract_id",
            "event_id",
            "user_id",
        ],
    )
    def test_id_validators_invalid(self, validator_func, valid_ids, invalid_ids):
        """GIVEN invalid ID values / WHEN validated / THEN raises BadParameter"""
        for invalid_id in invalid_ids:
            with pytest.raises(typer.BadParameter):
                validator_func(invalid_id)


class TestValidateEventName:
    """Test validate_event_name_callback function."""

    @pytest.mark.parametrize("name", ["Conference 2025", "Tech Workshop", "ABC"])
    def test_validate_event_name_valid(self, name):
        """GIVEN valid event name / WHEN validated / THEN returns name"""
        assert validators.validate_event_name_callback(name) == name

    def test_validate_event_name_too_short(self):
        """GIVEN name < 3 chars / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validators.validate_event_name_callback("AB")

    def test_validate_event_name_too_long(self):
        """GIVEN name > 100 chars / WHEN validated / THEN raises BadParameter"""
        long_name = "A" * 101
        with pytest.raises(typer.BadParameter):
            validators.validate_event_name_callback(long_name)


class TestValidateAmount:
    """Test validate_amount_callback function."""

    def test_validate_amount_valid(self):
        """GIVEN valid amount / WHEN validated / THEN returns amount"""
        assert validators.validate_amount_callback("100.00") == "100.00"
        assert validators.validate_amount_callback("0") == "0"
        assert validators.validate_amount_callback("1234.56") == "1234.56"

    def test_validate_amount_negative(self):
        """GIVEN negative amount / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validators.validate_amount_callback("-100")

    def test_validate_amount_invalid_format(self):
        """GIVEN invalid format / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validators.validate_amount_callback("abc")


class TestValidateDepartment:
    """Test validate_department_callback function."""

    def test_validate_department_valid(self):
        """GIVEN valid department choice / WHEN validated / THEN returns choice"""
        # Department enum has 3 values: GESTION, COMMERCIAL, SUPPORT
        assert validators.validate_department_callback(1) == 1
        assert validators.validate_department_callback(2) == 2
        assert validators.validate_department_callback(3) == 3

    def test_validate_department_invalid(self):
        """GIVEN invalid department choice / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validators.validate_department_callback(0)
        with pytest.raises(typer.BadParameter):
            validators.validate_department_callback(4)


class TestValidateContractAmounts:
    """Test validate_contract_amounts business function."""

    def test_validate_contract_amounts_valid(self):
        """GIVEN valid amounts / WHEN validated / THEN no error"""
        # Should not raise any exception
        validators.validate_contract_amounts(
            total_amount=Decimal("10000"), remaining_amount=Decimal("5000")
        )
        validators.validate_contract_amounts(
            total_amount=Decimal("10000"), remaining_amount=Decimal("10000")
        )
        validators.validate_contract_amounts(
            total_amount=Decimal("10000"), remaining_amount=Decimal("0")
        )

    def test_validate_contract_amounts_negative_total(self):
        """GIVEN negative total / WHEN validated / THEN raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            validators.validate_contract_amounts(
                total_amount=Decimal("-100"), remaining_amount=Decimal("0")
            )
        assert "positif" in str(exc_info.value)

    def test_validate_contract_amounts_negative_remaining(self):
        """GIVEN negative remaining / WHEN validated / THEN raises ValueError"""
        with pytest.raises(ValueError):
            validators.validate_contract_amounts(
                total_amount=Decimal("1000"), remaining_amount=Decimal("-100")
            )

    def test_validate_contract_amounts_remaining_exceeds_total(self):
        """GIVEN remaining > total / WHEN validated / THEN raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            validators.validate_contract_amounts(
                total_amount=Decimal("1000"), remaining_amount=Decimal("1500")
            )
        assert "dépasser" in str(exc_info.value)


class TestValidatePaymentAmount:
    """Test validate_payment_amount business function."""

    def test_validate_payment_amount_valid(self):
        """GIVEN valid payment / WHEN validated / THEN no error"""
        validators.validate_payment_amount(
            amount_paid=Decimal("500"), remaining_amount=Decimal("1000")
        )
        validators.validate_payment_amount(
            amount_paid=Decimal("1000"), remaining_amount=Decimal("1000")
        )

    def test_validate_payment_amount_zero(self):
        """GIVEN payment = 0 / WHEN validated / THEN raises ValueError"""
        with pytest.raises(ValueError):
            validators.validate_payment_amount(
                amount_paid=Decimal("0"), remaining_amount=Decimal("1000")
            )

    def test_validate_payment_amount_negative(self):
        """GIVEN negative payment / WHEN validated / THEN raises ValueError"""
        with pytest.raises(ValueError):
            validators.validate_payment_amount(
                amount_paid=Decimal("-100"), remaining_amount=Decimal("1000")
            )

    def test_validate_payment_amount_exceeds_remaining(self):
        """GIVEN payment > remaining / WHEN validated / THEN raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            validators.validate_payment_amount(
                amount_paid=Decimal("1500"), remaining_amount=Decimal("1000")
            )
        assert "dépasse" in str(exc_info.value)


class TestValidateUserIsCommercial:
    """Test validate_user_is_commercial business function."""

    def test_validate_user_is_commercial_valid(self, mocker):
        """GIVEN COMMERCIAL user / WHEN validated / THEN no error"""
        user = mocker.Mock()
        user.id = 1
        user.department = Department.COMMERCIAL

        # Should not raise any exception
        validators.validate_user_is_commercial(user)

    def test_validate_user_is_commercial_invalid(self, mocker):
        """GIVEN non-COMMERCIAL user / WHEN validated / THEN raises ValueError"""
        user = mocker.Mock()
        user.id = 1
        user.department = Department.GESTION

        with pytest.raises(ValueError) as exc_info:
            validators.validate_user_is_commercial(user)
        assert "COMMERCIAL" in str(exc_info.value)


class TestValidateUserIsSupport:
    """Test validate_user_is_support business function."""

    def test_validate_user_is_support_valid(self, mocker):
        """GIVEN SUPPORT user / WHEN validated / THEN no error"""
        user = mocker.Mock()
        user.id = 1
        user.department = Department.SUPPORT

        # Should not raise any exception
        validators.validate_user_is_support(user)

    def test_validate_user_is_support_invalid(self, mocker):
        """GIVEN non-SUPPORT user / WHEN validated / THEN raises ValueError"""
        user = mocker.Mock()
        user.id = 1
        user.department = Department.COMMERCIAL

        with pytest.raises(ValueError) as exc_info:
            validators.validate_user_is_support(user)
        assert "SUPPORT" in str(exc_info.value)


class TestValidateEventDates:
    """Test validate_event_dates business function."""

    def test_validate_event_dates_valid(self):
        """GIVEN valid dates / WHEN validated / THEN no error"""
        # Event in the future with valid end > start
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=2)

        validators.validate_event_dates(
            event_start=start, event_end=end, attendees=50
        )

    def test_validate_event_dates_end_before_start(self):
        """GIVEN end <= start / WHEN validated / THEN raises ValueError"""
        start = datetime.now() + timedelta(days=1)
        end = start - timedelta(hours=1)  # End before start

        with pytest.raises(ValueError) as exc_info:
            validators.validate_event_dates(
                event_start=start, event_end=end, attendees=50
            )
        assert "postérieure" in str(exc_info.value)

    def test_validate_event_dates_negative_attendees(self):
        """GIVEN negative attendees / WHEN validated / THEN raises ValueError"""
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=2)

        with pytest.raises(ValueError):
            validators.validate_event_dates(
                event_start=start, event_end=end, attendees=-5
            )

    def test_validate_event_dates_in_past(self):
        """GIVEN start in past / WHEN validated / THEN raises ValueError"""
        start = datetime.now() - timedelta(days=1)  # Yesterday
        end = start + timedelta(hours=2)

        with pytest.raises(ValueError) as exc_info:
            validators.validate_event_dates(
                event_start=start, event_end=end, attendees=50
            )
        assert "futur" in str(exc_info.value)


class TestValidateAttendeesPositive:
    """Test validate_attendees_positive business function."""

    def test_validate_attendees_positive_valid(self):
        """GIVEN positive attendees / WHEN validated / THEN no error"""
        validators.validate_attendees_positive(0)
        validators.validate_attendees_positive(1)
        validators.validate_attendees_positive(100)

    def test_validate_attendees_positive_negative(self):
        """GIVEN negative attendees / WHEN validated / THEN raises ValueError"""
        with pytest.raises(ValueError):
            validators.validate_attendees_positive(-5)
