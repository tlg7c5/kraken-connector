from typing import Any, Literal, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..constants.earn import (
    StrategyLockType,
)


@_attrs_define
class EarnStrategyLockInstant:
    """Instant strategy lock type is a special case of bonded strategy with no bonding/unbonding period. It is equivalent
    of what used to be called "flex" in legacy staking system (not to be confused with Flex defined above). Explicit
    allocate/deallocate action is required.

        Attributes:
            payout_frequency (int): At what intervals are rewards distributed and credited to the user`s ledger, in seconds
            type (StrategyLockType.INSTANT):
    """

    payout_frequency: int
    type: Literal[StrategyLockType.INSTANT]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payout_frequency = self.payout_frequency
        type = self.type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "payout_frequency": payout_frequency,
                "type": type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        payout_frequency = d.pop("payout_frequency")

        type = StrategyLockType(d.pop("type"))

        list_strategies_response_200_result_items_item_lock_type_type_3 = cls(
            payout_frequency=payout_frequency,
            type=type,  # type: ignore[arg-type]
        )

        list_strategies_response_200_result_items_item_lock_type_type_3.additional_properties = (
            d
        )
        return list_strategies_response_200_result_items_item_lock_type_type_3

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
