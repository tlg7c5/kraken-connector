from typing import TYPE_CHECKING, Any, Self, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..schemas.trade_volume_fees import TradeVolumeFees
    from ..schemas.trade_volume_fees_maker import TradeVolumeFeesMaker


@_attrs_define
class TradeVolumeResult:
    """Trade TradeVolumeResponse

    Attributes:
        currency (Union[Unset, str]): Fee volume currency (will always be USD)
        volume (Union[Unset, str]): Current fee discount volume (in USD, breakdown by subaccount if applicable and
            logged in to master account)
        fees (Union[Unset, TradeVolumeFees]):
        fees_maker (Union[Unset, TradeVolumeFeesMaker]):
    """

    currency: Unset | str = UNSET
    volume: Unset | str = UNSET
    fees: Union[Unset, "TradeVolumeFees"] = UNSET
    fees_maker: Union[Unset, "TradeVolumeFeesMaker"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        currency = self.currency
        volume = self.volume
        fees: Unset | dict[str, Any] = UNSET
        if not isinstance(self.fees, Unset):
            fees = self.fees.to_dict()

        fees_maker: Unset | dict[str, Any] = UNSET
        if not isinstance(self.fees_maker, Unset):
            fees_maker = self.fees_maker.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if currency is not UNSET:
            field_dict["currency"] = currency
        if volume is not UNSET:
            field_dict["volume"] = volume
        if fees is not UNSET:
            field_dict["fees"] = fees
        if fees_maker is not UNSET:
            field_dict["fees_maker"] = fees_maker

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        from ..schemas.trade_volume_fees import TradeVolumeFees
        from ..schemas.trade_volume_fees_maker import TradeVolumeFeesMaker

        d = src_dict.copy()
        currency = d.pop("currency", UNSET)

        volume = d.pop("volume", UNSET)

        _fees = d.pop("fees", UNSET)
        fees: Unset | TradeVolumeFees
        fees = UNSET if isinstance(_fees, Unset) else TradeVolumeFees.from_dict(_fees)

        _fees_maker = d.pop("fees_maker", UNSET)
        fees_maker: Unset | TradeVolumeFeesMaker
        if isinstance(_fees_maker, Unset):
            fees_maker = UNSET
        else:
            fees_maker = TradeVolumeFeesMaker.from_dict(_fees_maker)

        volume_trade_volume = cls(
            currency=currency,
            volume=volume,
            fees=fees,
            fees_maker=fees_maker,
        )

        volume_trade_volume.additional_properties = d
        return volume_trade_volume

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
