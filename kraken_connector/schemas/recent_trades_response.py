from typing import TYPE_CHECKING, Any, Self, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..schemas.recent_trades_result import RecentTradesResult


@_attrs_define
class RecentTradesResponse:
    """
    Attributes:
        result (Union[Unset, RecentTradesResult]):
        error (Union[Unset, List[str]]):
    """

    result: Union[Unset, "RecentTradesResult"] = UNSET
    error: Unset | list[str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result: Unset | dict[str, Any] = UNSET
        if not isinstance(self.result, Unset):
            result = self.result.to_dict()

        error: Unset | list[str] = UNSET
        if not isinstance(self.error, Unset):
            error = self.error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if result is not UNSET:
            field_dict["result"] = result
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: Self, src_dict: dict[str, Any]) -> Self:
        from ..schemas.recent_trades_result import RecentTradesResult

        d = src_dict.copy()
        _result = d.pop("result", UNSET)
        result: Unset | RecentTradesResult
        if isinstance(_result, Unset):
            result = UNSET
        else:
            result = RecentTradesResult.from_dict(_result)

        error = cast(list[str], d.pop("error", UNSET))

        trades = cls(
            result=result,
            error=error,
        )

        trades.additional_properties = d
        return trades

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
