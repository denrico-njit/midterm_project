# Display utilities for the calculator REPL

from decimal import Decimal
from colorama import Fore, init


# Helper function to manage when scientific notation is used for Decimal values
def format_decimal(value: Decimal) -> str:
    """Format a Decimal for display."""
    normalized = value.normalize()
    if normalized == normalized.to_integral_value() and 'E' in str(normalized):
        exponent = normalized.as_tuple().exponent
        if abs(exponent) <= 4:  
            return str(int(normalized))
    return str(normalized)

# Initialize colorama 
init(autoreset=True)

# Implement color-coded print functions for different message types
def print_result(message: str) -> None:
    """Print a result message in green."""
    print(Fore.GREEN + message)


def print_info(message: str) -> None:
    """Print an informational message in yellow."""
    print(Fore.YELLOW + message)


def print_error(message: str) -> None:
    """Print an error or warning message in red."""
    print(Fore.RED + message)
