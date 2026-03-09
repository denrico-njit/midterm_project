# Tests for CalculatorMemento

import pytest
import datetime
from decimal import Decimal
from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento


# Helper to create sample calculations

def make_calculation(op='Addition', a='2', b='3', result='5'):
    return Calculation(
        operation=op,
        operand1=Decimal(a),
        operand2=Decimal(b),
        result=Decimal(result)
    )


# CalculatorMemento Tests

class TestCalculatorMemento:

    def test_basic_instantiation(self):
        history = [make_calculation()]
        memento = CalculatorMemento(history=history)
        assert memento.history == history

    def test_timestamp_defaults_to_now(self):
        before = datetime.datetime.now()
        memento = CalculatorMemento(history=[])
        after = datetime.datetime.now()
        assert before <= memento.timestamp <= after

    def test_empty_history(self):
        memento = CalculatorMemento(history=[])
        assert memento.history == []

    def test_to_dict(self):
        ts = datetime.datetime(2024, 1, 1, 12, 0, 0)
        memento = CalculatorMemento(history=[make_calculation()], timestamp=ts)
        d = memento.to_dict()
        assert d['timestamp'] == '2024-01-01T12:00:00'
        assert len(d['history']) == 1
        assert d['history'][0]['operation'] == 'Addition'

    def test_from_dict(self):
        ts = datetime.datetime(2024, 1, 1, 12, 0, 0)
        original = CalculatorMemento(history=[make_calculation()], timestamp=ts)
        restored = CalculatorMemento.from_dict(original.to_dict())
        assert restored.timestamp == ts
        assert len(restored.history) == 1
        assert restored.history[0].operation == 'Addition'

    def test_round_trip(self):
        original = CalculatorMemento(history=[make_calculation(), make_calculation('Subtraction', '5', '3', '2')])
        restored = CalculatorMemento.from_dict(original.to_dict())
        assert len(restored.history) == len(original.history)
        assert restored.history[0] == original.history[0]
        assert restored.history[1] == original.history[1]