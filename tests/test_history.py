# Tests for History Observers

import pytest
import logging
from decimal import Decimal
from unittest.mock import MagicMock
from app.calculation import Calculation
# Uncomment when Calculator is implemented
# Then add spec=Calculator to MagicMock() calls
# from app.calculator import Calculator

from app.history import HistoryObserver, LoggingObserver, AutoSaveObserver


# Helper to create a sample calculation

def make_calculation():
    return Calculation(
        operation='Addition',
        operand1=Decimal('2'),
        operand2=Decimal('3'),
        result=Decimal('5')
    )


# HistoryObserver Tests

class TestHistoryObserver:

    def test_cannot_instantiate_abstract_class(self):
        with pytest.raises(TypeError):
            HistoryObserver()


# LoggingObserver Tests

class TestLoggingObserver:

    def test_update_logs_calculation(self, caplog):
        observer = LoggingObserver()
        calc = make_calculation()
        with caplog.at_level(logging.INFO):
            observer.update(calc)
        assert 'Addition' in caplog.text
        assert '2' in caplog.text
        assert '3' in caplog.text
        assert '5' in caplog.text


# AutoSaveObserver Tests

class TestAutoSaveObserver:

    def test_rejects_invalid_calculator(self):
        with pytest.raises(TypeError):
            AutoSaveObserver(object())

    def test_auto_save_triggered_when_enabled(self):
        mock_calc = MagicMock()
        mock_calc.config.auto_save = True
        observer = AutoSaveObserver(mock_calc)
        observer.update(make_calculation())
        mock_calc.save_history.assert_called_once()

    def test_auto_save_not_triggered_when_disabled(self):
        mock_calc = MagicMock()
        mock_calc.config.auto_save = False
        observer = AutoSaveObserver(mock_calc)
        observer.update(make_calculation())
        mock_calc.save_history.assert_not_called()

    def test_stores_calculator_reference(self):
        mock_calc = MagicMock()
        observer = AutoSaveObserver(mock_calc)
        assert observer.calculator is mock_calc