# History module for the calculator application.
# Defines classes to implement the Observer pattern for tracking calculation history and auto-saving.

from abc import ABC, abstractmethod
import logging
from typing import TYPE_CHECKING

from app.calculation import Calculation

# Avoids circular imports by only importing Calculator for type checking purposes.
# Docs: https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING
if TYPE_CHECKING:
    from app.calculator import Calculator


class HistoryObserver(ABC):
    """
    Abstract base class for calculator observers.

    This class defines the interface for observers that monitor and react to
    new calculation events. Implementing classes must provide an update method
    to handle the received Calculation instance.
    """

    @abstractmethod
    def update(self, calculation: Calculation) -> None:
        """
        Handle new calculation event.

        Args:
            calculation (Calculation): The calculation that was performed.
        """
        pass  # pragma: no cover


class LoggingObserver(HistoryObserver):
    """
    Observer that logs calculations to a file.

    Implements the Observer pattern by listening for new calculations and logging
    their details to a log file.
    """

    def update(self, calculation: Calculation) -> None:
        """
        Log calculation details.

        Args:
            calculation (Calculation): The calculation that was performed.
        """
        logging.info(
            f"Calculation performed: {calculation.operation} "
            f"({calculation.operand1}, {calculation.operand2}) = "
            f"{calculation.result}"
        )


class AutoSaveObserver(HistoryObserver):
    """
    Observer that automatically saves calculations.

    Implements the Observer pattern by listening for new calculations and
    triggering an automatic save of the calculation history if the auto-save
    feature is enabled in the configuration.
    """

    def __init__(self, calculator: 'Calculator') -> None:
        """
        Initialize the AutoSaveObserver.

        Args:
            calculator (Calculator): The calculator instance to interact with.
                Must have 'config' and 'save_history' attributes.

        Raises:
            TypeError: If the calculator does not have the required attributes.
        """
        if not hasattr(calculator, 'config') or not hasattr(calculator, 'save_history'):
            raise TypeError("Calculator must have 'config' and 'save_history' attributes")
        self.calculator = calculator

    def update(self, calculation: Calculation) -> None:
        """
        Trigger auto-save.

        Args:
            calculation (Calculation): The calculation that was performed.
        """
        if self.calculator.config.auto_save:
            self.calculator.save_history()
            logging.info("History auto-saved")