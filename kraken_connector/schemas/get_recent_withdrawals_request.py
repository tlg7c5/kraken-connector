from typing import Any, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..security import get_nonce
from ..types import UNSET, Unset


@_attrs_define
class GetRecentWithdrawalsRequest:
    """
    Attributes:
        nonce (int): Nonce used in construction of `API-Sign` header. Default `get_nonce`
        asset (Union[Unset, str]): Filter for specific asset being withdrawn
        method (Union[Unset, str]): Filter for specific name of withdrawal method
    """

    nonce: int = get_nonce()
    asset: Unset | str = UNSET
    method: Unset | str = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        nonce = self.nonce
        asset = self.asset
        method = self.method

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "nonce": nonce,
            }
        )
        if asset is not UNSET:
            field_dict["asset"] = asset
        if method is not UNSET:
            field_dict["method"] = method

        return field_dict

    @classmethod
    def from_dict(cls: Self, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        nonce = d.pop("nonce", get_nonce())

        asset = d.pop("asset", UNSET)

        method = d.pop("method", UNSET)

        get_status_of_recent_withdrawals_request_body = cls(
            nonce=nonce,
            asset=asset,
            method=method,
        )

        get_status_of_recent_withdrawals_request_body.additional_properties = d
        return get_status_of_recent_withdrawals_request_body

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
