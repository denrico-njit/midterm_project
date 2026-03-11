import pytest

from decimal import Decimal
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculator_repl import calculator_repl


# Fixture to provide a temporary configuration for testing

@pytest.fixture
def temp_config(tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    with patch('app.calculator_repl.Calculator', return_value=Calculator(config=config)), \
         patch('app.display.Fore.GREEN', ''), \
         patch('app.display.Fore.YELLOW', ''), \
         patch('app.display.Fore.RED', ''):
        yield config


# Exit

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_repl_exit(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("Exiting...")


# Help

@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_repl_help(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("\nAvailable commands:")


# Arithmetic operations

@patch('builtins.input', side_effect=['add', '10', '5', 'exit'])
@patch('builtins.print')
def test_repl_add(mock_print, mock_input, temp_config):
    calculator_repl()
    print(mock_print.call_args_list)  # this will go to real print since mock_print is the mock
    mock_print.assert_any_call("\nResult: 15")

@patch('builtins.input', side_effect=['subtract', '10', '4', 'exit'])
@patch('builtins.print')
def test_repl_subtract(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 6")

@patch('builtins.input', side_effect=['multiply', '3', '7', 'exit'])
@patch('builtins.print')
def test_repl_multiply(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 21")

@patch('builtins.input', side_effect=['divide', '20', '4', 'exit'])
@patch('builtins.print')
def test_repl_divide(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 5")

@patch('builtins.input', side_effect=['power', '2', '8', 'exit'])
@patch('builtins.print')
def test_repl_power(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 256")

@patch('builtins.input', side_effect=['root', '27', '3', 'exit'])
@patch('builtins.print')
def test_repl_root(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 3")

@patch('builtins.input', side_effect=['int_divide', '10', '3', 'exit'])
@patch('builtins.print')
def test_repl_int_divide(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 3")

@patch('builtins.input', side_effect=['modulo', '10', '3', 'exit'])
@patch('builtins.print')
def test_repl_modulo(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 1")

@patch('builtins.input', side_effect=['percentage', '50', '200', 'exit'])
@patch('builtins.print')
def test_repl_percentage(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 25")

@patch('builtins.input', side_effect=['abs_difference', '3', '10', 'exit'])
@patch('builtins.print')
def test_repl_abs_difference(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 7")


# Cancel during operation

@patch('builtins.input', side_effect=['add', 'cancel', 'exit'])
@patch('builtins.print')
def test_repl_cancel_first_number(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("Operation cancelled")

@patch('builtins.input', side_effect=['add', '5', 'cancel', 'exit'])
@patch('builtins.print')
def test_repl_cancel_second_number(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("Operation cancelled")


# Validation and operation errors

@patch('builtins.input', side_effect=['add', 'abc', '3', 'exit'])
@patch('builtins.print')
def test_repl_invalid_input(mock_print, mock_input, temp_config):
    calculator_repl()
    printed = [str(call) for call in mock_print.call_args_list]
    assert any("Error" in p for p in printed)

@patch('builtins.input', side_effect=['divide', '10', '0', 'exit'])
@patch('builtins.print')
def test_repl_division_by_zero(mock_print, mock_input, temp_config):
    calculator_repl()
    printed = [str(call) for call in mock_print.call_args_list]
    assert any("Error" in p for p in printed)


# History

@patch('builtins.input', side_effect=['history', 'exit'])
@patch('builtins.print')
def test_repl_history_empty(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("No available history.")

@patch('builtins.input', side_effect=['add', '2', '3', 'history', 'exit'])
@patch('builtins.print')
def test_repl_history_with_entries(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("\nCalculation History:")

@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_repl_unexpected_operation_error(mock_print, mock_input, tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    calc_instance = Calculator(config=config)
    calc_instance.perform_operation = MagicMock(side_effect=Exception("unexpected"))
    with patch('app.calculator_repl.Calculator', return_value=calc_instance), \
         patch('app.display.Fore.GREEN', ''), \
         patch('app.display.Fore.YELLOW', ''), \
         patch('app.display.Fore.RED', ''):
        calculator_repl()
        mock_print.assert_any_call("Unexpected error: unexpected")


# Clear

@patch('builtins.input', side_effect=['add', '2', '3', 'clear', 'exit'])
@patch('builtins.print')
def test_repl_clear(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("History cleared")


# Undo

@patch('builtins.input', side_effect=['add', '2', '3', 'undo', 'exit'])
@patch('builtins.print')
def test_repl_undo_with_history(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("Operation undone")

@patch('builtins.input', side_effect=['undo', 'exit'])
@patch('builtins.print')
def test_repl_undo_empty(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("Nothing to undo")


# Redo

@patch('builtins.input', side_effect=['add', '2', '3', 'undo', 'redo', 'exit'])
@patch('builtins.print')
def test_repl_redo_with_history(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("Operation redone")

@patch('builtins.input', side_effect=['redo', 'exit'])
@patch('builtins.print')
def test_repl_redo_empty(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("Nothing to redo")


# Save

@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
def test_repl_save_success(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("History saved successfully")

@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
def test_repl_save_failure(mock_print, mock_input, tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    calc_instance = Calculator(config=config)
    calc_instance.save_history = MagicMock(side_effect=Exception("disk error"))
    with patch('app.calculator_repl.Calculator', return_value=calc_instance), \
         patch('app.display.Fore.GREEN', ''), \
         patch('app.display.Fore.YELLOW', ''), \
         patch('app.display.Fore.RED', ''):
        calculator_repl()
        printed = [str(call) for call in mock_print.call_args_list]
        assert any("Error saving history" in p for p in printed)


# Load

@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
def test_repl_load_success(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("History loaded successfully")

@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
def test_repl_load_failure(mock_print, mock_input, tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    calc_instance = Calculator(config=config)
    calc_instance.load_history = MagicMock(side_effect=Exception("file error"))
    with patch('app.calculator_repl.Calculator', return_value=calc_instance), \
         patch('app.display.Fore.GREEN', ''), \
         patch('app.display.Fore.YELLOW', ''), \
         patch('app.display.Fore.RED', ''):
        calculator_repl()
        printed = [str(call) for call in mock_print.call_args_list]
        assert any("Error loading history" in p for p in printed)


# Unknown command

@patch('builtins.input', side_effect=['foobar', 'exit'])
@patch('builtins.print')
def test_repl_unknown_command(mock_print, mock_input, temp_config):
    calculator_repl()
    printed = [str(call) for call in mock_print.call_args_list]
    assert any("Unknown command" in p for p in printed)


# KeyboardInterrupt

@patch('builtins.input', side_effect=[KeyboardInterrupt, 'exit'])
@patch('builtins.print')
def test_repl_keyboard_interrupt(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("\nOperation cancelled")


# EOFError

@patch('builtins.input', side_effect=[EOFError])
@patch('builtins.print')
def test_repl_eof(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("\nInput terminated. Exiting...")


# Unexpected error in main REPL loop

@patch('builtins.input', side_effect=[Exception("unexpected"), 'exit'])
@patch('builtins.print')
def test_repl_unexpected_loop_error(mock_print, mock_input, temp_config):
    calculator_repl()
    mock_print.assert_any_call("Error: unexpected")


# Fatal error

@patch('builtins.print')
def test_repl_fatal_error(mock_print, temp_config):
    with patch('app.calculator_repl.Calculator', side_effect=Exception("fatal")):
        with pytest.raises(Exception, match="fatal"):
            calculator_repl()
        mock_print.assert_any_call("Fatal error: fatal")