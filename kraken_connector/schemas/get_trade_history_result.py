from typing import TYPE_CHECKING, Any, Self, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..schemas.get_trade_history_result_trades import GetTradeHistoryResultTrades


@_attrs_define
class GetTradeHistoryResult:
    """Trade History

    Attributes:
        count (Union[Unset, int]): Amount of available trades matching criteria
        trades (Union[Unset, GetTradeHistoryResultTrades]): Trade info
    """

    count: Unset | int = UNSET
    trades: Union[Unset, "GetTradeHistoryResultTrades"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        count = self.count
        trades: Unset | dict[str, Any] = UNSET
        if not isinstance(self.trades, Unset):
            trades = self.trades.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if count is not UNSET:
            field_dict["count"] = count
        if trades is not UNSET:
            field_dict["trades"] = trades

        return field_dict

    @classmethod
    def from_dict(cls: Self, src_dict: dict[str, Any]) -> Self:
        from ..schemas.get_trade_history_result_trades import (
            GetTradeHistoryResultTrades,
        )

        d = src_dict.copy()
        count = d.pop("count", UNSET)

        _trades = d.pop("trades", UNSET)
        trades: Unset | GetTradeHistoryResultTrades
        if isinstance(_trades, Unset):
            trades = UNSET
        else:
            trades = GetTradeHistoryResultTrades.from_dict(_trades)

        trade_history = cls(
            count=count,
            trades=trades,
        )

        trade_history.additional_properties = d
        return trade_history

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
