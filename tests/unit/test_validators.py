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
from src.cli.business_validator import BusinessValidator
from src.models.user import Department


class TestValidateEmail:
    """Test validate_email_callback function."""

    @pytest.mark.parametrize(
        "email",
        ["user@example.com", "test.user@example.com", "user+tag@example.co.uk"],
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
        "password", ["SecurePass123!", "MyP@ssw0rd", "Test1234!", "12345678"]
    )
    def test_validate_password_valid(self, password):
        """GIVEN valid password (>= 8 chars) / WHEN validated / THEN returns password"""
        assert validators.validate_password_callback(password) == password

    def test_validate_password_too_short(self):
        """GIVEN password < 8 chars / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter) as exc_info:
            validators.validate_password_callback("Short1")
        assert "au moins 8 caractères" in str(exc_info.value)


class TestValidateNames:
    """Test validate_first_name_callback and validate_last_name_callback functions."""

    @pytest.mark.parametrize(
        "validator,name",
        [
            (validators.validate_first_name_callback, "Jean"),
            (validators.validate_first_name_callback, "Marie-Claire"),
            (validators.validate_first_name_callback, "O'Connor"),
            (validators.validate_last_name_callback, "Dupont"),
            (validators.validate_last_name_callback, "Martin-Dubois"),
            (validators.validate_last_name_callback, "De La Fontaine"),
        ],
        ids=[
            "first_name-simple",
            "first_name-hyphen",
            "first_name-apostrophe",
            "last_name-simple",
            "last_name-hyphen",
            "last_name-spaces",
        ],
    )
    def test_validate_name_valid(self, validator, name):
        """GIVEN valid name / WHEN validated / THEN returns name"""
        assert validator(name) == name

    @pytest.mark.parametrize(
        "validator,name",
        [
            (validators.validate_first_name_callback, "A"),
            (validators.validate_last_name_callback, "D"),
        ],
        ids=["first_name-too_short", "last_name-too_short"],
    )
    def test_validate_name_too_short(self, validator, name):
        """GIVEN too short name / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validator(name)

    @pytest.mark.parametrize(
        "validator,name",
        [
            (validators.validate_first_name_callback, "Jean123"),
            (validators.validate_first_name_callback, "Marie@Claire"),
            (validators.validate_last_name_callback, "Dupont123"),
            (validators.validate_last_name_callback, "Martin@Dubois"),
        ],
        ids=[
            "first_name-digits",
            "first_name-symbol",
            "last_name-digits",
            "last_name-symbol",
        ],
    )
    def test_validate_name_invalid_chars(self, validator, name):
        """GIVEN name with invalid chars / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter) as exc_info:
            validator(name)
        assert "lettres" in str(exc_info.value)


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
        with pytest.raises(typer.BadParameter) as exc_info:
            validators.validate_location_callback("A" * 256)
        assert "255 caractères" in str(exc_info.value)


class TestValidateAttendees:
    """Test validate_attendees_callback function."""

    @pytest.mark.parametrize("value", [0, 1, 100, 999])
    def test_validate_attendees_valid(self, value):
        """GIVEN positive integer or zero / WHEN validated / THEN returns integer"""
        assert validators.validate_attendees_callback(value) == value

    def test_validate_attendees_negative(self):
        """GIVEN negative integer / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter) as exc_info:
            validators.validate_attendees_callback(-5)
        assert "positif" in str(exc_info.value)


class TestValidateUsername:
    """Test validate_username_callback function."""

    @pytest.mark.parametrize(
        "username", ["user123", "john_doe", "admin-user", "test_user_123"]
    )
    def test_validate_username_valid(self, username):
        """GIVEN valid username / WHEN validated / THEN returns username"""
        assert validators.validate_username_callback(username) == username

    @pytest.mark.parametrize(
        "username,reason",
        [("abc", "too_short"), ("user@123", "invalid_chars")],
        ids=["too_short", "invalid_chars"],
    )
    def test_validate_username_invalid(self, username, reason):
        """GIVEN invalid username / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validators.validate_username_callback(username)


class TestValidateCompanyName:
    """Test validate_company_name_callback function."""

    @pytest.mark.parametrize(
        "name", ["Acme Corp", "Tech Solutions", "ABC Company"]
    )
    def test_validate_company_name_valid(self, name):
        """GIVEN valid company name / WHEN validated / THEN returns name"""
        assert validators.validate_company_name_callback(name) == name

    @pytest.mark.parametrize("name", ["", "   "], ids=["empty", "whitespace"])
    def test_validate_company_name_invalid(self, name):
        """GIVEN empty or whitespace company name / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validators.validate_company_name_callback(name)


# Configuration for ID validators - single source of truth
ID_VALIDATORS_CONFIG = [
    # (validator_func, valid_ids, invalid_ids, name)
    (validators.validate_sales_contact_id_callback, [0, 1, 999], [-1], "sales_contact"),
    (validators.validate_support_contact_id_callback, [0, 1, 999], [-1], "support_contact"),
    (validators.validate_client_id_callback, [1, 999], [0, -1], "client"),
    (validators.validate_contract_id_callback, [1, 999], [0, -1], "contract"),
    (validators.validate_event_id_callback, [1, 999], [0, -1], "event"),
    (validators.validate_user_id_callback, [1, 999], [0, -1], "user"),
]


class TestValidateIdCallbacks:
    """Test ID validation callbacks using parametrize for DRY principle."""

    @pytest.mark.parametrize(
        "validator_func,valid_ids,invalid_ids,name",
        ID_VALIDATORS_CONFIG,
        ids=[c[3] for c in ID_VALIDATORS_CONFIG],
    )
    def test_id_validators_valid(self, validator_func, valid_ids, invalid_ids, name):
        """GIVEN valid ID values / WHEN validated / THEN returns ID unchanged"""
        for valid_id in valid_ids:
            assert validator_func(valid_id) == valid_id

    @pytest.mark.parametrize(
        "validator_func,valid_ids,invalid_ids,name",
        ID_VALIDATORS_CONFIG,
        ids=[c[3] for c in ID_VALIDATORS_CONFIG],
    )
    def test_id_validators_invalid(self, validator_func, valid_ids, invalid_ids, name):
        """GIVEN invalid ID values / WHEN validated / THEN raises BadParameter"""
        for invalid_id in invalid_ids:
            with pytest.raises(typer.BadParameter):
                validator_func(invalid_id)


class TestValidateEventName:
    """Test validate_event_name_callback function."""

    @pytest.mark.parametrize(
        "name", ["Conference 2025", "Tech Workshop", "ABC"]
    )
    def test_validate_event_name_valid(self, name):
        """GIVEN valid event name / WHEN validated / THEN returns name"""
        assert validators.validate_event_name_callback(name) == name

    @pytest.mark.parametrize(
        "name,reason",
        [("AB", "too_short"), ("A" * 101, "too_long")],
        ids=["too_short", "too_long"],
    )
    def test_validate_event_name_invalid(self, name, reason):
        """GIVEN invalid event name / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validators.validate_event_name_callback(name)


class TestValidateAmount:
    """Test validate_amount_callback function."""

    @pytest.mark.parametrize("amount", ["100.00", "0", "1234.56"])
    def test_validate_amount_valid(self, amount):
        """GIVEN valid amount / WHEN validated / THEN returns amount"""
        assert validators.validate_amount_callback(amount) == amount

    @pytest.mark.parametrize(
        "amount,reason",
        [("-100", "negative"), ("abc", "invalid_format")],
        ids=["negative", "invalid_format"],
    )
    def test_validate_amount_invalid(self, amount, reason):
        """GIVEN invalid amount / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validators.validate_amount_callback(amount)


class TestValidateDepartment:
    """Test validate_department_callback function."""

    @pytest.mark.parametrize("choice", [1, 2, 3])
    def test_validate_department_valid(self, choice):
        """GIVEN valid department choice / WHEN validated / THEN returns choice"""
        assert validators.validate_department_callback(choice) == choice

    @pytest.mark.parametrize("choice", [0, 4, -1])
    def test_validate_department_invalid(self, choice):
        """GIVEN invalid department choice / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validators.validate_department_callback(choice)


class TestValidateContractAmounts:
    """Test validate_contract_amounts business function."""

    @pytest.mark.parametrize(
        "total,remaining",
        [
            (Decimal("10000"), Decimal("5000")),
            (Decimal("10000"), Decimal("10000")),
            (Decimal("10000"), Decimal("0")),
        ],
        ids=["partial", "full_remaining", "zero_remaining"],
    )
    def test_validate_contract_amounts_valid(self, total, remaining):
        """GIVEN valid amounts / WHEN validated / THEN no error"""
        BusinessValidator.validate_contract_amounts(
            total_amount=total, remaining_amount=remaining
        )

    @pytest.mark.parametrize(
        "total,remaining,error_msg",
        [
            (Decimal("-100"), Decimal("0"), "positif"),
            (Decimal("1000"), Decimal("-100"), "positif"),
            (Decimal("1000"), Decimal("1500"), "dépasser"),
        ],
        ids=["negative_total", "negative_remaining", "remaining_exceeds_total"],
    )
    def test_validate_contract_amounts_invalid(self, total, remaining, error_msg):
        """GIVEN invalid amounts / WHEN validated / THEN raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            BusinessValidator.validate_contract_amounts(
                total_amount=total, remaining_amount=remaining
            )
        assert error_msg in str(exc_info.value)


class TestValidatePaymentAmount:
    """Test validate_payment_amount business function."""

    @pytest.mark.parametrize(
        "paid,remaining",
        [(Decimal("500"), Decimal("1000")), (Decimal("1000"), Decimal("1000"))],
        ids=["partial_payment", "full_payment"],
    )
    def test_validate_payment_amount_valid(self, paid, remaining):
        """GIVEN valid payment / WHEN validated / THEN no error"""
        BusinessValidator.validate_payment_amount(
            amount_paid=paid, remaining_amount=remaining
        )

    @pytest.mark.parametrize(
        "paid,remaining,error_msg",
        [
            (Decimal("0"), Decimal("1000"), "positif"),
            (Decimal("-100"), Decimal("1000"), "positif"),
            (Decimal("1500"), Decimal("1000"), "dépasse"),
        ],
        ids=["zero_payment", "negative_payment", "exceeds_remaining"],
    )
    def test_validate_payment_amount_invalid(self, paid, remaining, error_msg):
        """GIVEN invalid payment / WHEN validated / THEN raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            BusinessValidator.validate_payment_amount(
                amount_paid=paid, remaining_amount=remaining
            )
        assert error_msg in str(exc_info.value)


class TestValidateUserDepartment:
    """Test validate_user_is_commercial and validate_user_is_support business functions."""

    @pytest.mark.parametrize(
        "validator,valid_dept,invalid_dept",
        [
            (
                BusinessValidator.validate_user_is_commercial,
                Department.COMMERCIAL,
                Department.GESTION,
            ),
            (
                BusinessValidator.validate_user_is_support,
                Department.SUPPORT,
                Department.COMMERCIAL,
            ),
        ],
        ids=["commercial", "support"],
    )
    def test_validate_user_department_valid(self, validator, valid_dept, invalid_dept, mocker):
        """GIVEN user with correct department / WHEN validated / THEN no error"""
        user = mocker.Mock()
        user.id = 1
        user.department = valid_dept
        validator(user)  # Should not raise

    @pytest.mark.parametrize(
        "validator,valid_dept,invalid_dept,expected_msg",
        [
            (
                BusinessValidator.validate_user_is_commercial,
                Department.COMMERCIAL,
                Department.GESTION,
                "COMMERCIAL",
            ),
            (
                BusinessValidator.validate_user_is_support,
                Department.SUPPORT,
                Department.COMMERCIAL,
                "SUPPORT",
            ),
        ],
        ids=["commercial", "support"],
    )
    def test_validate_user_department_invalid(
        self, validator, valid_dept, invalid_dept, expected_msg, mocker
    ):
        """GIVEN user with wrong department / WHEN validated / THEN raises ValueError"""
        user = mocker.Mock()
        user.id = 1
        user.department = invalid_dept
        with pytest.raises(ValueError) as exc_info:
            validator(user)
        assert expected_msg in str(exc_info.value)


class TestValidateEventDates:
    """Test validate_event_dates business function."""

    def test_validate_event_dates_valid(self):
        """GIVEN valid dates / WHEN validated / THEN no error"""
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=2)
        BusinessValidator.validate_event_dates(
            event_start=start, event_end=end, attendees=50
        )

    @pytest.mark.parametrize(
        "start_offset,end_offset,attendees,error_msg",
        [
            (timedelta(days=1), timedelta(hours=-1), 50, "postérieure"),
            (timedelta(days=1), timedelta(hours=2), -5, "positif"),
            (timedelta(days=-1), timedelta(hours=2), 50, "futur"),
        ],
        ids=["end_before_start", "negative_attendees", "start_in_past"],
    )
    def test_validate_event_dates_invalid(
        self, start_offset, end_offset, attendees, error_msg
    ):
        """GIVEN invalid event data / WHEN validated / THEN raises ValueError"""
        start = datetime.now() + start_offset
        end = start + end_offset
        with pytest.raises(ValueError) as exc_info:
            BusinessValidator.validate_event_dates(
                event_start=start, event_end=end, attendees=attendees
            )
        assert error_msg in str(exc_info.value)


class TestValidateAttendeesPositive:
    """Test validate_attendees_positive business function."""

    @pytest.mark.parametrize("value", [0, 1, 100])
    def test_validate_attendees_positive_valid(self, value):
        """GIVEN positive attendees / WHEN validated / THEN no error"""
        BusinessValidator.validate_attendees_positive(value)

    def test_validate_attendees_positive_negative(self):
        """GIVEN negative attendees / WHEN validated / THEN raises ValueError"""
        with pytest.raises(ValueError):
            BusinessValidator.validate_attendees_positive(-5)
