"""Tests for WebSocket v2 message models and dispatcher."""
import json

import pytest

from kraken_connector.types import Unset
from kraken_connector.ws.channels.balances import (
    BalanceLedgerUpdate,
    BalanceSnapshot,
    BalanceWallet,
)
from kraken_connector.ws.channels.book import BookData, BookLevel
from kraken_connector.ws.channels.executions import ExecutionData, ExecutionFee
from kraken_connector.ws.channels.heartbeat import HeartbeatMessage
from kraken_connector.ws.channels.instrument import (
    InstrumentAsset,
    InstrumentData,
    InstrumentPair,
)
from kraken_connector.ws.channels.ohlc import OHLCData
from kraken_connector.ws.channels.status import StatusData
from kraken_connector.ws.channels.ticker import TickerData
from kraken_connector.ws.channels.trade import TradeData
from kraken_connector.ws.dispatcher import parse_message
from kraken_connector.ws.envelopes import (
    PingRequest,
    PongResponse,
    WSDataMessage,
    WSErrorResponse,
    WSRequest,
    WSResponse,
)
from kraken_connector.ws.subscribe import (
    BalancesParams,
    BookParams,
    ExecutionsParams,
    OHLCParams,
    TickerParams,
)
from kraken_connector.ws.trading import (
    AddOrderParams,
    AddOrderResult,
    BatchAddParams,
    BatchAddResult,
    BatchCancelParams,
    BatchCancelResult,
    CancelAllParams,
    CancelAllResult,
    CancelOrderParams,
    ConditionalClose,
    EditOrderParams,
    EditOrderResult,
    OrderTrigger,
)

# ---------------------------------------------------------------------------
# Envelope round-trips
# ---------------------------------------------------------------------------


class TestEnvelopes:
    def test_ws_request_round_trip(self) -> None:
        req = WSRequest(method="subscribe", params={"channel": "ticker"}, req_id=42)
        d = req.to_dict()
        assert d == {
            "method": "subscribe",
            "params": {"channel": "ticker"},
            "req_id": 42,
        }
        restored = WSRequest.from_dict(d)
        assert restored.method == "subscribe"
        assert restored.req_id == 42

    def test_ws_request_omits_unset_req_id(self) -> None:
        req = WSRequest(method="ping", params={})
        d = req.to_dict()
        assert "req_id" not in d

    def test_ws_response_round_trip(self) -> None:
        resp = WSResponse(
            method="subscribe",
            result={"channel": "ticker", "symbol": "BTC/USD"},
            success=True,
            time_in="2023-09-25T09:04:31.742599Z",
            time_out="2023-09-25T09:04:31.742648Z",
            req_id=42,
        )
        d = resp.to_dict()
        restored = WSResponse.from_dict(d)
        assert restored.method == "subscribe"
        assert restored.success is True
        assert restored.req_id == 42

    def test_ws_error_response_round_trip(self) -> None:
        resp = WSErrorResponse(
            method="subscribe",
            error="Currency pair not supported XBT/USD",
            success=False,
            time_in="2023-09-25T09:04:31.742599Z",
            time_out="2023-09-25T09:04:31.742648Z",
        )
        d = resp.to_dict()
        assert d["success"] is False
        assert "req_id" not in d
        restored = WSErrorResponse.from_dict(d)
        assert restored.error == "Currency pair not supported XBT/USD"

    def test_ws_data_message_round_trip(self) -> None:
        msg = WSDataMessage(
            channel="ticker", type="snapshot", data=[{"symbol": "BTC/USD"}]
        )
        d = msg.to_dict()
        restored = WSDataMessage.from_dict(d)
        assert restored.channel == "ticker"
        assert restored.type == "snapshot"
        assert len(restored.data) == 1

    def test_ping_request_round_trip(self) -> None:
        ping = PingRequest(req_id=101)
        d = ping.to_dict()
        assert d == {"method": "ping", "req_id": 101}

    def test_ping_request_omits_unset(self) -> None:
        ping = PingRequest()
        d = ping.to_dict()
        assert d == {"method": "ping"}

    def test_pong_response_round_trip(self) -> None:
        pong = PongResponse(
            req_id=101,
            time_in="2023-09-24T14:10:23.799685Z",
            time_out="2023-09-24T14:10:23.799703Z",
        )
        d = pong.to_dict()
        assert d["method"] == "pong"
        restored = PongResponse.from_dict(d)
        assert restored.req_id == 101

    def test_data_message_sequence_default_unset(self) -> None:
        msg = WSDataMessage(channel="ticker", type="snapshot", data=[])
        d = msg.to_dict()
        assert "sequence" not in d

    def test_data_message_sequence_roundtrip(self) -> None:
        msg = WSDataMessage(channel="executions", type="update", data=[], sequence=42)
        d = msg.to_dict()
        assert d["sequence"] == 42
        restored = WSDataMessage.from_dict(d)
        assert restored.sequence == 42


# ---------------------------------------------------------------------------
# Channel data round-trips
# ---------------------------------------------------------------------------


class TestChannelData:
    def test_ticker_data(self) -> None:
        raw = {
            "symbol": "BTC/USD",
            "bid": 26000.0,
            "bid_qty": 1.5,
            "ask": 26001.0,
            "ask_qty": 2.0,
            "last": 26000.5,
            "volume": 1234.56,
            "vwap": 25999.0,
            "low": 25500.0,
            "high": 26500.0,
            "change": 100.0,
            "change_pct": 0.38,
            "timestamp": "2023-09-25T10:00:00.000000Z",
        }
        ticker = TickerData.from_dict(raw)
        assert ticker.symbol == "BTC/USD"
        assert ticker.bid == 26000.0
        assert ticker.to_dict() == raw

    def test_book_data_with_checksum(self) -> None:
        raw = {
            "symbol": "BTC/USD",
            "bids": [{"price": 26000.0, "qty": 1.5}],
            "asks": [{"price": 26001.0, "qty": 2.0}],
            "checksum": 974942666,
            "timestamp": "2023-09-25T10:00:00.000000Z",
        }
        book = BookData.from_dict(raw)
        assert book.symbol == "BTC/USD"
        assert len(book.bids) == 1
        assert isinstance(book.bids[0], BookLevel)
        assert book.bids[0].price == 26000.0
        assert book.checksum == 974942666
        assert book.to_dict() == raw

    def test_book_data_without_checksum(self) -> None:
        raw = {
            "symbol": "BTC/USD",
            "bids": [{"price": 26000.0, "qty": 1.5}],
            "asks": [],
        }
        book = BookData.from_dict(raw)
        assert isinstance(book.checksum, Unset)
        d = book.to_dict()
        assert "checksum" not in d

    def test_trade_data(self) -> None:
        raw = {
            "symbol": "BTC/USD",
            "side": "buy",
            "qty": 0.5,
            "price": 26000.0,
            "ord_type": "market",
            "trade_id": 12345,
            "timestamp": "2023-09-25T10:00:00.000000Z",
        }
        trade = TradeData.from_dict(raw)
        assert trade.side == "buy"
        assert trade.trade_id == 12345
        assert trade.to_dict() == raw

    def test_ohlc_data(self) -> None:
        raw = {
            "symbol": "BTC/USD",
            "open": 26000.0,
            "high": 26500.0,
            "low": 25500.0,
            "close": 26200.0,
            "vwap": 26100.0,
            "trades": 150,
            "volume": 500.0,
            "interval": 60,
            "interval_begin": "2023-09-25T10:00:00.000000Z",
            "timestamp": "2023-09-25T11:00:00.000000Z",
        }
        ohlc = OHLCData.from_dict(raw)
        assert ohlc.interval == 60
        assert ohlc.trades == 150
        assert ohlc.to_dict() == raw

    def test_instrument_data(self) -> None:
        raw = {
            "assets": [
                {
                    "id": "BTC",
                    "status": "enabled",
                    "precision": 10,
                    "precision_display": 5,
                    "borrowable": True,
                    "collateral_value": 1.0,
                }
            ],
            "pairs": [
                {
                    "symbol": "BTC/USD",
                    "base": "BTC",
                    "quote": "USD",
                    "status": "online",
                    "qty_precision": 8,
                    "qty_increment": 0.00000001,
                    "qty_min": 0.0001,
                    "price_precision": 1,
                    "price_increment": 0.1,
                    "cost_precision": 5,
                    "cost_min": 0.5,
                    "marginable": True,
                    "margin_initial": 0.2,
                }
            ],
        }
        inst = InstrumentData.from_dict(raw)
        assert len(inst.assets) == 1
        assert isinstance(inst.assets[0], InstrumentAsset)
        assert inst.assets[0].id == "BTC"
        assert inst.assets[0].collateral_value == 1.0
        assert len(inst.pairs) == 1
        assert isinstance(inst.pairs[0], InstrumentPair)
        assert inst.pairs[0].symbol == "BTC/USD"
        assert inst.pairs[0].margin_initial == 0.2

    def test_execution_data_order_event(self) -> None:
        raw = {
            "exec_type": "new",
            "order_id": "OXXXXX-XXXXX-XXXXXX",
            "symbol": "BTC/USD",
            "order_status": "new",
            "side": "buy",
            "order_type": "limit",
            "order_qty": 1.0,
            "limit_price": 26000.0,
            "time_in_force": "gtc",
            "timestamp": "2023-09-25T10:00:00.000000Z",
        }
        exec_data = ExecutionData.from_dict(raw)
        assert exec_data.exec_type == "new"
        assert exec_data.order_id == "OXXXXX-XXXXX-XXXXXX"
        assert exec_data.limit_price == 26000.0
        assert isinstance(exec_data.exec_id, Unset)

    def test_execution_data_trade_event_with_fees(self) -> None:
        raw = {
            "exec_type": "trade",
            "order_id": "OXXXXX-XXXXX-XXXXXX",
            "exec_id": "TXXXXX-XXXXX-XXXXXX",
            "trade_id": 99999,
            "last_qty": 0.5,
            "last_price": 26000.0,
            "cost": 13000.0,
            "liquidity_ind": "t",
            "fees": [{"asset": "USD", "qty": 13.0}],
            "fee_usd_equiv": 13.0,
        }
        exec_data = ExecutionData.from_dict(raw)
        assert exec_data.exec_type == "trade"
        assert not isinstance(exec_data.fees, Unset)
        assert len(exec_data.fees) == 1
        assert isinstance(exec_data.fees[0], ExecutionFee)
        assert exec_data.fees[0].asset == "USD"
        d = exec_data.to_dict()
        assert d["fees"] == [{"asset": "USD", "qty": 13.0}]

    def test_balance_snapshot(self) -> None:
        raw = {
            "asset": "BTC",
            "asset_class": "currency",
            "balance": 1.5,
            "wallets": [{"type": "spot", "id": "main", "balance": 1.5}],
        }
        snap = BalanceSnapshot.from_dict(raw)
        assert snap.asset == "BTC"
        assert len(snap.wallets) == 1
        assert isinstance(snap.wallets[0], BalanceWallet)
        assert snap.wallets[0].type == "spot"

    def test_balance_ledger_update(self) -> None:
        raw = {
            "asset": "USD",
            "asset_class": "currency",
            "amount": -100.0,
            "balance": 9900.0,
            "fee": 0.26,
            "ledger_id": "LXXXXX",
            "ref_id": "TXXXXX",
            "timestamp": "2023-09-25T10:00:00.000000Z",
            "type": "trade",
            "wallet_type": "spot",
            "wallet_id": "main",
            "subtype": "spotfromfutures",
        }
        update = BalanceLedgerUpdate.from_dict(raw)
        assert update.amount == -100.0
        assert update.subtype == "spotfromfutures"
        assert isinstance(update.category, Unset)
        d = update.to_dict()
        assert "subtype" in d
        assert "category" not in d

    def test_heartbeat_message(self) -> None:
        msg = HeartbeatMessage()
        assert msg.channel == "heartbeat"
        assert msg.to_dict() == {"channel": "heartbeat"}

    def test_status_data(self) -> None:
        raw = {
            "system": "online",
            "api_version": "v2",
            "connection_id": 13834774380200032777,
            "version": "2.0.0",
        }
        status = StatusData.from_dict(raw)
        assert status.system == "online"
        assert status.connection_id == 13834774380200032777
        assert status.to_dict() == raw


# ---------------------------------------------------------------------------
# Subscription params
# ---------------------------------------------------------------------------


class TestSubscribeParams:
    def test_ticker_params_omits_unset(self) -> None:
        params = TickerParams(symbol=["BTC/USD"])
        d = params.to_dict()
        assert d == {"channel": "ticker", "symbol": ["BTC/USD"]}
        assert "event_trigger" not in d

    def test_ticker_params_with_trigger(self) -> None:
        params = TickerParams(symbol=["BTC/USD"], event_trigger="bbo")
        d = params.to_dict()
        assert d["event_trigger"] == "bbo"

    def test_book_params_defaults(self) -> None:
        params = BookParams(symbol=["BTC/USD"])
        d = params.to_dict()
        assert d["depth"] == 10

    def test_ohlc_params_round_trip(self) -> None:
        params = OHLCParams(symbol=["ETH/USD"], interval=60)
        d = params.to_dict()
        restored = OHLCParams.from_dict(d)
        assert restored.interval == 60
        assert restored.symbol == ["ETH/USD"]

    def test_executions_params(self) -> None:
        params = ExecutionsParams(
            token="test-token",  # noqa: S106
            snap_orders=True,
            ratecounter=True,
        )
        d = params.to_dict()
        assert d["token"] == "test-token"  # noqa: S105
        assert d["snap_orders"] is True
        assert d["ratecounter"] is True
        assert "snap_trades" not in d

    def test_balances_params(self) -> None:
        params = BalancesParams(token="test-token", snapshot=True)  # noqa: S106
        d = params.to_dict()
        assert d["snapshot"] is True


# ---------------------------------------------------------------------------
# Trading params + results
# ---------------------------------------------------------------------------


class TestTradingModels:
    def test_add_order_params_minimal(self) -> None:
        params = AddOrderParams(
            symbol="BTC/USD",
            side="buy",
            order_type="limit",
            order_qty=1.0,
            token="test-token",  # noqa: S106
            limit_price=26000.0,
        )
        d = params.to_dict()
        assert d["symbol"] == "BTC/USD"
        assert d["limit_price"] == 26000.0
        assert "triggers" not in d
        assert "conditional" not in d

    def test_add_order_params_with_trigger(self) -> None:
        trigger = OrderTrigger(reference="last", price=25000.0)
        params = AddOrderParams(
            symbol="BTC/USD",
            side="buy",
            order_type="stop-loss",
            order_qty=1.0,
            token="test-token",  # noqa: S106
            triggers=trigger,
        )
        d = params.to_dict()
        assert d["triggers"] == {"reference": "last", "price": 25000.0}

    def test_add_order_params_with_conditional(self) -> None:
        cond = ConditionalClose(order_type="limit", limit_price=27000.0)
        params = AddOrderParams(
            symbol="BTC/USD",
            side="buy",
            order_type="limit",
            order_qty=1.0,
            token="test-token",  # noqa: S106
            limit_price=26000.0,
            conditional=cond,
        )
        d = params.to_dict()
        assert d["conditional"] == {"order_type": "limit", "limit_price": 27000.0}
        restored = AddOrderParams.from_dict(d)
        assert not isinstance(restored.conditional, Unset)
        assert restored.conditional.limit_price == 27000.0

    def test_edit_order_params(self) -> None:
        params = EditOrderParams(
            order_id="OXXXXX",
            symbol="BTC/USD",
            token="test-token",  # noqa: S106
            limit_price=26500.0,
        )
        d = params.to_dict()
        assert d["order_id"] == "OXXXXX"
        assert d["limit_price"] == 26500.0
        assert "order_qty" not in d

    def test_cancel_order_params(self) -> None:
        params = CancelOrderParams(
            token="test-token",  # noqa: S106
            order_id=["OXXXXX-1", "OXXXXX-2"],
        )
        d = params.to_dict()
        assert d["order_id"] == ["OXXXXX-1", "OXXXXX-2"]
        assert "cl_ord_id" not in d

    def test_cancel_all_params(self) -> None:
        params = CancelAllParams(token="test-token")  # noqa: S106
        assert params.to_dict() == {"token": "test-token"}

    def test_batch_add_params(self) -> None:
        order1 = AddOrderParams(
            symbol="BTC/USD",
            side="buy",
            order_type="limit",
            order_qty=1.0,
            token="test-token",  # noqa: S106
            limit_price=26000.0,
        )
        order2 = AddOrderParams(
            symbol="BTC/USD",
            side="sell",
            order_type="limit",
            order_qty=0.5,
            token="test-token",  # noqa: S106
            limit_price=27000.0,
        )
        batch = BatchAddParams(
            symbol="BTC/USD",
            token="test-token",  # noqa: S106
            orders=[order1, order2],
        )
        d = batch.to_dict()
        assert len(d["orders"]) == 2
        assert d["orders"][0]["side"] == "buy"
        restored = BatchAddParams.from_dict(d)
        assert len(restored.orders) == 2
        assert isinstance(restored.orders[0], AddOrderParams)

    def test_batch_cancel_params(self) -> None:
        params = BatchCancelParams(
            token="test-token",  # noqa: S106
            orders=["OXXXXX-1", "OXXXXX-2"],
        )
        d = params.to_dict()
        assert d["orders"] == ["OXXXXX-1", "OXXXXX-2"]

    def test_add_order_result(self) -> None:
        raw = {"order_id": "OXXXXX", "warnings": ["warning1"]}
        result = AddOrderResult.from_dict(raw)
        assert result.order_id == "OXXXXX"
        assert not isinstance(result.warnings, Unset)
        assert result.warnings == ["warning1"]
        assert isinstance(result.cl_ord_id, Unset)

    def test_edit_order_result(self) -> None:
        raw = {"order_id": "ONEW", "original_order_id": "OOLD"}
        result = EditOrderResult.from_dict(raw)
        assert result.order_id == "ONEW"
        assert result.original_order_id == "OOLD"

    def test_cancel_all_result(self) -> None:
        raw = {"count": 5}
        result = CancelAllResult.from_dict(raw)
        assert result.count == 5
        assert isinstance(result.warnings, Unset)

    def test_batch_add_result(self) -> None:
        raw = {"orders": [{"order_id": "O1"}, {"order_id": "O2"}]}
        result = BatchAddResult.from_dict(raw)
        assert len(result.orders) == 2
        assert isinstance(result.orders[0], AddOrderResult)

    def test_batch_cancel_result(self) -> None:
        raw = {"count": 3, "warnings": ["partial fill"]}
        result = BatchCancelResult.from_dict(raw)
        assert result.count == 3
        assert result.warnings == ["partial fill"]


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


class TestDispatcher:
    def test_heartbeat(self) -> None:
        raw = json.dumps({"channel": "heartbeat"})
        msg = parse_message(raw)
        assert isinstance(msg, HeartbeatMessage)

    def test_pong(self) -> None:
        raw = json.dumps(
            {"method": "pong", "req_id": 101, "time_in": "T1", "time_out": "T2"}
        )
        msg = parse_message(raw)
        assert isinstance(msg, PongResponse)
        assert msg.req_id == 101

    def test_success_response(self) -> None:
        raw = json.dumps(
            {
                "method": "subscribe",
                "result": {"channel": "ticker", "symbol": "BTC/USD"},
                "success": True,
                "time_in": "T1",
                "time_out": "T2",
                "req_id": 42,
            }
        )
        msg = parse_message(raw)
        assert isinstance(msg, WSResponse)
        assert msg.success is True
        assert msg.req_id == 42

    def test_error_response(self) -> None:
        raw = json.dumps(
            {
                "method": "subscribe",
                "error": "Currency pair not supported",
                "success": False,
                "time_in": "T1",
                "time_out": "T2",
            }
        )
        msg = parse_message(raw)
        assert isinstance(msg, WSErrorResponse)
        assert msg.error == "Currency pair not supported"

    def test_ticker_data_message(self) -> None:
        raw = json.dumps(
            {
                "channel": "ticker",
                "type": "snapshot",
                "data": [
                    {
                        "symbol": "BTC/USD",
                        "bid": 26000.0,
                        "bid_qty": 1.5,
                        "ask": 26001.0,
                        "ask_qty": 2.0,
                        "last": 26000.5,
                        "volume": 1234.56,
                        "vwap": 25999.0,
                        "low": 25500.0,
                        "high": 26500.0,
                        "change": 100.0,
                        "change_pct": 0.38,
                        "timestamp": "2023-09-25T10:00:00.000000Z",
                    }
                ],
            }
        )
        msg = parse_message(raw)
        assert isinstance(msg, WSDataMessage)
        assert msg.channel == "ticker"
        assert len(msg.data) == 1
        assert isinstance(msg.data[0], TickerData)
        assert msg.data[0].symbol == "BTC/USD"

    def test_book_data_message(self) -> None:
        raw = json.dumps(
            {
                "channel": "book",
                "type": "update",
                "data": [
                    {
                        "symbol": "BTC/USD",
                        "bids": [{"price": 26000.0, "qty": 0.0}],
                        "asks": [{"price": 26001.0, "qty": 3.0}],
                        "checksum": 123456,
                    }
                ],
            }
        )
        msg = parse_message(raw)
        assert isinstance(msg, WSDataMessage)
        assert isinstance(msg.data[0], BookData)
        assert msg.data[0].bids[0].qty == 0.0

    def test_status_data_message(self) -> None:
        raw = json.dumps(
            {
                "channel": "status",
                "type": "update",
                "data": [
                    {
                        "system": "online",
                        "api_version": "v2",
                        "connection_id": 123,
                        "version": "2.0.0",
                    }
                ],
            }
        )
        msg = parse_message(raw)
        assert isinstance(msg, WSDataMessage)
        assert isinstance(msg.data[0], StatusData)
        assert msg.data[0].system == "online"

    def test_executions_data_message(self) -> None:
        raw = json.dumps(
            {
                "channel": "executions",
                "type": "update",
                "data": [
                    {
                        "exec_type": "new",
                        "order_id": "OXXXXX",
                        "symbol": "BTC/USD",
                    }
                ],
            }
        )
        msg = parse_message(raw)
        assert isinstance(msg, WSDataMessage)
        assert isinstance(msg.data[0], ExecutionData)

    def test_balances_snapshot_message(self) -> None:
        raw = json.dumps(
            {
                "channel": "balances",
                "type": "snapshot",
                "data": [
                    {
                        "asset": "BTC",
                        "asset_class": "currency",
                        "balance": 1.5,
                        "wallets": [{"type": "spot", "id": "main", "balance": 1.5}],
                    }
                ],
            }
        )
        msg = parse_message(raw)
        assert isinstance(msg, WSDataMessage)
        assert isinstance(msg.data[0], BalanceSnapshot)

    def test_balances_update_message(self) -> None:
        raw = json.dumps(
            {
                "channel": "balances",
                "type": "update",
                "data": [
                    {
                        "asset": "USD",
                        "asset_class": "currency",
                        "amount": -100.0,
                        "balance": 9900.0,
                        "fee": 0.26,
                        "ledger_id": "LXXXXX",
                        "ref_id": "TXXXXX",
                        "timestamp": "2023-09-25T10:00:00.000000Z",
                        "type": "trade",
                        "wallet_type": "spot",
                        "wallet_id": "main",
                    }
                ],
            }
        )
        msg = parse_message(raw)
        assert isinstance(msg, WSDataMessage)
        assert isinstance(msg.data[0], BalanceLedgerUpdate)

    def test_unknown_channel_returns_raw(self) -> None:
        raw = json.dumps(
            {
                "channel": "future_channel",
                "type": "update",
                "data": [{"foo": "bar"}],
            }
        )
        msg = parse_message(raw)
        assert isinstance(msg, WSDataMessage)
        assert msg.data[0] == {"foo": "bar"}

    def test_unrecognized_message_raises(self) -> None:
        raw = json.dumps({"unexpected": "format"})
        with pytest.raises(ValueError, match="Unrecognized"):
            parse_message(raw)
