"""Functions for handling conversion to a form expected by Kraken."""

from typing import List, Literal

from ..constants.trading import OrderFlags


def boolean_to_message(value: bool) -> Literal["true"] | Literal["false"]:
    """Convert python boolean to value expected by Kraken

    Returns:
        'true' if value is true else 'false'.
    """
    return "true" if value else "false"


def order_flags_to_message(flags: List[OrderFlags]) -> str:
    """Convert List of flags to comma separated values of flags.

    Args:
        flags: List of OrderFlags to apply to the order

    Returns:
        The list of OrderFlags as a comma separated string.
    """
    return ",".join([str(i) for i in flags])
