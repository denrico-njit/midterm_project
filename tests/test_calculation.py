# Tests for Calculation

import pytest
import datetime
from decimal import Decimal
from app.calculation import Calculation
from app.exceptions import OperationError


# Testing Calculation creation and properties

class TestCalculationInstantiation:

    def test_basic_instantiation(self):
        calc = Calculation(
            operation='Addition',
            operand1=Decimal('2'),
            operand2=Decimal('3'),
            result=Decimal('5')
        )
        assert calc.operation == 'Addition'
        assert calc.operand1 == Decimal('2')
        assert calc.operand2 == Decimal('3')
        assert calc.result == Decimal('5')

    def test_timestamp_defaults_to_now(self):
        before = datetime.datetime.now()
        calc = Calculation('Addition', Decimal('1'), Decimal('2'), Decimal('3'))
        after = datetime.datetime.now()
        assert before <= calc.timestamp <= after

    def test_timestamp_can_be_set_explicitly(self):
        ts = datetime.datetime(2024, 1, 1, 12, 0, 0)
        calc = Calculation('Addition', Decimal('1'), Decimal('2'), Decimal('3'), timestamp=ts)
        assert calc.timestamp == ts


# Equality Tests

class TestCalculationEquality:

    def test_equal_calculations(self):
        a = Calculation('Addition', Decimal('2'), Decimal('3'), Decimal('5'))
        b = Calculation('Addition', Decimal('2'), Decimal('3'), Decimal('5'))
        assert a == b

    def test_different_operation(self):
        a = Calculation('Addition', Decimal('2'), Decimal('3'), Decimal('5'))
        b = Calculation('Subtraction', Decimal('2'), Decimal('3'), Decimal('5'))
        assert a != b

    def test_different_operands(self):
        a = Calculation('Addition', Decimal('2'), Decimal('3'), Decimal('5'))
        b = Calculation('Addition', Decimal('1'), Decimal('4'), Decimal('5'))
        assert a != b

    def test_different_result(self):
        a = Calculation('Addition', Decimal('2'), Decimal('3'), Decimal('5'))
        b = Calculation('Addition', Decimal('2'), Decimal('3'), Decimal('6'))
        assert a != b

    def test_not_equal_to_non_calculation(self):
        calc = Calculation('Addition', Decimal('2'), Decimal('3'), Decimal('5'))
        assert calc.__eq__("not a calculation") == NotImplemented


# Serialization Tests

class TestCalculationSerialization:

    def test_to_dict(self):
        ts = datetime.datetime(2024, 1, 1, 12, 0, 0)
        calc = Calculation('Addition', Decimal('2'), Decimal('3'), Decimal('5'), timestamp=ts)
        d = calc.to_dict()
        assert d['operation'] == 'Addition'
        assert d['operand1'] == '2'
        assert d['operand2'] == '3'
        assert d['result'] == '5'
        assert d['timestamp'] == '2024-01-01T12:00:00'

    def test_from_dict(self):
        data = {
            'operation': 'Addition',
            'operand1': '2',
            'operand2': '3',
            'result': '5',
            'timestamp': '2024-01-01T12:00:00'
        }
        calc = Calculation.from_dict(data)
        assert calc.operation == 'Addition'
        assert calc.operand1 == Decimal('2')
        assert calc.operand2 == Decimal('3')
        assert calc.result == Decimal('5')
        assert calc.timestamp == datetime.datetime(2024, 1, 1, 12, 0, 0)

    def test_round_trip(self):
        original = Calculation('Addition', Decimal('2'), Decimal('3'), Decimal('5'))
        restored = Calculation.from_dict(original.to_dict())
        assert original == restored

    def test_from_dict_missing_key(self):
        with pytest.raises(OperationError, match="Invalid calculation data"):
            Calculation.from_dict({'operation': 'Addition'})

    def test_from_dict_invalid_decimal(self):
        with pytest.raises(OperationError, match="Invalid calculation data"):
            Calculation.from_dict({
                'operation': 'Addition',
                'operand1': 'not_a_number',
                'operand2': '3',
                'result': '5',
                'timestamp': '2024-01-01T12:00:00'
            })


# format_result Tests

class TestFormatResult:

    def test_format_result_no_precision(self):
        calc = Calculation('Addition', Decimal('2.50'), Decimal('0'), Decimal('2.50'))
        assert calc.format_result() == '2.5'

    def test_format_result_with_precision(self):
        calc = Calculation('Division', Decimal('1'), Decimal('3'), Decimal('0.3333333333'))
        assert calc.format_result(2) == '0.33'

    def test_format_result_whole_number(self):
        calc = Calculation('Addition', Decimal('2'), Decimal('3'), Decimal('5'))
        assert calc.format_result() == '5'

    def test_format_result_strips_trailing_zeros(self):
        calc = Calculation('Multiplication', Decimal('1.5'), Decimal('2'), Decimal('3.0'))
        assert calc.format_result() == '3'