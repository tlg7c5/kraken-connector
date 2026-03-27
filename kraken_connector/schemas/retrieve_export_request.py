from typing import Any, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..security import get_nonce


@_attrs_define
class RetrieveExportRequest:
    """
    Attributes:
        nonce (int): Nonce used in construction of `API-Sign` header.
            Default `get_nonce`
        id (str): Report ID to retrieve
    """

    id: str
    nonce: int = get_nonce()
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        nonce = self.nonce
        id = self.id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "nonce": nonce,
                "id": id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        nonce = d.pop("nonce", get_nonce())

        id = d.pop("id")

        retrieve_export_data = cls(
            nonce=nonce,
            id=id,
        )

        retrieve_export_data.additional_properties = d
        return retrieve_export_data

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
