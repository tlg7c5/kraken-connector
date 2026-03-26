from http import HTTPStatus
from typing import Any

import httpx

from ... import exceptions
from ...constants.api import API_VERSION_PREFIX
from ...http import HTTPAuthenticatedClient
from ...schemas.get_deallocate_strategy_status_request import (
    GetDeallocateStrategyStatusRequest,
)
from ...schemas.get_deallocate_strategy_status_response import (
    GetDeallocateStrategyStatusResponse,
)
from ...security import sign_message
from ...types import Response, Unset


def _get_kwargs(
    *,
    json_body: GetDeallocateStrategyStatusRequest,
) -> dict[str, Any]:
    json_json_body = json_body.to_dict()

    return {
        "method": "post",
        "url": f"{API_VERSION_PREFIX}/private/Earn/DeallocateStatus",
        "json": json_json_body,
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> GetDeallocateStrategyStatusResponse | None:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetDeallocateStrategyStatusResponse.from_dict(response.json())

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
) -> Response[GetDeallocateStrategyStatusResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient,
    json_body: GetDeallocateStrategyStatusRequest,
) -> Response[GetDeallocateStrategyStatusResponse]:
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
        json_body (GetDeallocateStrategyStatusRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetDeallocateStrategyStatusResponse]
    """

    kwargs = _get_kwargs(
        json_body=json_body,
    )

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
    json_body: GetDeallocateStrategyStatusRequest,
) -> GetDeallocateStrategyStatusResponse | None:
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
        json_body (GetDeallocateStrategyStatusRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetDeallocateStrategyStatusResponse
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient,
    json_body: GetDeallocateStrategyStatusRequest,
) -> Response[GetDeallocateStrategyStatusResponse]:
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
        json_body (GetDeallocateStrategyStatusRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetDeallocateStrategyStatusResponse]
    """

    kwargs = _get_kwargs(
        json_body=json_body,
    )

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
    json_body: GetDeallocateStrategyStatusRequest,
) -> GetDeallocateStrategyStatusResponse | None:
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
        json_body (GetDeallocateStrategyStatusRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetDeallocateStrategyStatusResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
