"""
Tests unitaires pour les validators (sécurité).

Tests couverts:
- validate_email_callback() : validation format email
- validate_phone_callback() : validation téléphone français
- validate_password_callback() : politique mots de passe forts
- validate_first_name_callback() : validation prénoms
- validate_last_name_callback() : validation noms
- validate_location_callback() : validation lieux
- validate_attendees_callback() : validation entiers positifs
- validate_username_callback() : validation nom d'utilisateur
- validate_company_name_callback() : validation nom entreprise
- validate_sales_contact_id_callback() : validation ID contact commercial
- validate_client_id_callback() : validation ID client
- validate_contract_id_callback() : validation ID contrat
- validate_event_id_callback() : validation ID événement
- validate_user_id_callback() : validation ID utilisateur
- validate_support_contact_id_callback() : validation ID contact support
- validate_event_name_callback() : validation nom événement
- validate_amount_callback() : validation montants monétaires
- validate_department_callback() : validation sélection département
- validate_contract_amounts() : validation règles métier contrats
- validate_payment_amount() : validation règles métier paiements
- validate_user_is_commercial() : validation département COMMERCIAL
- validate_user_is_support() : validation département SUPPORT
- validate_event_dates() : validation dates événements
- validate_attendees_positive() : validation participants positif
"""

import pytest
import typer
from datetime import datetime, timedelta
from decimal import Decimal
from src.cli.validators import (
    validate_email_callback,
    validate_phone_callback,
    validate_password_callback,
    validate_first_name_callback,
    validate_last_name_callback,
    validate_location_callback,
    validate_attendees_callback,
    validate_username_callback,
    validate_company_name_callback,
    validate_sales_contact_id_callback,
    validate_client_id_callback,
    validate_contract_id_callback,
    validate_event_id_callback,
    validate_user_id_callback,
    validate_support_contact_id_callback,
    validate_event_name_callback,
    validate_amount_callback,
    validate_department_callback,
    validate_contract_amounts,
    validate_payment_amount,
    validate_user_is_commercial,
    validate_user_is_support,
    validate_event_dates,
    validate_attendees_positive,
)
from src.models.user import Department


class TestValidateEmail:
    """Test validate_email_callback function."""

    def test_validate_email_valid(self):
        """GIVEN valid email / WHEN validated / THEN returns email"""
        valid_emails = [
            "user@example.com",
            "test.user@example.com",
            "user+tag@example.co.uk",
        ]
        for email in valid_emails:
            assert validate_email_callback(email) == email

    def test_validate_email_invalid(self):
        """GIVEN invalid email / WHEN validated / THEN raises BadParameter"""
        invalid_emails = ["invalid", "invalid@", "@example.com"]
        for email in invalid_emails:
            with pytest.raises(typer.BadParameter):
                validate_email_callback(email)


class TestValidatePhone:
    """Test validate_phone_callback function."""

    def test_validate_phone_valid(self):
        """GIVEN valid phone / WHEN validated / THEN returns phone"""
        valid_phones = ["0612345678", "01 23 45 67 89", "+33612345678"]
        for phone in valid_phones:
            assert validate_phone_callback(phone) == phone

    def test_validate_phone_invalid(self):
        """GIVEN invalid phone / WHEN validated / THEN raises BadParameter"""
        invalid_phones = ["123", "abcdefghij"]
        for phone in invalid_phones:
            with pytest.raises(typer.BadParameter):
                validate_phone_callback(phone)


class TestValidatePassword:
    """Test validate_password_callback function."""

    def test_validate_password_valid(self):
        """GIVEN valid password (>= 8 chars) / WHEN validated / THEN returns password"""
        valid_passwords = ["SecurePass123!", "MyP@ssw0rd", "Test1234!", "12345678"]
        for password in valid_passwords:
            assert validate_password_callback(password) == password

    def test_validate_password_too_short(self):
        """GIVEN password < 8 chars / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_password_callback("Short1")

        assert "au moins 8 caractères" in str(exc_info.value)


class TestValidateFirstName:
    """Test validate_first_name_callback function."""

    def test_validate_first_name_valid(self):
        """GIVEN valid first name / WHEN validated / THEN returns name"""
        valid_names = ["Jean", "Marie-Claire", "Anne"]
        for name in valid_names:
            assert validate_first_name_callback(name) == name

    def test_validate_first_name_too_short(self):
        """GIVEN too short name / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validate_first_name_callback("A")


class TestValidateLastName:
    """Test validate_last_name_callback function."""

    def test_validate_last_name_valid(self):
        """GIVEN valid last name / WHEN validated / THEN returns name"""
        valid_names = ["Dupont", "Martin-Dubois", "De La Fontaine"]
        for name in valid_names:
            assert validate_last_name_callback(name) == name

    def test_validate_last_name_too_short(self):
        """GIVEN too short name / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validate_last_name_callback("D")


class TestValidateLocation:
    """Test validate_location_callback function."""

    def test_validate_location_valid(self):
        """GIVEN valid location / WHEN validated / THEN returns location"""
        valid_locations = ["Paris", "New York", "Centre de conférence", "AB"]
        for location in valid_locations:
            assert validate_location_callback(location) == location

    def test_validate_location_empty(self):
        """GIVEN empty location / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_location_callback("")

        assert "requis" in str(exc_info.value)

    def test_validate_location_too_long(self):
        """GIVEN location > 255 chars / WHEN validated / THEN raises BadParameter"""
        long_location = "A" * 256
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_location_callback(long_location)

        assert "255 caractères" in str(exc_info.value)


class TestValidateAttendees:
    """Test validate_attendees_callback function."""

    def test_validate_attendees_valid(self):
        """GIVEN positive integer or zero / WHEN validated / THEN returns integer"""
        assert validate_attendees_callback(0) == 0  # Zero is valid
        assert validate_attendees_callback(1) == 1
        assert validate_attendees_callback(100) == 100
        assert validate_attendees_callback(999) == 999

    def test_validate_attendees_negative(self):
        """GIVEN negative integer / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter) as exc_info:
            validate_attendees_callback(-5)

        assert "positif" in str(exc_info.value)


class TestValidateUsername:
    """Test validate_username_callback function."""

    def test_validate_username_valid(self):
        """GIVEN valid username / WHEN validated / THEN returns username"""
        valid_usernames = ["user123", "john_doe", "admin-user", "test_user_123"]
        for username in valid_usernames:
            assert validate_username_callback(username) == username

    def test_validate_username_too_short(self):
        """GIVEN username < 4 chars / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validate_username_callback("abc")

    def test_validate_username_invalid_chars(self):
        """GIVEN username with invalid chars / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validate_username_callback("user@123")


class TestValidateCompanyName:
    """Test validate_company_name_callback function."""

    def test_validate_company_name_valid(self):
        """GIVEN valid company name / WHEN validated / THEN returns name"""
        valid_names = ["Acme Corp", "Tech Solutions", "ABC Company"]
        for name in valid_names:
            assert validate_company_name_callback(name) == name

    def test_validate_company_name_empty(self):
        """GIVEN empty company name / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validate_company_name_callback("")

    def test_validate_company_name_whitespace(self):
        """GIVEN only whitespace / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validate_company_name_callback("   ")


class TestValidateSalesContactId:
    """Test validate_sales_contact_id_callback function."""

    def test_validate_sales_contact_id_valid(self):
        """GIVEN valid ID (0 or positive) / WHEN validated / THEN returns ID"""
        assert validate_sales_contact_id_callback(0) == 0  # Auto-assign
        assert validate_sales_contact_id_callback(1) == 1
        assert validate_sales_contact_id_callback(999) == 999

    def test_validate_sales_contact_id_negative(self):
        """GIVEN negative ID / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validate_sales_contact_id_callback(-1)


class TestValidateClientId:
    """Test validate_client_id_callback function."""

    def test_validate_client_id_valid(self):
        """GIVEN positive ID / WHEN validated / THEN returns ID"""
        assert validate_client_id_callback(1) == 1
        assert validate_client_id_callback(999) == 999

    def test_validate_client_id_zero(self):
        """GIVEN ID = 0 / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validate_client_id_callback(0)

    def test_validate_client_id_negative(self):
        """GIVEN negative ID / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validate_client_id_callback(-1)


class TestValidateContractId:
    """Test validate_contract_id_callback function."""

    def test_validate_contract_id_valid(self):
        """GIVEN positive ID / WHEN validated / THEN returns ID"""
        assert validate_contract_id_callback(1) == 1
        assert validate_contract_id_callback(999) == 999

    def test_validate_contract_id_invalid(self):
        """GIVEN ID <= 0 / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validate_contract_id_callback(0)
        with pytest.raises(typer.BadParameter):
            validate_contract_id_callback(-1)


class TestValidateEventId:
    """Test validate_event_id_callback function."""

    def test_validate_event_id_valid(self):
        """GIVEN positive ID / WHEN validated / THEN returns ID"""
        assert validate_event_id_callback(1) == 1
        assert validate_event_id_callback(999) == 999

    def test_validate_event_id_invalid(self):
        """GIVEN ID <= 0 / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validate_event_id_callback(0)


class TestValidateUserId:
    """Test validate_user_id_callback function."""

    def test_validate_user_id_valid(self):
        """GIVEN positive ID / WHEN validated / THEN returns ID"""
        assert validate_user_id_callback(1) == 1
        assert validate_user_id_callback(999) == 999

    def test_validate_user_id_invalid(self):
        """GIVEN ID <= 0 / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validate_user_id_callback(0)


class TestValidateSupportContactId:
    """Test validate_support_contact_id_callback function."""

    def test_validate_support_contact_id_valid(self):
        """GIVEN valid ID (0 or positive) / WHEN validated / THEN returns ID"""
        assert validate_support_contact_id_callback(0) == 0  # Optional
        assert validate_support_contact_id_callback(1) == 1
        assert validate_support_contact_id_callback(999) == 999

    def test_validate_support_contact_id_negative(self):
        """GIVEN negative ID / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validate_support_contact_id_callback(-1)


class TestValidateEventName:
    """Test validate_event_name_callback function."""

    def test_validate_event_name_valid(self):
        """GIVEN valid event name / WHEN validated / THEN returns name"""
        valid_names = ["Conference 2025", "Tech Workshop", "ABC"]
        for name in valid_names:
            assert validate_event_name_callback(name) == name

    def test_validate_event_name_too_short(self):
        """GIVEN name < 3 chars / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validate_event_name_callback("AB")

    def test_validate_event_name_too_long(self):
        """GIVEN name > 100 chars / WHEN validated / THEN raises BadParameter"""
        long_name = "A" * 101
        with pytest.raises(typer.BadParameter):
            validate_event_name_callback(long_name)


class TestValidateAmount:
    """Test validate_amount_callback function."""

    def test_validate_amount_valid(self):
        """GIVEN valid amount / WHEN validated / THEN returns amount"""
        assert validate_amount_callback("100.00") == "100.00"
        assert validate_amount_callback("0") == "0"
        assert validate_amount_callback("1234.56") == "1234.56"

    def test_validate_amount_negative(self):
        """GIVEN negative amount / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validate_amount_callback("-100")

    def test_validate_amount_invalid_format(self):
        """GIVEN invalid format / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validate_amount_callback("abc")


class TestValidateDepartment:
    """Test validate_department_callback function."""

    def test_validate_department_valid(self):
        """GIVEN valid department choice / WHEN validated / THEN returns choice"""
        # Department enum has 3 values: GESTION, COMMERCIAL, SUPPORT
        assert validate_department_callback(1) == 1
        assert validate_department_callback(2) == 2
        assert validate_department_callback(3) == 3

    def test_validate_department_invalid(self):
        """GIVEN invalid department choice / WHEN validated / THEN raises BadParameter"""
        with pytest.raises(typer.BadParameter):
            validate_department_callback(0)
        with pytest.raises(typer.BadParameter):
            validate_department_callback(4)


class TestValidateContractAmounts:
    """Test validate_contract_amounts business function."""

    def test_validate_contract_amounts_valid(self):
        """GIVEN valid amounts / WHEN validated / THEN no error"""
        # Should not raise any exception
        validate_contract_amounts(
            total_amount=Decimal("10000"), remaining_amount=Decimal("5000")
        )
        validate_contract_amounts(
            total_amount=Decimal("10000"), remaining_amount=Decimal("10000")
        )
        validate_contract_amounts(
            total_amount=Decimal("10000"), remaining_amount=Decimal("0")
        )

    def test_validate_contract_amounts_negative_total(self):
        """GIVEN negative total / WHEN validated / THEN raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            validate_contract_amounts(
                total_amount=Decimal("-100"), remaining_amount=Decimal("0")
            )
        assert "positif" in str(exc_info.value)

    def test_validate_contract_amounts_negative_remaining(self):
        """GIVEN negative remaining / WHEN validated / THEN raises ValueError"""
        with pytest.raises(ValueError):
            validate_contract_amounts(
                total_amount=Decimal("1000"), remaining_amount=Decimal("-100")
            )

    def test_validate_contract_amounts_remaining_exceeds_total(self):
        """GIVEN remaining > total / WHEN validated / THEN raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            validate_contract_amounts(
                total_amount=Decimal("1000"), remaining_amount=Decimal("1500")
            )
        assert "dépasser" in str(exc_info.value)


class TestValidatePaymentAmount:
    """Test validate_payment_amount business function."""

    def test_validate_payment_amount_valid(self):
        """GIVEN valid payment / WHEN validated / THEN no error"""
        validate_payment_amount(
            amount_paid=Decimal("500"), remaining_amount=Decimal("1000")
        )
        validate_payment_amount(
            amount_paid=Decimal("1000"), remaining_amount=Decimal("1000")
        )

    def test_validate_payment_amount_zero(self):
        """GIVEN payment = 0 / WHEN validated / THEN raises ValueError"""
        with pytest.raises(ValueError):
            validate_payment_amount(
                amount_paid=Decimal("0"), remaining_amount=Decimal("1000")
            )

    def test_validate_payment_amount_negative(self):
        """GIVEN negative payment / WHEN validated / THEN raises ValueError"""
        with pytest.raises(ValueError):
            validate_payment_amount(
                amount_paid=Decimal("-100"), remaining_amount=Decimal("1000")
            )

    def test_validate_payment_amount_exceeds_remaining(self):
        """GIVEN payment > remaining / WHEN validated / THEN raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            validate_payment_amount(
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
        validate_user_is_commercial(user)

    def test_validate_user_is_commercial_invalid(self, mocker):
        """GIVEN non-COMMERCIAL user / WHEN validated / THEN raises ValueError"""
        user = mocker.Mock()
        user.id = 1
        user.department = Department.GESTION

        with pytest.raises(ValueError) as exc_info:
            validate_user_is_commercial(user)
        assert "COMMERCIAL" in str(exc_info.value)


class TestValidateUserIsSupport:
    """Test validate_user_is_support business function."""

    def test_validate_user_is_support_valid(self, mocker):
        """GIVEN SUPPORT user / WHEN validated / THEN no error"""
        user = mocker.Mock()
        user.id = 1
        user.department = Department.SUPPORT

        # Should not raise any exception
        validate_user_is_support(user)

    def test_validate_user_is_support_invalid(self, mocker):
        """GIVEN non-SUPPORT user / WHEN validated / THEN raises ValueError"""
        user = mocker.Mock()
        user.id = 1
        user.department = Department.COMMERCIAL

        with pytest.raises(ValueError) as exc_info:
            validate_user_is_support(user)
        assert "SUPPORT" in str(exc_info.value)


class TestValidateEventDates:
    """Test validate_event_dates business function."""

    def test_validate_event_dates_valid(self):
        """GIVEN valid dates / WHEN validated / THEN no error"""
        # Event in the future with valid end > start
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=2)

        validate_event_dates(event_start=start, event_end=end, attendees=50)

    def test_validate_event_dates_end_before_start(self):
        """GIVEN end <= start / WHEN validated / THEN raises ValueError"""
        start = datetime.now() + timedelta(days=1)
        end = start - timedelta(hours=1)  # End before start

        with pytest.raises(ValueError) as exc_info:
            validate_event_dates(event_start=start, event_end=end, attendees=50)
        assert "postérieure" in str(exc_info.value)

    def test_validate_event_dates_negative_attendees(self):
        """GIVEN negative attendees / WHEN validated / THEN raises ValueError"""
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=2)

        with pytest.raises(ValueError):
            validate_event_dates(event_start=start, event_end=end, attendees=-5)

    def test_validate_event_dates_in_past(self):
        """GIVEN start in past / WHEN validated / THEN raises ValueError"""
        start = datetime.now() - timedelta(days=1)  # Yesterday
        end = start + timedelta(hours=2)

        with pytest.raises(ValueError) as exc_info:
            validate_event_dates(event_start=start, event_end=end, attendees=50)
        assert "futur" in str(exc_info.value)


class TestValidateAttendeesPositive:
    """Test validate_attendees_positive business function."""

    def test_validate_attendees_positive_valid(self):
        """GIVEN positive attendees / WHEN validated / THEN no error"""
        validate_attendees_positive(0)
        validate_attendees_positive(1)
        validate_attendees_positive(100)

    def test_validate_attendees_positive_negative(self):
        """GIVEN negative attendees / WHEN validated / THEN raises ValueError"""
        with pytest.raises(ValueError):
            validate_attendees_positive(-5)
