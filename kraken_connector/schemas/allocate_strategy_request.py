from typing import TYPE_CHECKING, Any, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..security import get_nonce
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..schemas.allocate_strategy_request_nonce import (
        AllocateStrategyRequestNonce,
    )


@_attrs_define
class AllocateStrategyRequest:
    """Allocation amount in asset specified in the strategy

    Attributes:
        amount (str): The amount to allocate. This field is required.
        nonce (AllocateStrategyRequestNonce):
        strategy_id (str): A unique identifier of the chosen earn strategy, as returned from
            `/0/private/Earn/Strategies`.
        otp (Union[Unset, None, str]): https://docs.kraken.com/rest/#section/Authentication/Nonce-and-2FA
    """

    amount: str
    nonce: "AllocateStrategyRequestNonce"
    strategy_id: str
    otp: Unset | None | str = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        amount = self.amount
        nonce = self.nonce.to_dict()

        strategy_id = self.strategy_id
        otp = self.otp

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "amount": amount,
                "nonce": nonce,
                "strategy_id": strategy_id,
            }
        )
        if otp is not UNSET:
            field_dict["otp"] = otp

        return field_dict

    @classmethod
    def from_dict(cls: Self, src_dict: dict[str, Any]) -> Self:
        from ..schemas.allocate_strategy_request_nonce import (
            AllocateStrategyRequestNonce,
        )

        d = src_dict.copy()
        amount = d.pop("amount")

        nonce = AllocateStrategyRequestNonce.from_dict(d.pop("nonce", get_nonce()))

        strategy_id = d.pop("strategy_id")

        otp = d.pop("otp", UNSET)

        allocate_strategy_json_body = cls(
            amount=amount,
            nonce=nonce,
            strategy_id=strategy_id,
            otp=otp,
        )

        allocate_strategy_json_body.additional_properties = d
        return allocate_strategy_json_body

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
