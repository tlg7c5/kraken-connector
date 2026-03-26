from typing import Any, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset


@_attrs_define
class CancelAllOrdersResult:
    """
    Attributes:
        count (Union[Unset, int]): Number of orders that were cancelled
    """

    count: Unset | int = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        count = self.count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if count is not UNSET:
            field_dict["count"] = count

        return field_dict

    @classmethod
    def from_dict(cls: Self, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        count = d.pop("count", UNSET)

        cancel_all_orders_response_200_result = cls(
            count=count,
        )

        cancel_all_orders_response_200_result.additional_properties = d
        return cancel_all_orders_response_200_result

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
