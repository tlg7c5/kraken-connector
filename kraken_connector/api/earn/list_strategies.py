from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import exceptions
from ...constants.api import API_VERSION_PREFIX
from ...http import HTTPAuthenticatedClient
from ...schemas.list_strategies_request import ListStrategiesRequest
from ...schemas.list_strategies_response import ListStrategiesResponse
from ...security import sign_message
from ...types import Response, Unset


def _get_kwargs(
    *,
    json_body: ListStrategiesRequest,
) -> Dict[str, Any]:
    json_json_body = json_body.to_dict()

    return {
        "method": "post",
        "url": f"{API_VERSION_PREFIX}/private/Earn/Strategies",
        "json": json_json_body,
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Optional[ListStrategiesResponse]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ListStrategiesResponse.from_dict(response.json())

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
) -> Response[ListStrategiesResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient,
    json_body: ListStrategiesRequest,
) -> Response[ListStrategiesResponse]:
    """List Earn Strategies

     List earn strategies along with their parameters.

    Requires a valid API key but not specific permission is required.

    Returns only strategies that are available to the user
    based on geographic region.

    When the user does not meet the tier restriction, `can_allocate` will be
    false and `allocation_restriction_info` indicates `Tier` as the restriction
    reason. Earn products generally require Intermediate tier. Get your account verified
    to access earn.

    Paging isn't yet implemented, so it the endpoint always returns all
    data in the first page.

    Args:
        json_body (ListStrategiesRequest): List strategies parameters

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[ListStrategiesResponse]
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
    json_body: ListStrategiesRequest,
) -> Optional[ListStrategiesResponse]:
    """List Earn Strategies

     List earn strategies along with their parameters.

    Requires a valid API key but not specific permission is required.

    Returns only strategies that are available to the user
    based on geographic region.

    When the user does not meet the tier restriction, `can_allocate` will be
    false and `allocation_restriction_info` indicates `Tier` as the restriction
    reason. Earn products generally require Intermediate tier. Get your account verified
    to access earn.

    Paging isn't yet implemented, so it the endpoint always returns all
    data in the first page.

    Args:
        json_body (ListStrategiesRequest): List strategies parameters

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        ListStrategiesResponse
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient,
    json_body: ListStrategiesRequest,
) -> Response[ListStrategiesResponse]:
    """List Earn Strategies

     List earn strategies along with their parameters.

    Requires a valid API key but not specific permission is required.

    Returns only strategies that are available to the user
    based on geographic region.

    When the user does not meet the tier restriction, `can_allocate` will be
    false and `allocation_restriction_info` indicates `Tier` as the restriction
    reason. Earn products generally require Intermediate tier. Get your account verified
    to access earn.

    Paging isn't yet implemented, so it the endpoint always returns all
    data in the first page.

    Args:
        json_body (ListStrategiesRequest): List strategies parameters

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[ListStrategiesResponse]
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
    json_body: ListStrategiesRequest,
) -> Optional[ListStrategiesResponse]:
    """List Earn Strategies

     List earn strategies along with their parameters.

    Requires a valid API key but not specific permission is required.

    Returns only strategies that are available to the user
    based on geographic region.

    When the user does not meet the tier restriction, `can_allocate` will be
    false and `allocation_restriction_info` indicates `Tier` as the restriction
    reason. Earn products generally require Intermediate tier. Get your account verified
    to access earn.

    Paging isn't yet implemented, so it the endpoint always returns all
    data in the first page.

    Args:
        json_body (ListStrategiesRequest): List strategies parameters

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        ListStrategiesResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
