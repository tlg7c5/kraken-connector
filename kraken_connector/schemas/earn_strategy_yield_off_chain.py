from typing import Any, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..constants.earn import (
    YieldSourceType,
)


@_attrs_define
class EarnStrategyYieldOffChain:
    """Funds are put at work in another yield-generation financial mechanism.

    Attributes:
        type (YieldSourceType.OFF_CHAIN):
    """

    type: YieldSourceType.OFF_CHAIN
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type = self.type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Self, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        type = YieldSourceType(d.pop("type"))

        list_strategies_response_200_result_items_item_yield_source_type_1 = cls(
            type=type,
        )

        list_strategies_response_200_result_items_item_yield_source_type_1.additional_properties = (
            d
        )
        return list_strategies_response_200_result_items_item_yield_source_type_1

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
