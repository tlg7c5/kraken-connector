from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import exceptions
from ...constants.api import API_VERSION_PREFIX
from ...http import HTTPAuthenticatedClient
from ...schemas.deallocate_strategy_request import DeallocateStrategyRequest
from ...schemas.deallocate_strategy_response import DeallocateStrategyResponse
from ...security import sign_message
from ...types import Response, Unset


def _get_kwargs(
    *,
    json_body: DeallocateStrategyRequest,
) -> Dict[str, Any]:
    json_json_body = json_body.to_dict()

    return {
        "method": "post",
        "url": f"{API_VERSION_PREFIX}/private/Earn/Deallocate",
        "json": json_json_body,
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Optional[DeallocateStrategyResponse]:
    if response.status_code == HTTPStatus.OK:
        response_200 = DeallocateStrategyResponse.from_dict(response.json())

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
) -> Response[DeallocateStrategyResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient,
    json_body: DeallocateStrategyRequest,
) -> Response[DeallocateStrategyResponse]:
    """Deallocate Earn Funds

     Deallocate funds from a strategy.

    Requires the `Earn Funds` API key permission.
    The amount must always be defined.

    This method is asynchronous. A couple of preflight checks are
    performed synchronously on behalf of the method before it is dispatched
    further. If the method returns HTTP 202 code, the client is required to poll
    the result using the `/Earn/DeallocateStatus` endpoint.

    There can be only one (de)allocation request in progress for given user and
    strategy.  While the operation is in progress:

    1. `pending` attribute in `Allocations` response for the strategy will hold
       the amount that is being deallocated (negative amount)
    2. `pending` attribute in `DeallocateStatus` response will be true.

    Following specific errors within `Earnings` class can be returned by this
    method:
    - Minimum allocation: `EEarnings:Below min:(De)allocation operation amount less than minimum`
      allowed
    - Allocation in progress: `EEarnings:Busy:Another (de)allocation for the same strategy is in
    progress`
    - Strategy not found: `EGeneral:Invalid arguments:Invalid strategy ID`

    Args:
        json_body (DeallocateStrategyRequest): Allocation amount in asset specified in the
            strategy

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[DeallocateStrategyResponse]
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
    json_body: DeallocateStrategyRequest,
) -> Optional[DeallocateStrategyResponse]:
    """Deallocate Earn Funds

     Deallocate funds from a strategy.

    Requires the `Earn Funds` API key permission.
    The amount must always be defined.

    This method is asynchronous. A couple of preflight checks are
    performed synchronously on behalf of the method before it is dispatched
    further. If the method returns HTTP 202 code, the client is required to poll
    the result using the `/Earn/DeallocateStatus` endpoint.

    There can be only one (de)allocation request in progress for given user and
    strategy.  While the operation is in progress:

    1. `pending` attribute in `Allocations` response for the strategy will hold
       the amount that is being deallocated (negative amount)
    2. `pending` attribute in `DeallocateStatus` response will be true.

    Following specific errors within `Earnings` class can be returned by this
    method:
    - Minimum allocation: `EEarnings:Below min:(De)allocation operation amount less than minimum`
      allowed
    - Allocation in progress: `EEarnings:Busy:Another (de)allocation for the same strategy is in
    progress`
    - Strategy not found: `EGeneral:Invalid arguments:Invalid strategy ID`

    Args:
        json_body (DeallocateStrategyRequest): Allocation amount in asset specified in the
            strategy

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        DeallocateStrategyResponse
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient,
    json_body: DeallocateStrategyRequest,
) -> Response[DeallocateStrategyResponse]:
    """Deallocate Earn Funds

     Deallocate funds from a strategy.

    Requires the `Earn Funds` API key permission.
    The amount must always be defined.

    This method is asynchronous. A couple of preflight checks are
    performed synchronously on behalf of the method before it is dispatched
    further. If the method returns HTTP 202 code, the client is required to poll
    the result using the `/Earn/DeallocateStatus` endpoint.

    There can be only one (de)allocation request in progress for given user and
    strategy.  While the operation is in progress:

    1. `pending` attribute in `Allocations` response for the strategy will hold
       the amount that is being deallocated (negative amount)
    2. `pending` attribute in `DeallocateStatus` response will be true.

    Following specific errors within `Earnings` class can be returned by this
    method:
    - Minimum allocation: `EEarnings:Below min:(De)allocation operation amount less than minimum`
      allowed
    - Allocation in progress: `EEarnings:Busy:Another (de)allocation for the same strategy is in
    progress`
    - Strategy not found: `EGeneral:Invalid arguments:Invalid strategy ID`

    Args:
        json_body (DeallocateStrategyRequest): Allocation amount in asset specified in the
            strategy

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[DeallocateStrategyResponse]
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
    json_body: DeallocateStrategyRequest,
) -> Optional[DeallocateStrategyResponse]:
    """Deallocate Earn Funds

     Deallocate funds from a strategy.

    Requires the `Earn Funds` API key permission.
    The amount must always be defined.

    This method is asynchronous. A couple of preflight checks are
    performed synchronously on behalf of the method before it is dispatched
    further. If the method returns HTTP 202 code, the client is required to poll
    the result using the `/Earn/DeallocateStatus` endpoint.

    There can be only one (de)allocation request in progress for given user and
    strategy.  While the operation is in progress:

    1. `pending` attribute in `Allocations` response for the strategy will hold
       the amount that is being deallocated (negative amount)
    2. `pending` attribute in `DeallocateStatus` response will be true.

    Following specific errors within `Earnings` class can be returned by this
    method:
    - Minimum allocation: `EEarnings:Below min:(De)allocation operation amount less than minimum`
      allowed
    - Allocation in progress: `EEarnings:Busy:Another (de)allocation for the same strategy is in
    progress`
    - Strategy not found: `EGeneral:Invalid arguments:Invalid strategy ID`

    Args:
        json_body (DeallocateStrategyRequest): Allocation amount in asset specified in the
            strategy

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        DeallocateStrategyResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
