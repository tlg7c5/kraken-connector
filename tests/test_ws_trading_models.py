"""Tests for Phase 6 — new trading model serialization."""
from kraken_connector.types import Unset
from kraken_connector.ws.trading import (
    AmendOrderParams,
    AmendOrderResult,
    CancelAllOrdersAfterParams,
    CancelAllOrdersAfterResult,
)


class TestAmendOrderParams:
    def test_roundtrip(self) -> None:
        raw = {
            "order_id": "OTEST-123",
            "token": "t",
            "order_qty": 2.5,
            "limit_price": 26000.0,
            "trigger_price": 25900.0,
            "trigger_price_type": "last",
        }
        params = AmendOrderParams.from_dict(raw)
        assert params.order_id == "OTEST-123"
        assert params.order_qty == 2.5
        assert params.trigger_price == 25900.0
        assert params.to_dict() == raw

    def test_minimal(self) -> None:
        params = AmendOrderParams(order_id="O1", token="t")  # noqa: S106
        d = params.to_dict()
        assert d == {"order_id": "O1", "token": "t"}
        assert isinstance(params.order_qty, Unset)
        assert isinstance(params.limit_price, Unset)


class TestAmendOrderResult:
    def test_roundtrip(self) -> None:
        raw = {"order_id": "O1", "amend_id": "A1"}
        result = AmendOrderResult.from_dict(raw)
        assert result.order_id == "O1"
        assert result.amend_id == "A1"
        assert isinstance(result.warnings, Unset)
        assert result.to_dict() == raw

    def test_with_warnings(self) -> None:
        raw = {"order_id": "O1", "amend_id": "A1", "warnings": ["low balance"]}
        result = AmendOrderResult.from_dict(raw)
        assert result.warnings == ["low balance"]
        assert result.to_dict() == raw


class TestCancelAllOrdersAfterParams:
    def test_roundtrip(self) -> None:
        raw = {"token": "t", "timeout": 60}
        params = CancelAllOrdersAfterParams.from_dict(raw)
        assert params.timeout == 60
        assert params.to_dict() == raw

    def test_disable(self) -> None:
        params = CancelAllOrdersAfterParams(token="t", timeout=0)  # noqa: S106
        assert params.timeout == 0
        assert params.to_dict() == {"token": "t", "timeout": 0}


class TestCancelAllOrdersAfterResult:
    def test_roundtrip(self) -> None:
        raw = {
            "currentTime": "2024-01-01T00:00:00Z",
            "triggerTime": "2024-01-01T00:01:00Z",
        }
        result = CancelAllOrdersAfterResult.from_dict(raw)
        assert result.current_time == "2024-01-01T00:00:00Z"
        assert result.trigger_time == "2024-01-01T00:01:00Z"
        assert result.to_dict() == raw

    def test_from_dict(self) -> None:
        raw = {
            "currentTime": "2024-06-15T12:00:00Z",
            "triggerTime": "2024-06-15T12:01:00Z",
        }
        result = CancelAllOrdersAfterResult.from_dict(raw)
        assert result.current_time == "2024-06-15T12:00:00Z"
