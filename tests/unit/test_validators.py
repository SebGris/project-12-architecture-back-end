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
"""

import pytest
import typer
from src.cli.validators import (
    validate_email_callback,
    validate_phone_callback,
    validate_password_callback,
    validate_first_name_callback,
    validate_last_name_callback,
    validate_location_callback,
    validate_attendees_callback,
)


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
