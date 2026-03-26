from typing import TYPE_CHECKING, Any, Self, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..schemas.export_status_result_item import (
        ExportStatusResultItem,
    )


@_attrs_define
class ExportStatusResponse:
    """
    Attributes:
        result (Union[Unset, List['ExportStatusResultItem']]):
        error (Union[Unset, List[str]]):
    """

    result: Unset | list["ExportStatusResultItem"] = UNSET
    error: Unset | list[str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.result, Unset):
            result = []
            for result_item_data in self.result:
                result_item = result_item_data.to_dict()

                result.append(result_item)

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
        from ..schemas.export_status_result_item import (
            ExportStatusResultItem,
        )

        d = src_dict.copy()
        result = []
        _result = d.pop("result", UNSET)
        for result_item_data in _result or []:
            result_item = ExportStatusResultItem.from_dict(result_item_data)

            result.append(result_item)

        error = cast(list[str], d.pop("error", UNSET))

        export_status_response_200 = cls(
            result=result,
            error=error,
        )

        export_status_response_200.additional_properties = d
        return export_status_response_200

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
