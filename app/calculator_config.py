# Calculator config module with dotenv support and validation.

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
import os
from typing import Optional

from dotenv import load_dotenv

from app.exceptions import ConfigurationError

load_dotenv()


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path: The root directory path of the project.
    """
    current_file = Path(__file__)
    return current_file.parent.parent


@dataclass
class CalculatorConfig:
    """
    Calculator configuration settings.

    Manages all configuration parameters required by the calculator application,
    including directory paths, history size, auto-save preferences, calculation
    precision, maximum input values, and default encoding. Configuration can be
    set via environment variables or by passing parameters directly to the
    constructor.
    """

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        max_history_size: Optional[int] = None,
        auto_save: Optional[bool] = None,
        precision: Optional[int] = None,
        max_input_value: Optional[Decimal] = None,
        default_encoding: Optional[str] = None
    ):
        """
        Initialize configuration with environment variables and defaults.

        Args:
            base_dir (Optional[Path]): Base directory for the calculator.
            max_history_size (Optional[int]): Maximum number of history entries.
            auto_save (Optional[bool]): Whether to auto-save history.
            precision (Optional[int]): Number of decimal places for calculations.
            max_input_value (Optional[Decimal]): Maximum allowed input value.
            default_encoding (Optional[str]): Default encoding for file operations.
        """
        project_root = get_project_root()
        self.base_dir = base_dir or Path(
            os.getenv('CALCULATOR_BASE_DIR', str(project_root))
        ).resolve()

        self.max_history_size = max_history_size if max_history_size is not None else int(
            os.getenv('CALCULATOR_MAX_HISTORY_SIZE', '1000')
        )

        auto_save_env = os.getenv('CALCULATOR_AUTO_SAVE', 'true').lower()
        self.auto_save = auto_save if auto_save is not None else (
            auto_save_env == 'true' or auto_save_env == '1'
        )

        self.precision = precision if precision is not None else int(
            os.getenv('CALCULATOR_PRECISION', '10')
        )

        self.max_input_value = max_input_value if max_input_value is not None else Decimal(
            os.getenv('CALCULATOR_MAX_INPUT_VALUE', '1e999')
        )

        self.default_encoding = default_encoding or os.getenv(
            'CALCULATOR_DEFAULT_ENCODING', 'utf-8'
        )

    @property
    def log_dir(self) -> Path:
        """
        Get log directory path.

        Returns:
            Path: The log directory path.
        """
        return Path(os.getenv(
            'CALCULATOR_LOG_DIR',
            str(self.base_dir / "logs")
        )).resolve()

    @property
    def history_dir(self) -> Path:
        """
        Get history directory path.

        Returns:
            Path: The history directory path.
        """
        return Path(os.getenv(
            'CALCULATOR_HISTORY_DIR',
            str(self.base_dir / "history")
        )).resolve()

    @property
    def history_file(self) -> Path:
        """
        Get history file path.

        Returns:
            Path: The history file path.
        """
        return Path(os.getenv(
            'CALCULATOR_HISTORY_FILE',
            str(self.history_dir / "calculator_history.csv")
        )).resolve()

    @property
    def log_file(self) -> Path:
        """
        Get log file path.

        Returns:
            Path: The log file path.
        """
        return Path(os.getenv(
            'CALCULATOR_LOG_FILE',
            str(self.log_dir / "calculator.log")
        )).resolve()

    def validate(self) -> None:
        """
        Validate configuration settings.

        Raises:
            ConfigurationError: If any configuration parameter is invalid.
        """
        if self.max_history_size <= 0:
            raise ConfigurationError("max_history_size must be positive")
        if self.precision <= 0:
            raise ConfigurationError("precision must be positive")
        if self.max_input_value <= 0:
            raise ConfigurationError("max_input_value must be positive")