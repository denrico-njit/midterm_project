# Input validation module for the calculator application

from decimal import Decimal, InvalidOperation
from typing import Any

from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError


class InputValidator:
    """Validates and sanitizes calculator inputs."""

    @staticmethod
    def validate_number(value: Any, config: CalculatorConfig) -> Decimal:
        """
        Validate and convert input to Decimal.

        Args:
            value (Any): Input value to validate.
            config (CalculatorConfig): Calculator configuration.

        Returns:
            Decimal: Validated and converted number.

        Raises:
            ValidationError: If input is invalid.
        """
        try:
            if isinstance(value, str):
                value = value.strip()
            number = Decimal(str(value))
            if abs(number) > config.max_input_value:
                raise ValidationError(f"Value exceeds maximum allowed: {config.max_input_value}")
            return number.normalize()
        except InvalidOperation as e:
            raise ValidationError(f"Invalid number format: {value}") from e