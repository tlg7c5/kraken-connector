"""Websockets Client to connect to Kraken Websockets API."""
import logging
from typing import Any, Dict, Optional

import websockets
from attrs import define, field
from websockets.client import WebSocketClientProtocol

logger = logging.getLogger(__name__)


@define
class KrakenWSConnection:
    """A Client to maintain connections to Kraken Exchange's Websocket API.

    The following are accepted as keyword arguments and will be used to construct websockets' Clients internally:

        ``base_url``: The base URL for the API, all requests are made to a relative path to this URL

        ``websocket_args``: A dictionary of additional arguments to be passed to the ``websockets.WebSocketClientProtocol`` constructor.


    Attributes:
        raise_on_unexpected_status: Whether or not to raise an errors.UnexpectedStatus if the API returns a
            status code that was not documented in the source OpenAPI document. Can also be provided as a keyword
            argument to the constructor.
    """

    raise_on_unexpected_status: bool = field(default=False, kw_only=True)
    _base_url: str

    _api_key: Optional[str] = field(default=None, kw_only=True)
    _api_secret: Optional[str] = field(default=None, kw_only=True)

    _websocket_args: Dict[str, Any] = field(factory=dict, kw_only=True)
    _websocket: Optional[WebSocketClientProtocol] = field(default=None, init=False)
    _private_websocket: Optional[WebSocketClientProtocol] = field(
        default=None, init=False
    )

    async def connect_public(self):
        self._websocket = await websockets.connect(self._base_url)
        logger.info("Connected to WebSocket server")

    async def send_message(self, message):
        await self._websocket.send(message)
        logger.info("Message sent:", message)

    async def receive_message(self):
        message = await self._websocket.recv()
        logger.info("Message received:", message)

    async def process_events(self):
        await self.connect()
        while True:
            await self.receive_message()

    async def disconnect(self):
        await self._websocket.close()
        logger.info("Disconnected from WebSocket server")
