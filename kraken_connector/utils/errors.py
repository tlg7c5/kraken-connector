"""Functions for building error messages."""
from typing import TYPE_CHECKING, Any

from attrs import Attribute as _attrs_Attribute

if TYPE_CHECKING:
    from ..constants.websockets import EventType


def build_event_error_msg(
    attribute: _attrs_Attribute, value: Any, expected: "EventType"
):
    return (
        f"Expected '{attribute.name}' with value '{expected.value}' but received"
        f" '{value}'"
    )
