"""Tests for SequenceTracker and SequenceGapEvent."""
from kraken_connector.ws.sequence import SequenceGapEvent, SequenceTracker


class TestSequenceTracker:
    def test_first_message_sets_baseline(self) -> None:
        tracker = SequenceTracker()
        result = tracker.check(5, "executions")
        assert result is None

    def test_consecutive_sequences_no_gap(self) -> None:
        tracker = SequenceTracker()
        tracker.check(1, "executions")
        assert tracker.check(2, "executions") is None
        assert tracker.check(3, "balances") is None

    def test_gap_detected(self) -> None:
        tracker = SequenceTracker()
        tracker.check(1, "executions")
        gap = tracker.check(5, "balances")
        assert gap is not None
        assert gap.expected == 2
        assert gap.received == 5
        assert gap.channel == "balances"

    def test_reset_clears_state(self) -> None:
        tracker = SequenceTracker()
        tracker.check(10, "executions")
        tracker.reset()
        # After reset, first message sets baseline again.
        result = tracker.check(1, "executions")
        assert result is None


class TestSequenceGapEvent:
    def test_attributes(self) -> None:
        event = SequenceGapEvent(expected=3, received=7, channel="executions")
        assert event.expected == 3
        assert event.received == 7
        assert event.channel == "executions"
