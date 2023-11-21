from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import exceptions
from ...http import HTTPAuthenticatedClient
from ...schemas.cancel_all_orders_response_200 import CancelAllOrdersResponse200
from ...security import get_nonce, sign_message
from ...types import Response


def _get_kwargs() -> Dict[str, Any]:
    pass

    return {
        "method": "post",
        "url": "/0/private/CancelAll",
        "data": {"nonce": get_nonce()},
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Optional[CancelAllOrdersResponse200]:
    if response.status_code == HTTPStatus.OK:
        response_200 = CancelAllOrdersResponse200.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise exceptions.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Response[CancelAllOrdersResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient,
) -> Response[CancelAllOrdersResponse200]:
    """Cancel All Orders

     Cancel all open orders

    **API Key Permissions Required:** `Orders and trades - Create & modify orders` and `Orders and
    trades - Cancel & close orders`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[CancelAllOrdersResponse200]
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
) -> Optional[CancelAllOrdersResponse200]:
    """Cancel All Orders

     Cancel all open orders

    **API Key Permissions Required:** `Orders and trades - Create & modify orders` and `Orders and
    trades - Cancel & close orders`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        CancelAllOrdersResponse200
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient,
) -> Response[CancelAllOrdersResponse200]:
    """Cancel All Orders

     Cancel all open orders

    **API Key Permissions Required:** `Orders and trades - Create & modify orders` and `Orders and
    trades - Cancel & close orders`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[CancelAllOrdersResponse200]
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
) -> Optional[CancelAllOrdersResponse200]:
    """Cancel All Orders

     Cancel all open orders

    **API Key Permissions Required:** `Orders and trades - Create & modify orders` and `Orders and
    trades - Cancel & close orders`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        CancelAllOrdersResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
