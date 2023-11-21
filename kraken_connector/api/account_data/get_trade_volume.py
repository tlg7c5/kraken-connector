from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import exceptions
from ...http import HTTPAuthenticatedClient
from ...schemas.volume import Volume
from ...security import get_nonce, sign_message
from ...types import Response


def _get_kwargs() -> Dict[str, Any]:
    pass

    return {
        "method": "post",
        "url": "/0/private/TradeVolume",
        "data": {"nonce": get_nonce()},
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Optional[Volume]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Volume.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise exceptions.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Response[Volume]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient,
) -> Response[Volume]:
    """Get Trade Volume

     Returns 30 day USD trading volume and resulting fee schedule for any asset pair(s) provided.
    Note: If an asset pair is on a maker/taker fee schedule, the taker side is given in `fees` and maker
    side in `fees_maker`. For pairs not on maker/taker, they will only be given in `fees`.

    **API Key Permissions Required:** `Funds permissions - Query`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[Volume]
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
) -> Optional[Volume]:
    """Get Trade Volume

     Returns 30 day USD trading volume and resulting fee schedule for any asset pair(s) provided.
    Note: If an asset pair is on a maker/taker fee schedule, the taker side is given in `fees` and maker
    side in `fees_maker`. For pairs not on maker/taker, they will only be given in `fees`.

    **API Key Permissions Required:** `Funds permissions - Query`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Volume
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient,
) -> Response[Volume]:
    """Get Trade Volume

     Returns 30 day USD trading volume and resulting fee schedule for any asset pair(s) provided.
    Note: If an asset pair is on a maker/taker fee schedule, the taker side is given in `fees` and maker
    side in `fees_maker`. For pairs not on maker/taker, they will only be given in `fees`.

    **API Key Permissions Required:** `Funds permissions - Query`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[Volume]
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
) -> Optional[Volume]:
    """Get Trade Volume

     Returns 30 day USD trading volume and resulting fee schedule for any asset pair(s) provided.
    Note: If an asset pair is on a maker/taker fee schedule, the taker side is given in `fees` and maker
    side in `fees_maker`. For pairs not on maker/taker, they will only be given in `fees`.

    **API Key Permissions Required:** `Funds permissions - Query`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Volume
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
