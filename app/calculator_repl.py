# Main Calculator REPL (Read-Eval-Print Loop)

from decimal import Decimal
import logging

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory


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
                    for op in OperationFactory._operations.keys():
                        print(f"    {op}")
                    print("\n  History:")
                    print("    history - Show calculation history")
                    print("    clear   - Clear calculation history")
                    print("    undo    - Undo the last calculation")
                    print("    redo    - Redo the last undone calculation")
                    print("    save    - Save calculation history to file")
                    print("    load    - Load calculation history from file")
                    print("\n  Other:")
                    print("    help    - Show this help message")
                    print("    exit    - Exit the calculator")
                    continue
                
                if command == 'exit':
                    try:
                        calc.save_history()
                        print("History saved successfully.")
                    except Exception as e:
                        print(f"Warning: Could not save history: {e}")
                    print("Exiting...")
                    break

                if command == 'history':
                    history = calc.show_history()
                    if not history:
                        print("No available history.")
                    else:
                        print("\nCalculation History:")
                        for i, entry in enumerate(history, 1):
                            print(f"{i}. {entry}")
                    continue

                if command == 'clear':
                    calc.clear_history()
                    print("History cleared")
                    continue

                if command == 'undo':
                    if calc.undo():
                        print("Operation undone")
                    else:
                        print("Nothing to undo")
                    continue

                if command == 'redo':
                    if calc.redo():
                        print("Operation redone")
                    else:
                        print("Nothing to redo")
                    continue

                if command == 'save':
                    try:
                        calc.save_history()
                        print("History saved successfully")
                    except Exception as e:
                        print(f"Error saving history: {e}")
                    continue

                if command == 'load':
                    try:
                        calc.load_history()
                        print("History loaded successfully")
                    except Exception as e:
                        print(f"Error loading history: {e}")
                    continue

                if command in OperationFactory._operations:
                    try:
                        print("\nEnter numbers (or 'cancel' to abort):")
                        a = input("First number: ")
                        if a.lower() == 'cancel':
                            print("Operation cancelled")
                            continue
                        b = input("Second number: ")
                        if b.lower() == 'cancel':
                            print("Operation cancelled")
                            continue

                        result = calc.calculate(command, a, b)
                        print(f"\nResult: {result.normalize()}")

                    # Handle interruption during input collection 
                    except KeyboardInterrupt: #pragma: no cover - can't simulate
                        print("\nOperation cancelled")
                        continue
                    except EOFError: #pragma: no cover - can't simulate
                        print("\nInput terminated. Exiting...")
                        raise
                    except (ValidationError, OperationError) as e:
                        print(f"Error: {e}")
                    except Exception as e:
                        print(f"Unexpected error: {e}")
                    continue

                print(f"Unknown command: '{command}'. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\nOperation cancelled")
                continue
            except EOFError:
                print("\nInput terminated. Exiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue

    except Exception as e:
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise