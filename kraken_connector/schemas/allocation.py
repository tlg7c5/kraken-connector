from typing import TYPE_CHECKING, Any, Self, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..schemas.allocation_amount import (
        AllocationAmount,
    )
    from ..schemas.allocation_payout import (
        AllocationPayout,
    )
    from ..schemas.allocation_total_rewarded import (
        AllocationTotalRewarded,
    )


@_attrs_define
class Allocation:
    """
    Attributes:
        amount_allocated (AllocationAmount): Amounts allocated to this Earn
            strategy
        native_asset (str): The asset of the native currency of this allocation
        strategy_id (str): Unique ID for Earn Strategy
        total_rewarded (AllocationTotalRewarded): Amount earned using the strategy during
            the whole lifetime of user account
        payout (Union[Unset, None, AllocationPayout]): Information about the current
            payout period (if any)
    """

    amount_allocated: "AllocationAmount"
    native_asset: str
    strategy_id: str
    total_rewarded: "AllocationTotalRewarded"
    payout: Union[Unset, None, "AllocationPayout"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        amount_allocated = self.amount_allocated.to_dict()

        native_asset = self.native_asset
        strategy_id = self.strategy_id
        total_rewarded = self.total_rewarded.to_dict()

        payout: Unset | None | dict[str, Any] = UNSET
        if not isinstance(self.payout, Unset):
            payout = self.payout.to_dict() if self.payout else None

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "amount_allocated": amount_allocated,
                "native_asset": native_asset,
                "strategy_id": strategy_id,
                "total_rewarded": total_rewarded,
            }
        )
        if payout is not UNSET:
            field_dict["payout"] = payout

        return field_dict

    @classmethod
    def from_dict(cls: Self, src_dict: dict[str, Any]) -> Self:
        from ..schemas.allocation_amount import (
            AllocationAmount,
        )
        from ..schemas.allocation_payout import (
            AllocationPayout,
        )
        from ..schemas.allocation_total_rewarded import (
            AllocationTotalRewarded,
        )

        d = src_dict.copy()
        amount_allocated = AllocationAmount.from_dict(d.pop("amount_allocated"))

        native_asset = d.pop("native_asset")

        strategy_id = d.pop("strategy_id")

        total_rewarded = AllocationTotalRewarded.from_dict(d.pop("total_rewarded"))

        _payout = d.pop("payout", UNSET)
        payout: Unset | None | AllocationPayout
        if _payout is None:
            payout = None
        elif isinstance(_payout, Unset):
            payout = UNSET
        else:
            payout = AllocationPayout.from_dict(_payout)

        list_allocations_response_200_result_items_item = cls(
            amount_allocated=amount_allocated,
            native_asset=native_asset,
            strategy_id=strategy_id,
            total_rewarded=total_rewarded,
            payout=payout,
        )

        list_allocations_response_200_result_items_item.additional_properties = d
        return list_allocations_response_200_result_items_item

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
