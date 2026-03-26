from typing import TYPE_CHECKING, Any, Self, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..schemas.get_closed_orders_result_entries import GetClosedOrdersResultEntries


@_attrs_define
class GetClosedOrdersResult:
    """Closed Orders

    Attributes:
        closed (Union[Unset, GetClosedOrdersResultEntries]):
        count (Union[Unset, int]): Amount of available order info matching criteria
    """

    closed: Union[Unset, "GetClosedOrdersResultEntries"] = UNSET
    count: Unset | int = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        closed: Unset | dict[str, Any] = UNSET
        if not isinstance(self.closed, Unset):
            closed = self.closed.to_dict()

        count = self.count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if closed is not UNSET:
            field_dict["closed"] = closed
        if count is not UNSET:
            field_dict["count"] = count

        return field_dict

    @classmethod
    def from_dict(cls: Self, src_dict: dict[str, Any]) -> Self:
        from ..schemas.get_closed_orders_result_entries import (
            GetClosedOrdersResultEntries,
        )

        d = src_dict.copy()
        _closed = d.pop("closed", UNSET)
        closed: Unset | GetClosedOrdersResultEntries
        if isinstance(_closed, Unset):
            closed = UNSET
        else:
            closed = GetClosedOrdersResultEntries.from_dict(_closed)

        count = d.pop("count", UNSET)

        closed_2_closed_orders = cls(
            closed=closed,
            count=count,
        )

        closed_2_closed_orders.additional_properties = d
        return closed_2_closed_orders

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
