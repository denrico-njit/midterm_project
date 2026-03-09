# Calculation Object for the calculator application.

from dataclasses import dataclass, field
import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from app.exceptions import OperationError


@dataclass
class Calculation:
    """
    Calculation object representing a single calculation.

    Encapsulates the details of a mathematical calculation, including the
    operation performed, operands involved, the result, and the timestamp.
    The result is computed externally and passed in, keeping this class
    as a pure value object.
    """

    operation: str
    operand1: Decimal
    operand2: Decimal
    result: Decimal
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert calculation to dictionary for serialization.

        Returns:
            Dict[str, Any]: A dictionary containing the calculation data.
        """
        return {
            'operation': self.operation,
            'operand1': str(self.operand1),
            'operand2': str(self.operand2),
            'result': str(self.result),
            'timestamp': self.timestamp.isoformat()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Calculation':
        """
        Create a Calculation instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary containing calculation data.

        Returns:
            Calculation: A new Calculation instance.

        Raises:
            OperationError: If data is invalid or missing required fields.
        """
        try:
            return Calculation(
                operation=data['operation'],
                operand1=Decimal(data['operand1']),
                operand2=Decimal(data['operand2']),
                result=Decimal(data['result']),
                timestamp=datetime.datetime.fromisoformat(data['timestamp'])
            )
        except (KeyError, InvalidOperation, ValueError) as e:
            raise OperationError(f"Invalid calculation data: {str(e)}")

    def __str__(self) -> str:  # pragma: no cover
        """
        Return string representation of calculation.

        Returns:
            str: Formatted string showing the calculation and result.
        """
        return f"{self.operation}({self.operand1}, {self.operand2}) = {self.result}"

    def __repr__(self) -> str:  # pragma: no cover
        """
        Return detailed string representation of calculation.

        Returns:
            str: Detailed string showing all calculation attributes.
        """
        return (
            f"Calculation(operation='{self.operation}', "
            f"operand1={self.operand1}, "
            f"operand2={self.operand2}, "
            f"result={self.result}, "
            f"timestamp='{self.timestamp.isoformat()}')"
        )

    def __eq__(self, other: object) -> bool:
        """
        Check equality between two Calculation instances.

        Args:
            other (object): Another calculation to compare with.

        Returns:
            bool: True if calculations are equal, False otherwise.
        """
        if not isinstance(other, Calculation):
            return NotImplemented
        return (
            self.operation == other.operation and
            self.operand1 == other.operand1 and
            self.operand2 == other.operand2 and
            self.result == other.result
        )

    def format_result(self, precision: Optional[int] = None) -> str:
        if precision is None:
            return str(self.result.normalize())
        return str(self.result.quantize(Decimal('0.' + '0' * precision)).normalize())