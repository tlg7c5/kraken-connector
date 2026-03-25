from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import exceptions
from ...constants.api import API_VERSION_PREFIX
from ...http import HTTPAuthenticatedClient
from ...schemas.allocate_strategy_request import AllocateStrategyRequest
from ...schemas.allocate_strategy_response import AllocateStrategyResponse
from ...security import sign_message
from ...types import Response, Unset


def _get_kwargs(
    *,
    json_body: AllocateStrategyRequest,
) -> Dict[str, Any]:
    json_json_body = json_body.to_dict()

    return {
        "method": "post",
        "url": f"{API_VERSION_PREFIX}/private/Earn/Allocate",
        "json": json_json_body,
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Optional[AllocateStrategyResponse]:
    if response.status_code == HTTPStatus.OK:
        response_200 = AllocateStrategyResponse.from_dict(response.json())

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
) -> Response[AllocateStrategyResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient,
    json_body: AllocateStrategyRequest,
) -> Response[AllocateStrategyResponse]:
    """Allocate Earn Funds

     Allocate funds to the Strategy.

    Requires the `Earn Funds` API key permission.
    The amount must always be defined.

    This method is asynchronous. A couple of preflight checks are
    performed synchronously on behalf of the method before it is dispatched
    further. The client is required to poll
    the result using the `/0/private/Earn/AllocateStatus` endpoint.

    There can be only one (de)allocation request in progress for given user and
    strategy at any time. While the operation is in progress:

    1. `pending` attribute in `/Earn/Allocations` response for the strategy
      indicates that funds are being allocated,
    2. `pending` attribute in `/Earn/AllocateStatus` response will be true.

    Following specific errors within `Earnings` class can be returned by this
    method:
    - Minimum allocation: `EEarnings:Below min:(De)allocation operation amount less than minimum`
    - Allocation in progress: `EEarnings:Busy:Another (de)allocation for the same strategy is in
    progress`
    - Service temporarily unavailable: `EEarnings:Busy`. Try again in a few minutes.
    - User tier verification: `EEarnings:Permission denied:The user's tier is not high enough`
    - Strategy not found: `EGeneral:Invalid arguments:Invalid strategy ID`

    Args:
        json_body (AllocateStrategyRequest): Allocation amount in asset specified in the strategy

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[AllocateStrategyResponse]
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
    json_body: AllocateStrategyRequest,
) -> Optional[AllocateStrategyResponse]:
    """Allocate Earn Funds

     Allocate funds to the Strategy.

    Requires the `Earn Funds` API key permission.
    The amount must always be defined.

    This method is asynchronous. A couple of preflight checks are
    performed synchronously on behalf of the method before it is dispatched
    further. The client is required to poll
    the result using the `/0/private/Earn/AllocateStatus` endpoint.

    There can be only one (de)allocation request in progress for given user and
    strategy at any time. While the operation is in progress:

    1. `pending` attribute in `/Earn/Allocations` response for the strategy
      indicates that funds are being allocated,
    2. `pending` attribute in `/Earn/AllocateStatus` response will be true.

    Following specific errors within `Earnings` class can be returned by this
    method:
    - Minimum allocation: `EEarnings:Below min:(De)allocation operation amount less than minimum`
    - Allocation in progress: `EEarnings:Busy:Another (de)allocation for the same strategy is in
    progress`
    - Service temporarily unavailable: `EEarnings:Busy`. Try again in a few minutes.
    - User tier verification: `EEarnings:Permission denied:The user's tier is not high enough`
    - Strategy not found: `EGeneral:Invalid arguments:Invalid strategy ID`

    Args:
        json_body (AllocateStrategyRequest): Allocation amount in asset specified in the strategy

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        AllocateStrategyResponse
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient,
    json_body: AllocateStrategyRequest,
) -> Response[AllocateStrategyResponse]:
    """Allocate Earn Funds

     Allocate funds to the Strategy.

    Requires the `Earn Funds` API key permission.
    The amount must always be defined.

    This method is asynchronous. A couple of preflight checks are
    performed synchronously on behalf of the method before it is dispatched
    further. The client is required to poll
    the result using the `/0/private/Earn/AllocateStatus` endpoint.

    There can be only one (de)allocation request in progress for given user and
    strategy at any time. While the operation is in progress:

    1. `pending` attribute in `/Earn/Allocations` response for the strategy
      indicates that funds are being allocated,
    2. `pending` attribute in `/Earn/AllocateStatus` response will be true.

    Following specific errors within `Earnings` class can be returned by this
    method:
    - Minimum allocation: `EEarnings:Below min:(De)allocation operation amount less than minimum`
    - Allocation in progress: `EEarnings:Busy:Another (de)allocation for the same strategy is in
    progress`
    - Service temporarily unavailable: `EEarnings:Busy`. Try again in a few minutes.
    - User tier verification: `EEarnings:Permission denied:The user's tier is not high enough`
    - Strategy not found: `EGeneral:Invalid arguments:Invalid strategy ID`

    Args:
        json_body (AllocateStrategyRequest): Allocation amount in asset specified in the strategy

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[AllocateStrategyResponse]
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
    json_body: AllocateStrategyRequest,
) -> Optional[AllocateStrategyResponse]:
    """Allocate Earn Funds

     Allocate funds to the Strategy.

    Requires the `Earn Funds` API key permission.
    The amount must always be defined.

    This method is asynchronous. A couple of preflight checks are
    performed synchronously on behalf of the method before it is dispatched
    further. The client is required to poll
    the result using the `/0/private/Earn/AllocateStatus` endpoint.

    There can be only one (de)allocation request in progress for given user and
    strategy at any time. While the operation is in progress:

    1. `pending` attribute in `/Earn/Allocations` response for the strategy
      indicates that funds are being allocated,
    2. `pending` attribute in `/Earn/AllocateStatus` response will be true.

    Following specific errors within `Earnings` class can be returned by this
    method:
    - Minimum allocation: `EEarnings:Below min:(De)allocation operation amount less than minimum`
    - Allocation in progress: `EEarnings:Busy:Another (de)allocation for the same strategy is in
    progress`
    - Service temporarily unavailable: `EEarnings:Busy`. Try again in a few minutes.
    - User tier verification: `EEarnings:Permission denied:The user's tier is not high enough`
    - Strategy not found: `EGeneral:Invalid arguments:Invalid strategy ID`

    Args:
        json_body (AllocateStrategyRequest): Allocation amount in asset specified in the strategy

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        AllocateStrategyResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
