"""Sequence number tracking for Kraken WebSocket API v2 private channels."""
from attrs import define as _attrs_define
from attrs import field as _attrs_field


@_attrs_define
class SequenceGapEvent:
    """Emitted to the message queue when a sequence gap is detected.

    Attributes:
        expected: The expected next sequence number.
        received: The sequence number actually received.
        channel: The channel where the gap was detected.
    """

    expected: int
    received: int
    channel: str


@_attrs_define
class SequenceTracker:
    """Tracks sequence numbers for private channel messages.

    Kraken sends a monotonically increasing ``sequence`` field on
    executions and balances messages (per-connection, not per-channel).
    This tracker detects gaps indicating missed messages.
    """

    _last_sequence: int | None = _attrs_field(default=None, init=False)

    def check(self, sequence: int, channel: str) -> SequenceGapEvent | None:
        """Validate sequence continuity.

        First call sets the baseline (no gap possible).
        Subsequent calls return a ``SequenceGapEvent`` if a gap is detected.

        Args:
            sequence: The sequence number from the incoming message.
            channel: The channel name (for diagnostic context).

        Returns:
            A gap event if a gap was detected, otherwise None.
        """
        if self._last_sequence is None:
            self._last_sequence = sequence
            return None

        expected = self._last_sequence + 1
        self._last_sequence = sequence

        if sequence != expected:
            return SequenceGapEvent(
                expected=expected, received=sequence, channel=channel
            )
        return None

    def reset(self) -> None:
        """Reset tracker state (called on reconnect)."""
        self._last_sequence = None
