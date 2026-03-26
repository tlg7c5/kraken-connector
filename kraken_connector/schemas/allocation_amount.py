from typing import TYPE_CHECKING, Any, Self, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..schemas.allocation_bonding import (
        AllocationBonding,
    )
    from ..schemas.allocation_exit_queue import (
        AllocationExitQueue,
    )
    from ..schemas.allocation_pending import (
        AllocationPending,
    )
    from ..schemas.allocation_total import (
        AllocationTotal,
    )
    from ..schemas.allocation_unbonding import (
        AllocationUnbonding,
    )


@_attrs_define
class AllocationAmount:
    """Amounts allocated to this Earn strategy

    Attributes:
        total (AllocationTotal): Total amount allocated to this Earn
            strategy
        bonding (Union[Unset, None, AllocationBonding]): Amount allocated
            in bonding status
        exit_queue (Union[Unset, None, AllocationExitQueue]): Amount
            allocated in the exit-queue status
        pending (Union[Unset, None, AllocationPending]): Pending
            allocation amount - can be negative if the pending operation is deallocation
        unbonding (Union[Unset, None, AllocationUnbonding]): Amount
            allocated in unbonding status
    """

    total: "AllocationTotal"
    bonding: Union[Unset, None, "AllocationBonding"] = UNSET
    exit_queue: Union[Unset, None, "AllocationExitQueue"] = UNSET
    pending: Union[Unset, None, "AllocationPending"] = UNSET
    unbonding: Union[Unset, None, "AllocationUnbonding"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total = self.total.to_dict()

        bonding: Unset | None | dict[str, Any] = UNSET
        if not isinstance(self.bonding, Unset):
            bonding = self.bonding.to_dict() if self.bonding else None

        exit_queue: Unset | None | dict[str, Any] = UNSET
        if not isinstance(self.exit_queue, Unset):
            exit_queue = self.exit_queue.to_dict() if self.exit_queue else None

        pending: Unset | None | dict[str, Any] = UNSET
        if not isinstance(self.pending, Unset):
            pending = self.pending.to_dict() if self.pending else None

        unbonding: Unset | None | dict[str, Any] = UNSET
        if not isinstance(self.unbonding, Unset):
            unbonding = self.unbonding.to_dict() if self.unbonding else None

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total": total,
            }
        )
        if bonding is not UNSET:
            field_dict["bonding"] = bonding
        if exit_queue is not UNSET:
            field_dict["exit_queue"] = exit_queue
        if pending is not UNSET:
            field_dict["pending"] = pending
        if unbonding is not UNSET:
            field_dict["unbonding"] = unbonding

        return field_dict

    @classmethod
    def from_dict(cls: Self, src_dict: dict[str, Any]) -> Self:
        from ..schemas.allocation_bonding import (
            AllocationBonding,
        )
        from ..schemas.allocation_exit_queue import (
            AllocationExitQueue,
        )
        from ..schemas.allocation_pending import (
            AllocationPending,
        )
        from ..schemas.allocation_total import (
            AllocationTotal,
        )
        from ..schemas.allocation_unbonding import (
            AllocationUnbonding,
        )

        d = src_dict.copy()
        total = AllocationTotal.from_dict(d.pop("total"))

        _bonding = d.pop("bonding", UNSET)
        bonding: Unset | None | AllocationBonding
        if _bonding is None:
            bonding = None
        elif isinstance(_bonding, Unset):
            bonding = UNSET
        else:
            bonding = AllocationBonding.from_dict(_bonding)

        _exit_queue = d.pop("exit_queue", UNSET)
        exit_queue: Unset | None | AllocationExitQueue
        if _exit_queue is None:
            exit_queue = None
        elif isinstance(_exit_queue, Unset):
            exit_queue = UNSET
        else:
            exit_queue = AllocationExitQueue.from_dict(_exit_queue)

        _pending = d.pop("pending", UNSET)
        pending: Unset | None | AllocationPending
        if _pending is None:
            pending = None
        elif isinstance(_pending, Unset):
            pending = UNSET
        else:
            pending = AllocationPending.from_dict(_pending)

        _unbonding = d.pop("unbonding", UNSET)
        unbonding: Unset | None | AllocationUnbonding
        if _unbonding is None:
            unbonding = None
        elif isinstance(_unbonding, Unset):
            unbonding = UNSET
        else:
            unbonding = AllocationUnbonding.from_dict(_unbonding)

        list_allocations_response_200_result_items_item_amount_allocated = cls(
            total=total,
            bonding=bonding,
            exit_queue=exit_queue,
            pending=pending,
            unbonding=unbonding,
        )

        list_allocations_response_200_result_items_item_amount_allocated.additional_properties = (
            d
        )
        return list_allocations_response_200_result_items_item_amount_allocated

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
