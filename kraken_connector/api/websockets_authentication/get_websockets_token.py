from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import exceptions
from ...http import HTTPAuthenticatedClient
from ...schemas.get_websockets_token_response_200 import GetWebsocketsTokenResponse200
from ...security import get_nonce, sign_message
from ...types import Response


def _get_kwargs() -> Dict[str, Any]:
    pass

    return {
        "method": "post",
        "url": "/0/private/GetWebSocketsToken",
        "data": {"nonce": get_nonce()},
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Optional[GetWebsocketsTokenResponse200]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetWebsocketsTokenResponse200.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise exceptions.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Response[GetWebsocketsTokenResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient,
) -> Response[GetWebsocketsTokenResponse200]:
    """Get Websockets Token

     An authentication token must be requested via this REST API endpoint in order to connect to and
    authenticate with our [Websockets API](https://docs.kraken.com/websockets/#authentication). The
    token should be used within 15 minutes of creation, but it does not expire once a successful
    Websockets connection and private subscription has been made and is maintained.

    **API Key Permissions Required:** `WebSocket interface - On`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetWebsocketsTokenResponse200]
    """

    kwargs = _get_kwargs()

    security_header = {
        client.hmac_msg_signature: sign_message(
            client._api_secret, kwargs["data"], kwargs["url"]
        )
    }
    # ensure client._client is set as default is `None`
    client.get_httpx_client()
    secured_client = client.with_headers(security_header)

    response = secured_client.get_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    *,
    client: HTTPAuthenticatedClient,
) -> Optional[GetWebsocketsTokenResponse200]:
    """Get Websockets Token

     An authentication token must be requested via this REST API endpoint in order to connect to and
    authenticate with our [Websockets API](https://docs.kraken.com/websockets/#authentication). The
    token should be used within 15 minutes of creation, but it does not expire once a successful
    Websockets connection and private subscription has been made and is maintained.

    **API Key Permissions Required:** `WebSocket interface - On`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetWebsocketsTokenResponse200
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient,
) -> Response[GetWebsocketsTokenResponse200]:
    """Get Websockets Token

     An authentication token must be requested via this REST API endpoint in order to connect to and
    authenticate with our [Websockets API](https://docs.kraken.com/websockets/#authentication). The
    token should be used within 15 minutes of creation, but it does not expire once a successful
    Websockets connection and private subscription has been made and is maintained.

    **API Key Permissions Required:** `WebSocket interface - On`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetWebsocketsTokenResponse200]
    """

    kwargs = _get_kwargs()

    security_header = {
        client.hmac_msg_signature: sign_message(
            client._api_secret, kwargs["data"], kwargs["url"]
        )
    }
    # ensure client._client is set as default is `None`
    client.get_async_httpx_client()
    secured_client = client.with_headers(security_header)

    response = await secured_client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: HTTPAuthenticatedClient,
) -> Optional[GetWebsocketsTokenResponse200]:
    """Get Websockets Token

     An authentication token must be requested via this REST API endpoint in order to connect to and
    authenticate with our [Websockets API](https://docs.kraken.com/websockets/#authentication). The
    token should be used within 15 minutes of creation, but it does not expire once a successful
    Websockets connection and private subscription has been made and is maintained.

    **API Key Permissions Required:** `WebSocket interface - On`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetWebsocketsTokenResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
