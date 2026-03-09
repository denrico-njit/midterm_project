# Tests for InputValidator

import pytest
from decimal import Decimal
from unittest.mock import MagicMock
from app.input_validators import InputValidator
from app.exceptions import ValidationError


# Helper to create a mock config

def make_config(max_input_value=Decimal('1e999')):
    config = MagicMock()
    config.max_input_value = max_input_value
    return config


# InputValidator Tests

class TestInputValidator:

    def test_valid_string_integer(self):
        assert InputValidator.validate_number('5', make_config()) == Decimal('5')

    def test_valid_string_decimal(self):
        assert InputValidator.validate_number('3.14', make_config()) == Decimal('3.14')

    def test_valid_negative(self):
        assert InputValidator.validate_number('-7.5', make_config()) == Decimal('-7.5')

    def test_strips_whitespace(self):
        assert InputValidator.validate_number('  5  ', make_config()) == Decimal('5')

    def test_valid_decimal_input(self):
        assert InputValidator.validate_number(Decimal('2.5'), make_config()) == Decimal('2.5')

    def test_valid_integer_input(self):
        assert InputValidator.validate_number(42, make_config()) == Decimal('42')

    def test_invalid_string(self):
        with pytest.raises(ValidationError, match="Invalid number format"):
            InputValidator.validate_number('abc', make_config())

    def test_empty_string(self):
        with pytest.raises(ValidationError, match="Invalid number format"):
            InputValidator.validate_number('', make_config())

    def test_exceeds_max_value(self):
        with pytest.raises(ValidationError, match="Value exceeds maximum allowed"):
            InputValidator.validate_number('1000', make_config(max_input_value=Decimal('999')))

    def test_normalizes_result(self):
        assert InputValidator.validate_number('2.50', make_config()) == Decimal('2.5')