from typing import Any, Self, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset


@_attrs_define
class AssetTickerInfo:
    """Asset Ticker Info

    Attributes:
        a (Union[Unset, List[str]]): Ask `[<price>, <whole lot volume>, <lot volume>]`
        b (Union[Unset, List[str]]): Bid `[<price>, <whole lot volume>, <lot volume>]`
        c (Union[Unset, List[str]]): Last trade closed `[<price>, <lot volume>]`
        v (Union[Unset, List[str]]): TradeVolumeResponse `[<today>, <last 24 hours>]`
        p (Union[Unset, List[str]]): TradeVolumeResponse weighted average price `[<today>, <last 24 hours>]`
        t (Union[Unset, List[int]]): Number of trades `[<today>, <last 24 hours>]`
        l (Union[Unset, List[str]]): Low `[<today>, <last 24 hours>]`
        h (Union[Unset, List[str]]): High `[<today>, <last 24 hours>]`
        o (Union[Unset, str]): Today's opening price
    """

    a: Unset | list[str] = UNSET
    b: Unset | list[str] = UNSET
    c: Unset | list[str] = UNSET
    v: Unset | list[str] = UNSET
    p: Unset | list[str] = UNSET
    t: Unset | list[int] = UNSET
    l: Unset | list[str] = UNSET
    h: Unset | list[str] = UNSET
    o: Unset | str = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        a: Unset | list[str] = UNSET
        if not isinstance(self.a, Unset):
            a = self.a

        b: Unset | list[str] = UNSET
        if not isinstance(self.b, Unset):
            b = self.b

        c: Unset | list[str] = UNSET
        if not isinstance(self.c, Unset):
            c = self.c

        v: Unset | list[str] = UNSET
        if not isinstance(self.v, Unset):
            v = self.v

        p: Unset | list[str] = UNSET
        if not isinstance(self.p, Unset):
            p = self.p

        t: Unset | list[int] = UNSET
        if not isinstance(self.t, Unset):
            t = self.t

        l: Unset | list[str] = UNSET
        if not isinstance(self.l, Unset):
            l = self.l

        h: Unset | list[str] = UNSET
        if not isinstance(self.h, Unset):
            h = self.h

        o = self.o

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if a is not UNSET:
            field_dict["a"] = a
        if b is not UNSET:
            field_dict["b"] = b
        if c is not UNSET:
            field_dict["c"] = c
        if v is not UNSET:
            field_dict["v"] = v
        if p is not UNSET:
            field_dict["p"] = p
        if t is not UNSET:
            field_dict["t"] = t
        if l is not UNSET:
            field_dict["l"] = l
        if h is not UNSET:
            field_dict["h"] = h
        if o is not UNSET:
            field_dict["o"] = o

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        a = cast(list[str], d.pop("a", UNSET))

        b = cast(list[str], d.pop("b", UNSET))

        c = cast(list[str], d.pop("c", UNSET))

        v = cast(list[str], d.pop("v", UNSET))

        p = cast(list[str], d.pop("p", UNSET))

        t = cast(list[int], d.pop("t", UNSET))

        l = cast(list[str], d.pop("l", UNSET))

        h = cast(list[str], d.pop("h", UNSET))

        o = d.pop("o", UNSET)

        asset_ticker_info = cls(
            a=a,
            b=b,
            c=c,
            v=v,
            p=p,
            t=t,
            l=l,
            h=h,
            o=o,
        )

        asset_ticker_info.additional_properties = d
        return asset_ticker_info

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
