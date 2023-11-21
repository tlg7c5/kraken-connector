from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import exceptions
from ...http import HTTPAuthenticatedClient
from ...schemas.batch_cancel_open_orders_request_body import (
    BatchCancelOpenOrdersRequestBody,
)
from ...security import sign_message
from ...types import Response


def _get_kwargs(
    form_data: BatchCancelOpenOrdersRequestBody,
) -> Dict[str, Any]:
    pass

    return {
        "method": "post",
        "url": "/0/private/CancelOrderBatch",
        "data": form_data.to_dict(),
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Optional[Any]:
    if response.status_code == HTTPStatus.OK:
        return None
    if client.raise_on_unexpected_status:
        raise exceptions.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient,
    form_data: BatchCancelOpenOrdersRequestBody,
) -> Response[Any]:
    """Cancel Order Batch

     Cancel multiple open orders  by `txid` or `userref` (maximum 50 total unique IDs/references)

    **API Key Permissions Required:** `Orders and trades - Create & modify orders` and `Orders and
    trades - Cancel & close orders`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        form_data=form_data,
    )

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


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient,
    form_data: BatchCancelOpenOrdersRequestBody,
) -> Response[Any]:
    """Cancel Order Batch

     Cancel multiple open orders  by `txid` or `userref` (maximum 50 total unique IDs/references)

    **API Key Permissions Required:** `Orders and trades - Create & modify orders` and `Orders and
    trades - Cancel & close orders`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        form_data=form_data,
    )

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
