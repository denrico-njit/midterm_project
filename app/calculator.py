# Main Calculator class which serves as a facade to coordinate all components of the application

from decimal import Decimal
import logging
import os
from pathlib import Path
from typing import Optional

import pandas as pd

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.exceptions import OperationError, ValidationError
from app.history import HistoryObserver
from app.input_validators import InputValidator
from app.operations import Operation, OperationFactory


class Calculator:
    """
    Facade providing a simplified interface to the following:
      - CalculatorConfig: configuration and environment management
      - InputValidator: input parsing and validation
      - OperationFactory + Operation classes: arithmetic strategy execution
      - CalculatorMemento: undo/redo state management
      - HistoryObserver instances: logging and auto-save notifications
      - pandas CSV read/write: persistent history storage
    """

    def __init__(self, config: Optional[CalculatorConfig] = None):
        """
        Initialize calculator with configuration.

        Args:
            config (Optional[CalculatorConfig]): Configuration settings.
                If not provided, default settings are loaded from environment variables.
        """
        if config is None:
            current_file = Path(__file__)
            project_root = current_file.parent.parent
            config = CalculatorConfig(base_dir=project_root)

        self.config = config
        self.config.validate()

        os.makedirs(self.config.log_dir, exist_ok=True)

        self._setup_logging()

        self.history: list[Calculation] = []
        self.operation_strategy: Optional[Operation] = None
        self.observers: list[HistoryObserver] = []
        self.undo_stack: list[CalculatorMemento] = []
        self.redo_stack: list[CalculatorMemento] = []

        self._setup_directories()

        try:
            self.load_history()
        except Exception as e:
            logging.warning(f"Could not load existing history: {e}")

        logging.info("Calculator initialized with configuration")

    def _setup_logging(self) -> None:
        """
        Configure the logging system.
        """
        try:
            os.makedirs(self.config.log_dir, exist_ok=True)
            log_file = self.config.log_file.resolve()
            logging.basicConfig(
                filename=str(log_file),
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                force=True
            )
            logging.info(f"Logging initialized at: {log_file}")
        except Exception as e:
            print(f"Error setting up logging: {e}")
            raise

    def _setup_directories(self) -> None:
        """
        Create required directories.
        """
        self.config.history_dir.mkdir(parents=True, exist_ok=True)

    def add_observer(self, observer: HistoryObserver) -> None:
        """
        Register a new observer.

        Args:
            observer (HistoryObserver): The observer to be added.
        """
        self.observers.append(observer)
        logging.info(f"Added observer: {observer.__class__.__name__}")

    def remove_observer(self, observer: HistoryObserver) -> None:
        """
        Remove an existing observer.

        Args:
            observer (HistoryObserver): The observer to be removed.
        """
        self.observers.remove(observer)
        logging.info(f"Removed observer: {observer.__class__.__name__}")

    def notify_observers(self, calculation: Calculation) -> None:
        """
        Notify all observers of a new calculation.

        Args:
            calculation (Calculation): The latest calculation performed.
        """
        for observer in self.observers:
            observer.update(calculation)

    def set_operation(self, operation: Operation) -> None:
        """
        Set the current operation strategy.

        Args:
            operation (Operation): The operation strategy to be set.
        """
        self.operation_strategy = operation
        logging.info(f"Set operation: {operation}")

    def perform_operation(self, a: str, b: str) -> Decimal:
        """
        Perform calculation with the current operation.

        Args:
            a (str): The first operand as a string.
            b (str): The second operand as a string.

        Returns:
            Decimal: The result of the calculation.

        Raises:
            OperationError: If no operation is set or if the operation fails.
            ValidationError: If input validation fails.
        """
        if not self.operation_strategy:
            raise OperationError("No operation set")

        try:
            validated_a = InputValidator.validate_number(a, self.config)
            validated_b = InputValidator.validate_number(b, self.config)

            result = self.operation_strategy.execute(validated_a, validated_b)

            calculation = Calculation(
                operation=str(self.operation_strategy),
                operand1=validated_a,
                operand2=validated_b,
                result=result
            )

            self.undo_stack.append(CalculatorMemento(self.history.copy()))
            self.redo_stack.clear()
            self.history.append(calculation)

            if len(self.history) > self.config.max_history_size:
                self.history.pop(0)

            self.notify_observers(calculation)

            return result

        except ValidationError as e:
            logging.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Operation failed: {str(e)}")
            raise OperationError(f"Operation failed: {str(e)}")

    def save_history(self) -> None:
        """
        Save calculation history to a CSV file using pandas.

        Raises:
            OperationError: If saving the history fails.
        """
        try:
            self.config.history_dir.mkdir(parents=True, exist_ok=True)

            history_data = [
                {
                    'operation': str(calc.operation),
                    'operand1': str(calc.operand1),
                    'operand2': str(calc.operand2),
                    'result': str(calc.result),
                    'timestamp': calc.timestamp.isoformat()
                }
                for calc in self.history
            ]

            if history_data:
                pd.DataFrame(history_data).to_csv(
                    self.config.history_file, index=False
                )
                logging.info(f"History saved to {self.config.history_file}")
            else:
                pd.DataFrame(
                    columns=['operation', 'operand1', 'operand2', 'result', 'timestamp']
                ).to_csv(self.config.history_file, index=False)
                logging.info("Empty history saved")

        except Exception as e:
            logging.error(f"Failed to save history: {e}")
            raise OperationError(f"Failed to save history: {e}")

    def load_history(self) -> None:
        """
        Load calculation history from a CSV file using pandas.

        Raises:
            OperationError: If loading the history fails.
        """
        try:
            if self.config.history_file.exists():
                df = pd.read_csv(self.config.history_file)
                if not df.empty:
                    self.history = [
                        Calculation.from_dict({
                            'operation': row['operation'],
                            'operand1': row['operand1'],
                            'operand2': row['operand2'],
                            'result': row['result'],
                            'timestamp': row['timestamp']
                        })
                        for _, row in df.iterrows()
                    ]
                    logging.info(f"Loaded {len(self.history)} calculations from history")
                else:
                    logging.info("Loaded empty history file")
            else:
                logging.info("No history file found - starting with empty history")
        except Exception as e:
            logging.error(f"Failed to load history: {e}")
            raise OperationError(f"Failed to load history: {e}")

    def get_history_dataframe(self) -> pd.DataFrame:
        """
        Get calculation history as a pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing the calculation history.
        """
        return pd.DataFrame([
            {
                'operation': str(calc.operation),
                'operand1': str(calc.operand1),
                'operand2': str(calc.operand2),
                'result': str(calc.result),
                'timestamp': calc.timestamp
            }
            for calc in self.history
        ])

    def show_history(self) -> list[str]:
        """
        Get formatted history of calculations.

        Returns:
            list[str]: List of formatted calculation history entries.
        """
        return [
            f"{calc.operation}({calc.operand1}, {calc.operand2}) = {calc.result}"
            for calc in self.history
        ]

    def clear_history(self) -> None:
        """
        Clear calculation history.
        """
        self.history.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        logging.info("History cleared")

    def undo(self) -> bool:
        """
        Undo the last operation.

        Returns:
            bool: True if an operation was undone, False if nothing to undo.
        """
        if not self.undo_stack:
            return False
        memento = self.undo_stack.pop()
        self.redo_stack.append(CalculatorMemento(self.history.copy()))
        self.history = memento.history.copy()
        return True

    def redo(self) -> bool:
        """
        Redo the previously undone operation.

        Returns:
            bool: True if an operation was redone, False if nothing to redo.
        """
        if not self.redo_stack:
            return False
        memento = self.redo_stack.pop()
        self.undo_stack.append(CalculatorMemento(self.history.copy()))
        self.history = memento.history.copy()
        return True

    def calculate(self, operation_type: str, a: str, b: str) -> Decimal:
        """
        Facade method for performing a calculation.

        Args:
            operation_type (str): Operation name (e.g., 'add', 'divide').
            a (str): First operand as a string.
            b (str): Second operand as a string.

        Returns:
            Decimal: The result of the calculation.
        """
        operation = OperationFactory.create_operation(operation_type)
        self.set_operation(operation)
        return self.perform_operation(a, b)