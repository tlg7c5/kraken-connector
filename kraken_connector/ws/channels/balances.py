"""Balances channel data models for Kraken WebSocket API v2."""
from typing import Any, Self

from attrs import define as _attrs_define

from ...types import UNSET, Unset


@_attrs_define
class BalanceWallet:
    """Wallet entry within a balance snapshot.

    Attributes:
        type: Wallet type ("spot" or "earn").
        id: Wallet identifier (e.g. "main", "flex", "bonded").
        balance: Wallet-specific balance.
    """

    type: str
    id: str
    balance: float

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "id": self.id, "balance": self.balance}

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(type=d.pop("type"), id=d.pop("id"), balance=d.pop("balance"))


@_attrs_define
class BalanceSnapshot:
    """Balance snapshot data from the v2 balances channel.

    Attributes:
        asset: Asset symbol (e.g. "BTC").
        asset_class: Asset class (e.g. "currency").
        balance: Total balance.
        wallets: List of wallet entries.
    """

    asset: str
    asset_class: str
    balance: float
    wallets: list[BalanceWallet]

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset": self.asset,
            "asset_class": self.asset_class,
            "balance": self.balance,
            "wallets": [w.to_dict() for w in self.wallets],
        }

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        wallets = [BalanceWallet.from_dict(w) for w in d.pop("wallets", [])]
        return cls(
            asset=d.pop("asset"),
            asset_class=d.pop("asset_class"),
            balance=d.pop("balance"),
            wallets=wallets,
        )


@_attrs_define
class BalanceLedgerUpdate:
    """Ledger update data from the v2 balances channel.

    Attributes:
        asset: Asset symbol.
        asset_class: Asset class.
        amount: Change amount.
        balance: Current total balance.
        fee: Fee amount.
        ledger_id: Ledger entry identifier.
        ref_id: Reference identifier (e.g. trade_id).
        timestamp: RFC3339 timestamp.
        type: Ledger type (deposit, withdrawal, trade, margin, etc.).
        wallet_type: Wallet type ("spot" or "earn").
        wallet_id: Wallet identifier.
        subtype: Ledger subtype.
        category: Detailed categorization.
    """

    asset: str
    asset_class: str
    amount: float
    balance: float
    fee: float
    ledger_id: str
    ref_id: str
    timestamp: str
    type: str
    wallet_type: str
    wallet_id: str
    subtype: Unset | str = UNSET
    category: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "asset": self.asset,
            "asset_class": self.asset_class,
            "amount": self.amount,
            "balance": self.balance,
            "fee": self.fee,
            "ledger_id": self.ledger_id,
            "ref_id": self.ref_id,
            "timestamp": self.timestamp,
            "type": self.type,
            "wallet_type": self.wallet_type,
            "wallet_id": self.wallet_id,
        }
        if not isinstance(self.subtype, Unset):
            field_dict["subtype"] = self.subtype
        if not isinstance(self.category, Unset):
            field_dict["category"] = self.category
        return field_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> Self:
        d = src_dict.copy()
        return cls(
            asset=d.pop("asset"),
            asset_class=d.pop("asset_class"),
            amount=d.pop("amount"),
            balance=d.pop("balance"),
            fee=d.pop("fee"),
            ledger_id=d.pop("ledger_id"),
            ref_id=d.pop("ref_id"),
            timestamp=d.pop("timestamp"),
            type=d.pop("type"),
            wallet_type=d.pop("wallet_type"),
            wallet_id=d.pop("wallet_id"),
            subtype=d.pop("subtype", UNSET),
            category=d.pop("category", UNSET),
        )
