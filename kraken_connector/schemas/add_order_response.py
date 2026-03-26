from typing import TYPE_CHECKING, Any, Self, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..schemas.add_order_result import AddOrderResult


@_attrs_define
class AddOrderResponse:
    """
    Attributes:
        result (Union[Unset, AddOrderResult]):
        error (Union[Unset, List[List[str]]]):
    """

    result: Union[Unset, "AddOrderResult"] = UNSET
    error: Unset | list[list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result: Unset | dict[str, Any] = UNSET
        if not isinstance(self.result, Unset):
            result = self.result.to_dict()

        error: Unset | list[list[str]] = UNSET
        if not isinstance(self.error, Unset):
            error = []
            for error_item_data in self.error:
                error_item = error_item_data

                error.append(error_item)

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
        from ..schemas.add_order_result import AddOrderResult

        d = src_dict.copy()
        _result = d.pop("result", UNSET)
        result: Unset | AddOrderResult
        if isinstance(_result, Unset):
            result = UNSET
        else:
            result = AddOrderResult.from_dict(_result)

        error = []
        _error = d.pop("error", UNSET)
        for error_item_data in _error or []:
            error_item = cast(list[str], error_item_data)

            error.append(error_item)

        add_2 = cls(
            result=result,
            error=error,
        )

        add_2.additional_properties = d
        return add_2

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
