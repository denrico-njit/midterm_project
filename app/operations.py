from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict
from app.exceptions import ValidationError


class Operation(ABC):
    """
    Abstract base class for calculator operations.

    Outlines the structure for all operations and enforces the 
    implementation of the execute method in subclasses. 
    It also provides an interface for validation and string representation.
    """

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Perform the operation.

        Performs the arithmetic operation on the provided values.

        Args:
            a (Decimal): First value.
            b (Decimal): Second value.

        Returns:
            Decimal: Result of the operation.

        Raises:
            OperationError: If the operation fails.
        """
        pass  # pragma: no cover

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands before execution.

        Args:
            a (Decimal): First operand.
            b (Decimal): Second operand.

        Raises:
            ValidationError: If operands are invalid.
        """
        if not isinstance(a, Decimal) or not isinstance(b, Decimal):
            raise ValidationError("Operands must be Decimal instances")
        if not a.is_finite() or not b.is_finite():
            raise ValidationError("Operands must be finite numbers")

    def __str__(self) -> str:
        """
        Return operation name for display.

        Returns:
            str: Name of the operation.
        """
        return self.__class__.__name__

# Decorator for giving operations metadata for dynamically generating help info
def register_operation(name: str, description: str, usage: str):
    def decorator(cls):
        cls._help = {
            'name': name,
            'description': description,
            'usage': usage
        }
        return cls
    return decorator

@register_operation('add', 'Adds two numbers together.', 'add <number1> <number2>')
class Addition(Operation):
    """
    Addition operation implementation.

    Performs the addition of two numbers.
    """

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Add two numbers.

        Args:
            a (Decimal): First operand.
            b (Decimal): Second operand.

        Returns:
            Decimal: Sum of the two operands.
        """
        self.validate_operands(a, b)
        return a + b


@register_operation('subtract', 'Subtracts one number from another.', 'subtract <number1> <number2>')
class Subtraction(Operation):
    """
    Subtraction operation implementation.

    Performs the subtraction of one number from another.
    """

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Subtract one number from another.

        Args:
            a (Decimal): First operand.
            b (Decimal): Second operand.

        Returns:
            Decimal: Difference between the two operands.
        """
        self.validate_operands(a, b)
        return a - b


@register_operation('multiply', 'Multiplies two numbers together.', 'multiply <number1> <number2>')
class Multiplication(Operation):
    """
    Multiplication operation implementation.

    Performs the multiplication of two numbers.
    """

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Multiply two numbers.

        Args:
            a (Decimal): First operand.
            b (Decimal): Second operand.

        Returns:
            Decimal: Product of the two operands.
        """
        self.validate_operands(a, b)
        return a * b


@register_operation('divide', 'Divides one number by another.', 'divide <number1> <number2>')
class Division(Operation):
    """
    Division operation implementation.

    Performs the division of one number by another.
    """

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands, checking for division by zero.

        Overrides the base class method to ensure that the divisor is not zero.

        Args:
            a (Decimal): Dividend.
            b (Decimal): Divisor.

        Raises:
            ValidationError: If the divisor is zero.
        """
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Division by zero is not allowed")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Divide one number by another.

        Args:
            a (Decimal): Dividend.
            b (Decimal): Divisor.

        Returns:
            Decimal: Quotient of the division.
        """
        self.validate_operands(a, b)
        return a / b


@register_operation('int_divide', 'Performs integer division of one number by another. Truncates towards zero.', 'int_divide <number1> <number2>')
class IntegerDivision(Operation):
    """
    Integer division operation implementation.

    Performs the integer division of one number by another.
    """

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands, checking for division by zero.

        Overrides the base class method to ensure that the divisor is not zero.

        Args:
            a (Decimal): Dividend.
            b (Decimal): Divisor.
        
        Raises:
            ValidationError: If the divisor is zero.
        """
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Division by zero is not allowed")
    
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Perform integer division of one number by another.

        Args:
            a (Decimal): Dividend.
            b (Decimal): Divisor.

        Returns:
            Decimal: Result of the integer division.
        """
        self.validate_operands(a, b)
        return a // b


@register_operation('modulo', 'Calculates the remainder of the division of one number by another.', 'modulo <number1> <number2>')
class Modulo(Operation):
    """
    Modulo operation implementation.

    Performs the modulo operation, returning the remainder of the division of one number by another.
    """

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands, checking for division by zero.

        Overrides the base class method to ensure that the divisor is not zero.

        Args:
            a (Decimal): Dividend.
            b (Decimal): Divisor
        
        Raises:
            ValidationError: If the divisor is zero.
        """
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Division by zero is not allowed")
    
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Perform the modulo operation.

        Args:
            a (Decimal): Dividend.
            b (Decimal): Divisor.

        Returns:
            Decimal: Remainder of the division.
        """
        self.validate_operands(a, b)
        return a % b
    

@register_operation('power', 'Raises one number to the power of another.', 'power <base> <exponent>')
class Power(Operation):
    """
    Power (exponentiation) operation implementation.

    Raises one number to the power of another.
    """

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands for power operation.

        Overrides the base class method to ensure that the exponent is not negative.

        Args:
            a (Decimal): Base number.
            b (Decimal): Exponent.

        Raises:
            ValidationError: If the base is zero and the exponent is negative.
        """
        super().validate_operands(a, b)
        if a == 0 and b < 0:
            raise ValidationError("Zero cannot be raised to a negative power")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Calculate one number raised to the power of another.

        Args:
            a (Decimal): Base number.
            b (Decimal): Exponent.

        Returns:
            Decimal: Result of the exponentiation.
        """
        self.validate_operands(a, b)
        return a ** b


@register_operation('percentage', 'Calculates the percentage of one number with respect to another.', 'percentage <part> <whole>')
class Percentage(Operation):
    """
    Percentage operation implementation.

    Calculates the percentage of one number with respect to another.
    """
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands for percentage operation.
        Overrides the base class method to ensure that the whole value is not zero.
        Args:
            a (Decimal): The part value.
            b (Decimal): The whole value.

        Raises:
            ValidationError: If the whole value is zero.
        """
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Whole value cannot be zero for percentage calculation")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Calculate the percentage of one number with respect to another.

        Args:
            a (Decimal): The part value.
            b (Decimal): The whole value.

        Returns:
            Decimal: The percentage of a with respect to b.
        """
        self.validate_operands(a, b)
        return (a / b) * Decimal(100)


@register_operation('abs_difference', 'Calculates the absolute difference between two numbers.', 'abs_difference <number1> <number2>')
class AbsoluteDifference(Operation):
    """
    Absolute difference operation implementation.

    Calculates the absolute difference between two numbers.
    """

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Calculate the absolute difference between two numbers.

        Args:
            a (Decimal): First operand.
            b (Decimal): Second operand.

        Returns:
            Decimal: Absolute difference between the two operands.
        """
        self.validate_operands(a, b)
        return abs(a - b)
    

@register_operation('root', 'Calculates the nth root of a number.', 'root <number> <degree>')
class Root(Operation):
    """
    Root operation implementation.

    Calculates the nth root of a number.
    """

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands for root operation.

        Overrides the base class method to ensure that the number is non-negative
        and the root degree is not zero.

        Args:
            a (Decimal): Number from which the root is taken.
            b (Decimal): Degree of the root.

        Raises:
            ValidationError: If the number is negative or the root degree is zero.
        """
        super().validate_operands(a, b)
        if a < 0:
            raise ValidationError("Cannot calculate root of negative number")
        if b == 0:
            raise ValidationError("Zero root is undefined")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Calculate the nth root of a number.

        Args:
            a (Decimal): Number from which the root is taken.
            b (Decimal): Degree of the root.

        Returns:
            Decimal: Result of the root calculation.
        """
        self.validate_operands(a, b)
        return a ** (Decimal(1) / b)


class OperationFactory:
    """
    Factory class for creating operation instances.

    Implements the Factory pattern by providing a method to instantiate
    different operation classes based on a given operation type. This promotes
    scalability and decouples the creation logic from the Calculator class.
    """

    # Dictionary mapping operation identifiers to their corresponding classes
    _operations: Dict[str, type] = {
        'add': Addition,
        'subtract': Subtraction,
        'multiply': Multiplication,
        'divide': Division,
        'int_divide': IntegerDivision,
        'abs_difference': AbsoluteDifference,
        'modulo': Modulo,
        'percentage': Percentage,
        'power': Power,
        'root': Root
    }

    @classmethod
    def register_operation(cls, name: str, operation_class: type) -> None:
        """
        Register a new operation type.

        Allows dynamic addition of new operations to the factory.

        Args:
            name (str): Operation identifier (e.g., 'modulus').
            operation_class (type): The class implementing the new operation.

        Raises:
            TypeError: If the operation_class does not inherit from Operation.
        """
        if not issubclass(operation_class, Operation):
            raise TypeError("Operation class must inherit from Operation")
        cls._operations[name.lower()] = operation_class

    @classmethod
    def create_operation(cls, operation_type: str) -> Operation:
        """
        Create an operation instance based on the operation type.

        This method retrieves the appropriate operation class from the
        _operations dictionary and instantiates it.

        Args:
            operation_type (str): The type of operation to create (e.g., 'add').

        Returns:
            Operation: An instance of the specified operation class.

        Raises:
            ValueError: If the operation type is unknown.
        """
        operation_class = cls._operations.get(operation_type.lower())
        if not operation_class:
            raise ValueError(f"Unknown operation: {operation_type}")
        return operation_class()