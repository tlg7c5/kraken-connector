"""Data validation and coercion functions."""

from ..types import Unset


def _check_reqid(value: Unset | int | str) -> Unset | int:
    if not isinstance(value, (Unset, int)):
        try:
            return int(value)
        except ValueError as e:
            raise e
    return value
