from http import HTTPStatus
from typing import Any

import httpx

from ... import exceptions
from ...constants.api import API_VERSION_PREFIX
from ...http import HTTPAuthenticatedClient
from ...schemas.trade_volume_response import TradeVolumeResponse
from ...security import get_nonce, sign_message
from ...types import Response, Unset


def _get_kwargs() -> dict[str, Any]:
    return {
        "method": "post",
        "url": f"{API_VERSION_PREFIX}/private/TradeVolume",
        "data": {"nonce": get_nonce()},
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> TradeVolumeResponse | None:
    if response.status_code == HTTPStatus.OK:
        response_200 = TradeVolumeResponse.from_dict(response.json())

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
) -> Response[TradeVolumeResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient,
) -> Response[TradeVolumeResponse]:
    """Get Trade TradeVolumeResponse

     Returns 30 day USD trading volume and resulting fee schedule for any asset pair(s) provided.
    Note: If an asset pair is on a maker/taker fee schedule, the taker side is given in `fees` and maker
    side in `fees_maker`. For pairs not on maker/taker, they will only be given in `fees`.

    **API Key Permissions Required:** `Funds permissions - Query`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[TradeVolumeResponse]
    """

    kwargs = _get_kwargs()

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
) -> TradeVolumeResponse | None:
    """Get Trade TradeVolumeResponse

     Returns 30 day USD trading volume and resulting fee schedule for any asset pair(s) provided.
    Note: If an asset pair is on a maker/taker fee schedule, the taker side is given in `fees` and maker
    side in `fees_maker`. For pairs not on maker/taker, they will only be given in `fees`.

    **API Key Permissions Required:** `Funds permissions - Query`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        TradeVolumeResponse
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient,
) -> Response[TradeVolumeResponse]:
    """Get Trade TradeVolumeResponse

     Returns 30 day USD trading volume and resulting fee schedule for any asset pair(s) provided.
    Note: If an asset pair is on a maker/taker fee schedule, the taker side is given in `fees` and maker
    side in `fees_maker`. For pairs not on maker/taker, they will only be given in `fees`.

    **API Key Permissions Required:** `Funds permissions - Query`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[TradeVolumeResponse]
    """

    kwargs = _get_kwargs()

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
) -> TradeVolumeResponse | None:
    """Get Trade TradeVolumeResponse

     Returns 30 day USD trading volume and resulting fee schedule for any asset pair(s) provided.
    Note: If an asset pair is on a maker/taker fee schedule, the taker side is given in `fees` and maker
    side in `fees_maker`. For pairs not on maker/taker, they will only be given in `fees`.

    **API Key Permissions Required:** `Funds permissions - Query`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        TradeVolumeResponse
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
