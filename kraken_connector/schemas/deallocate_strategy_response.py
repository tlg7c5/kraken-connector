from typing import Any, Self, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset


@_attrs_define
class DeallocateStrategyResponse:
    """
    Attributes:
        error (List[str]):
        result (Union[Unset, None, bool]): Will return `true` when the operation is successful, null when an error
            occurred.
    """

    error: list[str]
    result: Unset | None | bool = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        error = self.error

        result = self.result

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "error": error,
            }
        )
        if result is not UNSET:
            field_dict["result"] = result

        return field_dict

    @classmethod
    def from_dict(cls: Self, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        error = cast(list[str], d.pop("error"))

        result = d.pop("result", UNSET)

        deallocate_strategy_response_200 = cls(
            error=error,
            result=result,
        )

        deallocate_strategy_response_200.additional_properties = d
        return deallocate_strategy_response_200

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
