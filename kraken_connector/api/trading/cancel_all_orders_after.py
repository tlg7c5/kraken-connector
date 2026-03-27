from http import HTTPStatus
from typing import Any

import httpx

from ... import exceptions
from ...constants.api import API_VERSION_PREFIX
from ...http import HTTPAuthenticatedClient
from ...schemas.cancel_all_orders_after_request import CancelAllOrdersAfterRequest
from ...schemas.cancel_all_orders_after_response import (
    CancelAllOrdersAfterResponse,
)
from ...security import sign_message
from ...types import Response, Unset


def _get_kwargs(
    form_data: CancelAllOrdersAfterRequest,
) -> dict[str, Any]:
    return {
        "method": "post",
        "url": f"{API_VERSION_PREFIX}/private/CancelAllOrdersAfter",
        "data": form_data.to_dict(),
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> CancelAllOrdersAfterResponse | None:
    if response.status_code == HTTPStatus.OK:
        response_200 = CancelAllOrdersAfterResponse.from_dict(response.json())

        # Check for API-level errors in response body
        errors = getattr(response_200, "error", None)
        if errors and not isinstance(errors, Unset) and errors:
            raise exceptions.KrakenAPIError(
                errors if isinstance(errors, list) else [str(errors)]
            )

        return response_200
    if client.raise_on_unexpected_status:
        raise exceptions.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Response[CancelAllOrdersAfterResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient,
    form_data: CancelAllOrdersAfterRequest,
) -> Response[CancelAllOrdersAfterResponse]:
    """Cancel All Orders After X

     CancelAllOrdersAfter provides a \"Dead Man's Switch\" mechanism to protect the client from network
    malfunction, extreme latency or unexpected matching engine downtime. The client can send a request
    with a timeout (in seconds), that will start a countdown timer which will cancel *all* client orders
    when the timer expires. The client has to keep sending new requests to push back the trigger time,
    or deactivate the mechanism by specifying a timeout of 0. If the timer expires, all orders are
    cancelled and then the timer remains disabled until the client provides a new (non-zero) timeout.

    The recommended use is to make a call every 15 to 30 seconds, providing a timeout of 60 seconds.
    This allows the client to keep the orders in place in case of a brief disconnection or transient
    delay, while keeping them safe in case of a network breakdown. It is also recommended to disable the
    timer ahead of regularly scheduled trading engine maintenance (if the timer is enabled, all orders
    will be cancelled when the trading engine comes back from downtime - planned or otherwise).

    **API Key Permissions Required:** `Orders and trades - Create & modify orders` and `Orders and
    trades - Cancel & close orders`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[CancelAllOrdersAfterResponse]
    """

    kwargs = _get_kwargs(
        form_data=form_data,
    )

    if client._api_secret is None:
        raise ValueError("api_secret is required for authenticated endpoints")
    security_header = {
        client.hmac_msg_signature: sign_message(
            client._api_secret, kwargs["data"], kwargs["url"]
        )
    }
    secured_client = client.with_headers(security_header)

    response = secured_client.get_or_create_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    *,
    client: HTTPAuthenticatedClient,
    form_data: CancelAllOrdersAfterRequest,
) -> CancelAllOrdersAfterResponse | None:
    """Cancel All Orders After X

     CancelAllOrdersAfter provides a \"Dead Man's Switch\" mechanism to protect the client from network
    malfunction, extreme latency or unexpected matching engine downtime. The client can send a request
    with a timeout (in seconds), that will start a countdown timer which will cancel *all* client orders
    when the timer expires. The client has to keep sending new requests to push back the trigger time,
    or deactivate the mechanism by specifying a timeout of 0. If the timer expires, all orders are
    cancelled and then the timer remains disabled until the client provides a new (non-zero) timeout.

    The recommended use is to make a call every 15 to 30 seconds, providing a timeout of 60 seconds.
    This allows the client to keep the orders in place in case of a brief disconnection or transient
    delay, while keeping them safe in case of a network breakdown. It is also recommended to disable the
    timer ahead of regularly scheduled trading engine maintenance (if the timer is enabled, all orders
    will be cancelled when the trading engine comes back from downtime - planned or otherwise).

    **API Key Permissions Required:** `Orders and trades - Create & modify orders` and `Orders and
    trades - Cancel & close orders`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        CancelAllOrdersAfterResponse
    """

    return sync_detailed(
        client=client,
        form_data=form_data,
    ).parsed


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient,
    form_data: CancelAllOrdersAfterRequest,
) -> Response[CancelAllOrdersAfterResponse]:
    """Cancel All Orders After X

     CancelAllOrdersAfter provides a \"Dead Man's Switch\" mechanism to protect the client from network
    malfunction, extreme latency or unexpected matching engine downtime. The client can send a request
    with a timeout (in seconds), that will start a countdown timer which will cancel *all* client orders
    when the timer expires. The client has to keep sending new requests to push back the trigger time,
    or deactivate the mechanism by specifying a timeout of 0. If the timer expires, all orders are
    cancelled and then the timer remains disabled until the client provides a new (non-zero) timeout.

    The recommended use is to make a call every 15 to 30 seconds, providing a timeout of 60 seconds.
    This allows the client to keep the orders in place in case of a brief disconnection or transient
    delay, while keeping them safe in case of a network breakdown. It is also recommended to disable the
    timer ahead of regularly scheduled trading engine maintenance (if the timer is enabled, all orders
    will be cancelled when the trading engine comes back from downtime - planned or otherwise).

    **API Key Permissions Required:** `Orders and trades - Create & modify orders` and `Orders and
    trades - Cancel & close orders`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[CancelAllOrdersAfterResponse]
    """

    kwargs = _get_kwargs(
        form_data=form_data,
    )

    if client._api_secret is None:
        raise ValueError("api_secret is required for authenticated endpoints")
    security_header = {
        client.hmac_msg_signature: sign_message(
            client._api_secret, kwargs["data"], kwargs["url"]
        )
    }
    secured_client = client.with_headers(security_header)

    response = await secured_client.get_or_create_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: HTTPAuthenticatedClient,
    form_data: CancelAllOrdersAfterRequest,
) -> CancelAllOrdersAfterResponse | None:
    """Cancel All Orders After X

     CancelAllOrdersAfter provides a \"Dead Man's Switch\" mechanism to protect the client from network
    malfunction, extreme latency or unexpected matching engine downtime. The client can send a request
    with a timeout (in seconds), that will start a countdown timer which will cancel *all* client orders
    when the timer expires. The client has to keep sending new requests to push back the trigger time,
    or deactivate the mechanism by specifying a timeout of 0. If the timer expires, all orders are
    cancelled and then the timer remains disabled until the client provides a new (non-zero) timeout.

    The recommended use is to make a call every 15 to 30 seconds, providing a timeout of 60 seconds.
    This allows the client to keep the orders in place in case of a brief disconnection or transient
    delay, while keeping them safe in case of a network breakdown. It is also recommended to disable the
    timer ahead of regularly scheduled trading engine maintenance (if the timer is enabled, all orders
    will be cancelled when the trading engine comes back from downtime - planned or otherwise).

    **API Key Permissions Required:** `Orders and trades - Create & modify orders` and `Orders and
    trades - Cancel & close orders`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        CancelAllOrdersAfterResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            form_data=form_data,
        )
    ).parsed
