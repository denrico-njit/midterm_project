# Calculator Memento implementation for undo/redo functionality.

from dataclasses import dataclass, field
import datetime
## Avoids nesting syntax in type hints for CalculatorMemento.to_dict and from_dict methods.
from typing import Any 

from app.calculation import Calculation


@dataclass
class CalculatorMemento:
    """
    Stores calculator state for undo/redo functionality.

    The Memento pattern allows the Calculator to save its current state (history)
    so that it can be restored later. This enables features like undo and redo.
    """

    history: list[Calculation]
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert memento to dictionary.

        Returns:
            dict[str, Any]: A dictionary containing the serialized state of the memento.
        """
        return {
            'history': [calc.to_dict() for calc in self.history],
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'CalculatorMemento':
        """
        Create memento from dictionary.

        Args:
            data (dict[str, Any]): Dictionary containing serialized memento data.

        Returns:
            CalculatorMemento: A new instance of CalculatorMemento with restored state.
        """
        return cls(
            history=[Calculation.from_dict(calc) for calc in data['history']],
            timestamp=datetime.datetime.fromisoformat(data['timestamp'])
        )