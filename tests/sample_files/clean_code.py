"""A clean, well-formatted, type-annotated, and PEP 8 compliant Python module."""
from typing import List, Optional


def calculate_average(numbers: List[float]) -> Optional[float]:
    """Calculate the arithmetic mean of a sequence of floating-point numbers.

    Args:
        numbers: List of floats to average.

    Returns:
        The average float value, or None if the input list is empty.
    """
    if not numbers:
        return None
    return sum(numbers) / len(numbers)


def format_greeting(name: str, uppercase: bool = False) -> str:
    """Format a personalized greeting message.

    Args:
        name: Name of the recipient.
        uppercase: Whether to return the greeting in uppercase letters.

    Returns:
        Formatted greeting string.
    """
    cleaned_name = name.strip()
    if not cleaned_name:
        cleaned_name = "Guest"
    greeting = f"Hello, {cleaned_name}!"
    return greeting.upper() if uppercase else greeting
