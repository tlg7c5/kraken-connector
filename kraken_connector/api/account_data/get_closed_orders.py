from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import exceptions
from ...http import HTTPAuthenticatedClient
from ...schemas.closed_2 import Closed2
from ...security import get_nonce, sign_message
from ...types import Response


def _get_kwargs() -> Dict[str, Any]:
    pass

    return {
        "method": "post",
        "url": "/0/private/ClosedOrders",
        "data": {"nonce": get_nonce()},
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Optional[Closed2]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Closed2.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise exceptions.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Response[Closed2]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient,
) -> Response[Closed2]:
    """Get Closed Orders

     Retrieve information about orders that have been closed (filled or cancelled). 50 results are
    returned at a time, the most recent by default.

    **Note:** If an order's tx ID is given for `start` or `end` time, the order's opening time
    (`opentm`) is used

    **API Key Permissions Required:** `Orders and trades - Query closed orders & trades`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[Closed2]
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
) -> Optional[Closed2]:
    """Get Closed Orders

     Retrieve information about orders that have been closed (filled or cancelled). 50 results are
    returned at a time, the most recent by default.

    **Note:** If an order's tx ID is given for `start` or `end` time, the order's opening time
    (`opentm`) is used

    **API Key Permissions Required:** `Orders and trades - Query closed orders & trades`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Closed2
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient,
) -> Response[Closed2]:
    """Get Closed Orders

     Retrieve information about orders that have been closed (filled or cancelled). 50 results are
    returned at a time, the most recent by default.

    **Note:** If an order's tx ID is given for `start` or `end` time, the order's opening time
    (`opentm`) is used

    **API Key Permissions Required:** `Orders and trades - Query closed orders & trades`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[Closed2]
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
) -> Optional[Closed2]:
    """Get Closed Orders

     Retrieve information about orders that have been closed (filled or cancelled). 50 results are
    returned at a time, the most recent by default.

    **Note:** If an order's tx ID is given for `start` or `end` time, the order's opening time
    (`opentm`) is used

    **API Key Permissions Required:** `Orders and trades - Query closed orders & trades`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Closed2
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
