# Tests for Calculator

import pytest
import logging
from decimal import Decimal
from unittest.mock import MagicMock, patch
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculation import Calculation
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver


# Helper to create a test config

def make_config(tmp_path):
    return CalculatorConfig(base_dir=tmp_path)


# Initialization Tests

class TestCalculatorInit:

    def test_initializes_with_config(self, tmp_path):
        config = make_config(tmp_path)
        calc = Calculator(config=config)
        assert calc.config is config

    def test_initializes_with_empty_history(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        assert calc.history == []

    def test_initializes_with_empty_stacks(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        assert calc.undo_stack == []
        assert calc.redo_stack == []

    def test_initializes_with_no_observers(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        assert calc.observers == []

    def test_creates_history_directory(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        assert calc.config.history_dir.exists()

    def test_creates_log_directory(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        assert calc.config.log_dir.exists()

    def test_default_config_when_none_provided(self, tmp_path):
        with patch('app.calculator.CalculatorConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config.log_dir = tmp_path / 'logs'
            mock_config.log_file = tmp_path / 'logs' / 'calculator.log'
            mock_config.history_dir = tmp_path / 'history'
            mock_config.history_file = tmp_path / 'history' / 'calculator_history.csv'
            mock_config.max_history_size = 1000
            mock_config.auto_save = False
            mock_config_class.return_value = mock_config
            calc = Calculator()
            assert calc.config is mock_config

    def test_setup_logging_failure_raises(self, tmp_path):
        config = make_config(tmp_path)
        with patch('logging.basicConfig', side_effect=Exception("logging failed")):
            with pytest.raises(Exception, match="logging failed"):
                Calculator(config=config)

# Observer Tests

class TestCalculatorObservers:

    def test_add_observer(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        observer = MagicMock()
        calc.add_observer(observer)
        assert observer in calc.observers

    def test_remove_observer(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        observer = MagicMock()
        calc.add_observer(observer)
        calc.remove_observer(observer)
        assert observer not in calc.observers

    def test_notify_observers(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        observer = MagicMock()
        calc.add_observer(observer)
        calculation = Calculation('Addition', Decimal('2'), Decimal('3'), Decimal('5'))
        calc.notify_observers(calculation)
        observer.update.assert_called_once_with(calculation)

    def test_multiple_observers_notified(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        observer1 = MagicMock()
        observer2 = MagicMock()
        calc.add_observer(observer1)
        calc.add_observer(observer2)
        calculation = Calculation('Addition', Decimal('2'), Decimal('3'), Decimal('5'))
        calc.notify_observers(calculation)
        observer1.update.assert_called_once_with(calculation)
        observer2.update.assert_called_once_with(calculation)


# Calculate Tests

class TestCalculatorCalculate:

    def test_basic_addition(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        result = calc.calculate('add', '2', '3')
        assert result == Decimal('5')

    def test_basic_subtraction(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        assert calc.calculate('subtract', '5', '3') == Decimal('2')

    def test_basic_multiplication(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        assert calc.calculate('multiply', '3', '4') == Decimal('12')

    def test_basic_division(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        assert calc.calculate('divide', '10', '2') == Decimal('5')

    def test_division_by_zero(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        with pytest.raises(ValidationError):
            calc.calculate('divide', '10', '0')

    def test_invalid_operation(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        with pytest.raises(ValueError):
            calc.calculate('unknown', '2', '3')

    def test_invalid_input(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        with pytest.raises(ValidationError):
            calc.calculate('add', 'abc', '3')

    def test_result_added_to_history(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        calc.calculate('add', '2', '3')
        assert len(calc.history) == 1
        assert calc.history[0].result == Decimal('5')

    def test_no_operation_set_raises(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        with pytest.raises(OperationError, match="No operation set"):
            calc.perform_operation('2', '3')

    def test_history_capped_at_max_size(self, tmp_path):
        config = make_config(tmp_path)
        config.max_history_size = 3
        calc = Calculator(config=config)
        for i in range(5):
            calc.calculate('add', str(i), '1')
        assert len(calc.history) == 3


# History Management Tests

class TestCalculatorHistory:

    def test_show_history_empty(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        assert calc.show_history() == []

    def test_show_history_after_calculation(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        calc.calculate('add', '2', '3')
        history = calc.show_history()
        assert len(history) == 1
        assert 'Addition' in history[0]

    def test_clear_history(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        calc.calculate('add', '2', '3')
        calc.clear_history()
        assert calc.history == []
        assert calc.undo_stack == []
        assert calc.redo_stack == []

    def test_save_and_load_history(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        calc.calculate('add', '2', '3')
        calc.save_history()
        calc.history.clear()
        calc.load_history()
        assert len(calc.history) == 1
        assert calc.history[0].result == Decimal('5')

    def test_save_empty_history(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        calc.save_history()
        assert calc.config.history_file.exists()
    
    def test_load_empty_history_file(self, tmp_path):
        config = make_config(tmp_path)
        calc = Calculator(config=config)
        # Save empty history to create the file
        calc.save_history()
        # Clear and reload
        calc.history.clear()
        calc.load_history()
        assert calc.history == []

    def test_load_nonexistent_history(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        calc.load_history()  # should not raise
        assert calc.history == []

    def test_get_history_dataframe(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        calc.calculate('add', '2', '3')
        df = calc.get_history_dataframe()
        assert len(df) == 1
        assert 'operation' in df.columns
        assert 'result' in df.columns

    def test_init_handles_load_history_failure(self, tmp_path):
        config = make_config(tmp_path)
        with patch('app.calculator.Calculator.load_history', side_effect=Exception("load failed")):
            calc = Calculator(config=config)
            assert calc.history == []

# Undo/Redo Tests

class TestCalculatorUndoRedo:

    def test_undo_last_operation(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        calc.calculate('add', '2', '3')
        calc.undo()
        assert calc.history == []

    def test_undo_empty_stack_returns_false(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        assert calc.undo() == False

    def test_redo_after_undo(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        calc.calculate('add', '2', '3')
        calc.undo()
        calc.redo()
        assert len(calc.history) == 1

    def test_redo_empty_stack_returns_false(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        assert calc.redo() == False

    def test_new_operation_clears_redo_stack(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        calc.calculate('add', '2', '3')
        calc.undo()
        calc.calculate('add', '4', '5')
        assert calc.redo_stack == []

    def test_multiple_undos(self, tmp_path):
        calc = Calculator(config=make_config(tmp_path))
        calc.calculate('add', '2', '3')
        calc.calculate('add', '4', '5')
        calc.undo()
        calc.undo()
        assert calc.history == []