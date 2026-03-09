# Tests for operations

import pytest
from decimal import Decimal
from app.exceptions import ValidationError
from app.operations import (
    Addition, Subtraction, Multiplication, Division,
    FloorDivision, Modulo, Power, Percentage,
    AbsoluteDifference, Root, OperationFactory
)


# Base Validation Tests

class TestBaseValidation:

    def test_rejects_non_decimal_first_operand(self):
        with pytest.raises(ValidationError, match="Operands must be Decimal instances"):
            Addition().validate_operands(1.5, Decimal('2'))

    def test_rejects_non_decimal_second_operand(self):
        with pytest.raises(ValidationError, match="Operands must be Decimal instances"):
            Addition().validate_operands(Decimal('1'), 2.5)

    def test_rejects_infinity(self):
        with pytest.raises(ValidationError, match="Operands must be finite numbers"):
            Addition().validate_operands(Decimal('Infinity'), Decimal('1'))

    def test_rejects_negative_infinity(self):
        with pytest.raises(ValidationError, match="Operands must be finite numbers"):
            Addition().validate_operands(Decimal('1'), Decimal('-Infinity'))

    def test_rejects_nan(self):
        with pytest.raises(ValidationError, match="Operands must be finite numbers"):
            Addition().validate_operands(Decimal('NaN'), Decimal('1'))

    def test_accepts_valid_decimals(self):
        Addition().validate_operands(Decimal('1'), Decimal('2'))


# Addition Tests

class TestAddition:

    def test_add_positive_numbers(self):
        assert Addition().execute(Decimal('2'), Decimal('3')) == Decimal('5')

    def test_add_negative_numbers(self):
        assert Addition().execute(Decimal('-2'), Decimal('-3')) == Decimal('-5')

    def test_add_mixed_sign(self):
        assert Addition().execute(Decimal('-2'), Decimal('3')) == Decimal('1')

    def test_add_decimals(self):
        assert Addition().execute(Decimal('1.5'), Decimal('2.5')) == Decimal('4.0')

    def test_add_zero(self):
        assert Addition().execute(Decimal('5'), Decimal('0')) == Decimal('5')


# Subtraction Tests

class TestSubtraction:

    def test_subtract_positive_numbers(self):
        assert Subtraction().execute(Decimal('5'), Decimal('3')) == Decimal('2')

    def test_subtract_negative_numbers(self):
        assert Subtraction().execute(Decimal('-5'), Decimal('-3')) == Decimal('-2')

    def test_subtract_to_negative(self):
        assert Subtraction().execute(Decimal('3'), Decimal('5')) == Decimal('-2')

    def test_subtract_zero(self):
        assert Subtraction().execute(Decimal('5'), Decimal('0')) == Decimal('5')


# Multiplication Tests

class TestMultiplication:

    def test_multiply_positive_numbers(self):
        assert Multiplication().execute(Decimal('3'), Decimal('4')) == Decimal('12')

    def test_multiply_negative_numbers(self):
        assert Multiplication().execute(Decimal('-3'), Decimal('-4')) == Decimal('12')

    def test_multiply_mixed_sign(self):
        assert Multiplication().execute(Decimal('-3'), Decimal('4')) == Decimal('-12')

    def test_multiply_by_zero(self):
        assert Multiplication().execute(Decimal('5'), Decimal('0')) == Decimal('0')

    def test_multiply_decimals(self):
        assert Multiplication().execute(Decimal('1.5'), Decimal('2')) == Decimal('3.0')


# Division Tests

class TestDivision:

    def test_divide_positive_numbers(self):
        assert Division().execute(Decimal('10'), Decimal('2')) == Decimal('5')

    def test_divide_negative_numbers(self):
        assert Division().execute(Decimal('-10'), Decimal('-2')) == Decimal('5')

    def test_divide_mixed_sign(self):
        assert Division().execute(Decimal('-10'), Decimal('2')) == Decimal('-5')

    def test_divide_by_zero(self):
        with pytest.raises(ValidationError, match="Division by zero is not allowed"):
            Division().execute(Decimal('10'), Decimal('0'))

    def test_divide_decimals(self):
        assert Division().execute(Decimal('1'), Decimal('4')) == Decimal('0.25')


# FloorDivision Tests

class TestFloorDivision:

    def test_floor_divide_positive_numbers(self):
        assert FloorDivision().execute(Decimal('10'), Decimal('3')) == Decimal('3')

    def test_floor_divide_negative_numbers(self):
        assert FloorDivision().execute(Decimal('-10'), Decimal('3')) == Decimal('-4')

    def test_floor_divide_by_zero(self):
        with pytest.raises(ValidationError, match="Division by zero is not allowed"):
            FloorDivision().execute(Decimal('10'), Decimal('0'))


# Modulo Tests

class TestModulo:

    def test_modulo_positive_numbers(self):
        assert Modulo().execute(Decimal('10'), Decimal('3')) == Decimal('1')

    def test_modulo_by_zero(self):
        with pytest.raises(ValidationError, match="Division by zero is not allowed"):
            Modulo().execute(Decimal('10'), Decimal('0'))

    def test_modulo_even_division(self):
        assert Modulo().execute(Decimal('10'), Decimal('5')) == Decimal('0')


# Power Tests

class TestPower:

    def test_power_positive_exponent(self):
        assert Power().execute(Decimal('2'), Decimal('3')) == Decimal('8')

    def test_power_zero_exponent(self):
        assert Power().execute(Decimal('5'), Decimal('0')) == Decimal('1')

    def test_power_negative_exponent(self):
        assert Power().execute(Decimal('2'), Decimal('-1')) == Decimal('0.5')

    def test_power_zero_base_negative_exponent(self):
        with pytest.raises(ValidationError, match="Zero cannot be raised to a negative power"):
            Power().execute(Decimal('0'), Decimal('-1'))

    def test_power_fractional_exponent(self):
        assert Power().execute(Decimal('4'), Decimal('0.5')) == Decimal('2')


# Percentage Tests

class TestPercentage:

    def test_percentage_basic(self):
        assert Percentage().execute(Decimal('50'), Decimal('200')) == Decimal('25')

    def test_percentage_whole_zero(self):
        with pytest.raises(ValidationError, match="Whole value cannot be zero"):
            Percentage().execute(Decimal('50'), Decimal('0'))

    def test_percentage_full(self):
        assert Percentage().execute(Decimal('100'), Decimal('100')) == Decimal('100')


# AbsoluteDifference Tests

class TestAbsoluteDifference:

    def test_absolute_difference_positive(self):
        assert AbsoluteDifference().execute(Decimal('10'), Decimal('3')) == Decimal('7')

    def test_absolute_difference_reversed(self):
        assert AbsoluteDifference().execute(Decimal('3'), Decimal('10')) == Decimal('7')

    def test_absolute_difference_negative_numbers(self):
        assert AbsoluteDifference().execute(Decimal('-3'), Decimal('-10')) == Decimal('7')

    def test_absolute_difference_equal_numbers(self):
        assert AbsoluteDifference().execute(Decimal('5'), Decimal('5')) == Decimal('0')


# Root Tests

class TestRoot:

    def test_square_root(self):
        assert Root().execute(Decimal('9'), Decimal('2')) == Decimal('3')

    def test_cube_root(self):
        result = Root().execute(Decimal('27'), Decimal('3'))
        assert abs(result - Decimal('3')) < Decimal('0.0000001')

    def test_root_of_negative_number(self):
        with pytest.raises(ValidationError, match="Cannot calculate root of negative number"):
            Root().execute(Decimal('-9'), Decimal('2'))

    def test_zero_root(self):
        with pytest.raises(ValidationError, match="Zero root is undefined"):
            Root().execute(Decimal('9'), Decimal('0'))

    def test_root_of_zero(self):
        assert Root().execute(Decimal('0'), Decimal('2')) == Decimal('0')


# OperationFactory Tests

class TestOperationFactory:

    def test_create_addition(self):
        assert isinstance(OperationFactory.create_operation('add'), Addition)

    def test_create_subtraction(self):
        assert isinstance(OperationFactory.create_operation('subtract'), Subtraction)

    def test_create_multiplication(self):
        assert isinstance(OperationFactory.create_operation('multiply'), Multiplication)

    def test_create_division(self):
        assert isinstance(OperationFactory.create_operation('divide'), Division)

    def test_create_floor_division(self):
        assert isinstance(OperationFactory.create_operation('int_divide'), FloorDivision)

    def test_create_modulo(self):
        assert isinstance(OperationFactory.create_operation('modulo'), Modulo)

    def test_create_percentage(self):
        assert isinstance(OperationFactory.create_operation('percentage'), Percentage)

    def test_create_power(self):
        assert isinstance(OperationFactory.create_operation('power'), Power)

    def test_create_root(self):
        assert isinstance(OperationFactory.create_operation('root'), Root)

    def test_create_abs_difference(self):
        assert isinstance(OperationFactory.create_operation('abs_difference'), AbsoluteDifference)

    def test_unknown_operation(self):
        with pytest.raises(ValueError, match="Unknown operation"):
            OperationFactory.create_operation('unknown')

    def test_case_insensitive(self):
        assert isinstance(OperationFactory.create_operation('ADD'), Addition)

    def test_register_new_operation(self):
        class Square(Addition):
            pass
        OperationFactory.register_operation('square', Square)
        assert isinstance(OperationFactory.create_operation('square'), Square)

    def test_register_invalid_operation(self):
        with pytest.raises(TypeError):
            OperationFactory.register_operation('bad', str)