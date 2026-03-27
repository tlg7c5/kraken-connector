from typing import TYPE_CHECKING, Any, Self, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..schemas.list_strategies_result import (
        ListStrategiesResult,
    )


@_attrs_define
class ListStrategiesResponse:
    """
    Attributes:
        error (List[str]):
        result (Union[Unset, None, ListStrategiesResult]):
    """

    error: list[str]
    result: Union[Unset, None, "ListStrategiesResult"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        error = self.error

        result: Unset | None | dict[str, Any] = UNSET
        if not isinstance(self.result, Unset):
            result = self.result.to_dict() if self.result else None

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
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        from ..schemas.list_strategies_result import (
            ListStrategiesResult,
        )

        d = src_dict.copy()
        error = cast(list[str], d.pop("error"))

        _result = d.pop("result", UNSET)
        result: Unset | None | ListStrategiesResult
        if _result is None:
            result = None
        elif isinstance(_result, Unset):
            result = UNSET
        else:
            result = ListStrategiesResult.from_dict(_result)

        list_strategies_response_200 = cls(
            error=error,
            result=result,
        )

        list_strategies_response_200.additional_properties = d
        return list_strategies_response_200

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
