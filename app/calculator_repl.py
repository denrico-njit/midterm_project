# Main Calculator REPL (Read-Eval-Print Loop)

from decimal import Decimal
import logging
import textwrap

from app.calculator import Calculator
from app.display import print_result, print_info, print_error
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory
from app.display import print_result, print_info, print_error, format_decimal


def calculator_repl():
    """
    Command-line interface for the calculator.

    Implements a Read-Eval-Print Loop (REPL) that continuously prompts the user
    for commands, processes arithmetic operations, and manages calculation history.
    """
    try:
        calc = Calculator()

        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))

        print("The Python REPL Calculator is ready to use! Type 'help' for available commands.")

        while True:
            try:
                command = input("\nEnter command: ").lower().strip()

                if command == 'help':
                    print("\nAvailable commands:")
                    print("\n  Operations:")
                    print(f"    {'Command':<15} {'Description':<45} {'Example'}")
                    print(f"    {'-'*15} {'-'*45} {'-'*20}")
                    for op in OperationFactory._operations.values():
                        if hasattr(op, '_help'):
                            h = op._help
                            name_col = f"{h['name']:<15}"
                            usage_col = h['usage']
                            lines = textwrap.wrap(h['description'], width=45)
                            print(f"    {name_col} {lines[0]:<45} {usage_col}")
                            for line in lines[1:]:
                                print(f"    {' '*15} {line}")
                        else:
                            print(f"    {op.__name__}")
                    print("\n  History:")
                    print("    history         Show calculation history")
                    print("    clear           Clear calculation history")
                    print("    undo            Undo the last calculation")
                    print("    redo            Redo the last undone calculation")
                    print("    save            Save calculation history to file")
                    print("    load            Load calculation history from file")
                    print("\n  Other:")
                    print("    help            Show this help message")
                    print("    exit            Exit the calculator")
                    continue

                if command == 'exit':
                    try:
                        calc.save_history()
                        print_info("History saved successfully.")
                    except Exception as e:
                        print_error(f"Warning: Could not save history: {e}")
                    print("Exiting...")
                    break

                if command == 'history':
                    history = calc.show_history()
                    if not history:
                        print_info("No available history.")
                    else:
                        print("\nCalculation History:")
                        for i, entry in enumerate(history, 1):
                            print_info(f"{i}. {entry}")
                    continue

                if command == 'clear':
                    calc.clear_history()
                    print_info("History cleared")
                    continue

                if command == 'undo':
                    if calc.undo():
                        print_info("Operation undone")
                    else:
                        print_info("Nothing to undo")
                    continue

                if command == 'redo':
                    if calc.redo():
                        print_info("Operation redone")
                    else:
                        print_info("Nothing to redo")
                    continue

                if command == 'save':
                    try:
                        calc.save_history()
                        print_info("History saved successfully")
                    except Exception as e:
                        print_error(f"Error saving history: {e}")
                    continue

                if command == 'load':
                    try:
                        calc.load_history()
                        print_info("History loaded successfully")
                    except Exception as e:
                        print_error(f"Error loading history: {e}")
                    continue

                if command in OperationFactory._operations:
                    try:
                        print("\nEnter numbers (or 'cancel' to abort):")
                        a = input("First number: ")
                        if a.lower() == 'cancel':
                            print_info("Operation cancelled")
                            continue
                        b = input("Second number: ")
                        if b.lower() == 'cancel':
                            print_info("Operation cancelled")
                            continue

                        result = calc.calculate(command, a, b)
                        print_result(f"\nResult: {format_decimal(result)}")

                    except KeyboardInterrupt:  # pragma: no cover
                        print_info("\nOperation cancelled")
                        continue
                    except EOFError:  # pragma: no cover
                        print_error("\nInput terminated. Exiting...")
                        raise
                    except (ValidationError, OperationError) as e:
                        print_error(f"Error: {e}")
                    except Exception as e:
                        print_error(f"Unexpected error: {e}")
                    continue

                print_error(f"Unknown command: '{command}'. Type 'help' for available commands.")

            except KeyboardInterrupt:  # pragma: no cover
                print_info("\nOperation cancelled")
                continue
            except EOFError:  # pragma: no cover
                print("\nInput terminated. Exiting...")
                break
            except Exception as e:
                print_error(f"Error: {e}")
                continue

    except Exception as e:
        print_error(f"Fatal error: {e}")
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise