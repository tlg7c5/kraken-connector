from io import BytesIO
from typing import Any, Self

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, File, FileJsonType, Unset


@_attrs_define
class RetrieveExportResponse:
    """
    Attributes:
        report (Union[Unset, File]): Binary zip archive containing the report
    """

    report: Unset | File = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        report: Unset | FileJsonType = UNSET
        if not isinstance(self.report, Unset):
            report = self.report.to_tuple()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if report is not UNSET:
            field_dict["report"] = report

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        _report = d.pop("report", UNSET)
        report: Unset | File
        report = UNSET if isinstance(_report, Unset) else File(payload=BytesIO(_report))

        retrieve_export_response_200 = cls(
            report=report,
        )

        retrieve_export_response_200.additional_properties = d
        return retrieve_export_response_200

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
