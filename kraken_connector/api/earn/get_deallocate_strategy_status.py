from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import exceptions
from ...http import HTTPAuthenticatedClient
from ...schemas.get_deallocate_strategy_status_json_body import (
    GetDeallocateStrategyStatusJsonBody,
)
from ...schemas.get_deallocate_strategy_status_response_200 import (
    GetDeallocateStrategyStatusResponse200,
)
from ...security import sign_message
from ...types import Response


def _get_kwargs(
    *,
    json_body: GetDeallocateStrategyStatusJsonBody,
) -> Dict[str, Any]:
    pass

    json_json_body = json_body.to_dict()

    return {
        "method": "post",
        "url": "/0/private/Earn/DeallocateStatus",
        "json": json_json_body,
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Optional[GetDeallocateStrategyStatusResponse200]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetDeallocateStrategyStatusResponse200.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise exceptions.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Response[GetDeallocateStrategyStatusResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient,
    json_body: GetDeallocateStrategyStatusJsonBody,
) -> Response[GetDeallocateStrategyStatusResponse200]:
    """Get Deallocation Status

     Get the status of the last deallocation request.

    Requires either the `Earn Funds` or `Query Funds` API key permission.

    (De)allocation operations are asynchronous and this endpoint allows client
    to retrieve the status of the last dispatched operation. There can be only
    one (de)allocation request in progress for given user and strategy.

    The `pending` attribute in the response indicates if the previously
    dispatched operation is still in progress (true) or has successfully
    completed (false).  If the dispatched request failed with an error, then
    HTTP error is returned to the client as if it belonged to the original
    request.

    Following specific errors within `Earnings` class can be returned by this
    method:
    - Insufficient funds: `EEarnings:Insufficient funds:Insufficient funds to complete the
    (de)allocation request`
    - Minimum allocation: `EEarnings:Below min:(De)allocation operation amount less than minimum`

    Args:
        json_body (GetDeallocateStrategyStatusJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetDeallocateStrategyStatusResponse200]
    """

    kwargs = _get_kwargs(
        json_body=json_body,
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
    json_body: GetDeallocateStrategyStatusJsonBody,
) -> Optional[GetDeallocateStrategyStatusResponse200]:
    """Get Deallocation Status

     Get the status of the last deallocation request.

    Requires either the `Earn Funds` or `Query Funds` API key permission.

    (De)allocation operations are asynchronous and this endpoint allows client
    to retrieve the status of the last dispatched operation. There can be only
    one (de)allocation request in progress for given user and strategy.

    The `pending` attribute in the response indicates if the previously
    dispatched operation is still in progress (true) or has successfully
    completed (false).  If the dispatched request failed with an error, then
    HTTP error is returned to the client as if it belonged to the original
    request.

    Following specific errors within `Earnings` class can be returned by this
    method:
    - Insufficient funds: `EEarnings:Insufficient funds:Insufficient funds to complete the
    (de)allocation request`
    - Minimum allocation: `EEarnings:Below min:(De)allocation operation amount less than minimum`

    Args:
        json_body (GetDeallocateStrategyStatusJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetDeallocateStrategyStatusResponse200
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient,
    json_body: GetDeallocateStrategyStatusJsonBody,
) -> Response[GetDeallocateStrategyStatusResponse200]:
    """Get Deallocation Status

     Get the status of the last deallocation request.

    Requires either the `Earn Funds` or `Query Funds` API key permission.

    (De)allocation operations are asynchronous and this endpoint allows client
    to retrieve the status of the last dispatched operation. There can be only
    one (de)allocation request in progress for given user and strategy.

    The `pending` attribute in the response indicates if the previously
    dispatched operation is still in progress (true) or has successfully
    completed (false).  If the dispatched request failed with an error, then
    HTTP error is returned to the client as if it belonged to the original
    request.

    Following specific errors within `Earnings` class can be returned by this
    method:
    - Insufficient funds: `EEarnings:Insufficient funds:Insufficient funds to complete the
    (de)allocation request`
    - Minimum allocation: `EEarnings:Below min:(De)allocation operation amount less than minimum`

    Args:
        json_body (GetDeallocateStrategyStatusJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetDeallocateStrategyStatusResponse200]
    """

    kwargs = _get_kwargs(
        json_body=json_body,
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
    json_body: GetDeallocateStrategyStatusJsonBody,
) -> Optional[GetDeallocateStrategyStatusResponse200]:
    """Get Deallocation Status

     Get the status of the last deallocation request.

    Requires either the `Earn Funds` or `Query Funds` API key permission.

    (De)allocation operations are asynchronous and this endpoint allows client
    to retrieve the status of the last dispatched operation. There can be only
    one (de)allocation request in progress for given user and strategy.

    The `pending` attribute in the response indicates if the previously
    dispatched operation is still in progress (true) or has successfully
    completed (false).  If the dispatched request failed with an error, then
    HTTP error is returned to the client as if it belonged to the original
    request.

    Following specific errors within `Earnings` class can be returned by this
    method:
    - Insufficient funds: `EEarnings:Insufficient funds:Insufficient funds to complete the
    (de)allocation request`
    - Minimum allocation: `EEarnings:Below min:(De)allocation operation amount less than minimum`

    Args:
        json_body (GetDeallocateStrategyStatusJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetDeallocateStrategyStatusResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
