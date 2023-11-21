from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import exceptions
from ...http import HTTPAuthenticatedClient
from ...schemas.add_2 import Add2
from ...schemas.add_standard_order_request_body import AddStandardOrderRequestBody
from ...security import sign_message
from ...types import Response


def _get_kwargs(
    form_data: AddStandardOrderRequestBody,
) -> Dict[str, Any]:
    pass

    return {
        "method": "post",
        "url": "/0/private/AddOrder",
        "data": form_data.to_dict(),
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Optional[Add2]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Add2.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise exceptions.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Response[Add2]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient,
    form_data: AddStandardOrderRequestBody,
) -> Response[Add2]:
    """Add Order

     Place a new order.

    **Note**: See the [AssetPairs](#operation/getTradableAssetPairs) endpoint for details on the
    available trading pairs, their price and quantity precisions, order minimums, available leverage,
    etc.

    **API Key Permissions Required:** `Orders and trades - Create & modify orders`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[Add2]
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


def sync(
    *,
    client: HTTPAuthenticatedClient,
    form_data: AddStandardOrderRequestBody,
) -> Optional[Add2]:
    """Add Order

     Place a new order.

    **Note**: See the [AssetPairs](#operation/getTradableAssetPairs) endpoint for details on the
    available trading pairs, their price and quantity precisions, order minimums, available leverage,
    etc.

    **API Key Permissions Required:** `Orders and trades - Create & modify orders`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Add2
    """

    return sync_detailed(
        client=client,
        form_data=form_data,
    ).parsed


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient,
    form_data: AddStandardOrderRequestBody,
) -> Response[Add2]:
    """Add Order

     Place a new order.

    **Note**: See the [AssetPairs](#operation/getTradableAssetPairs) endpoint for details on the
    available trading pairs, their price and quantity precisions, order minimums, available leverage,
    etc.

    **API Key Permissions Required:** `Orders and trades - Create & modify orders`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[Add2]
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


async def asyncio(
    *,
    client: HTTPAuthenticatedClient,
    form_data: AddStandardOrderRequestBody,
) -> Optional[Add2]:
    """Add Order

     Place a new order.

    **Note**: See the [AssetPairs](#operation/getTradableAssetPairs) endpoint for details on the
    available trading pairs, their price and quantity precisions, order minimums, available leverage,
    etc.

    **API Key Permissions Required:** `Orders and trades - Create & modify orders`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Add2
    """

    return (
        await asyncio_detailed(
            client=client,
            form_data=form_data,
        )
    ).parsed
