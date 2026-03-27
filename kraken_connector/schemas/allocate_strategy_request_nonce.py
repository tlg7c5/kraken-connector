from typing import Any, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..security import get_nonce
from ..types import UNSET, Unset


@_attrs_define
class AllocateStrategyRequestNonce:
    """
    Attributes:
        nonce (Union[Unset, int]): Nonce used in construction of `API-Sign` header.
            Default `get_nonce`
    """

    nonce: Unset | int = get_nonce()
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        nonce = self.nonce

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if nonce is not UNSET:
            field_dict["nonce"] = nonce

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        nonce = d.pop("nonce", get_nonce())

        allocate_strategy_json_body_nonce = cls(
            nonce=nonce,
        )

        allocate_strategy_json_body_nonce.additional_properties = d
        return allocate_strategy_json_body_nonce

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
