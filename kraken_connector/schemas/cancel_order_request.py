from typing import Any, Self, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..security import get_nonce


@_attrs_define
class CancelOrderRequest:
    """
    Attributes:
        nonce (int): Nonce used in construction of `API-Sign` header. Default `get_nonce`
        txid (Union[int, str]): Open order transaction ID (txid) or user reference (userref)
    """

    txid: int | str
    nonce: int = get_nonce()
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        nonce = self.nonce
        txid: int | str

        txid = self.txid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "nonce": nonce,
                "txid": txid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Self, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        nonce = d.pop("nonce", get_nonce())

        def _parse_txid(data: object) -> int | str:
            return cast(Union[int, str], data)

        txid = _parse_txid(d.pop("txid"))

        cancel_open_order_request_body = cls(
            nonce=nonce,
            txid=txid,
        )

        cancel_open_order_request_body.additional_properties = d
        return cancel_open_order_request_body

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
