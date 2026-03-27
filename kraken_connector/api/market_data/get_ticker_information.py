from http import HTTPStatus
from typing import Any

import httpx

from ... import exceptions
from ...constants.api import API_VERSION_PREFIX
from ...http import HTTPAuthenticatedClient, HTTPClient
from ...schemas.get_ticker_response import GetTickerResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    pair: Unset | None | str = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    params["pair"] = pair

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": f"{API_VERSION_PREFIX}/public/Ticker",
        "params": params,
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient | HTTPClient, response: httpx.Response
) -> GetTickerResponse | None:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetTickerResponse.from_dict(response.json())

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
    *, client: HTTPAuthenticatedClient | HTTPClient, response: httpx.Response
) -> Response[GetTickerResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient | HTTPClient,
    pair: Unset | None | str = UNSET,
) -> Response[GetTickerResponse]:
    """Get Ticker Information

     Note: Today's prices start at midnight UTC. Leaving the pair parameter blank will return tickers for
    all tradable assets on Kraken.

    Args:
        pair (Union[Unset, None, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetTickerResponse]
    """

    kwargs = _get_kwargs(
        pair=pair,
    )

    response = client.get_or_create_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: HTTPAuthenticatedClient | HTTPClient,
    pair: Unset | None | str = UNSET,
) -> GetTickerResponse | None:
    """Get Ticker Information

     Note: Today's prices start at midnight UTC. Leaving the pair parameter blank will return tickers for
    all tradable assets on Kraken.

    Args:
        pair (Union[Unset, None, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetTickerResponse
    """

    return sync_detailed(
        client=client,
        pair=pair,
    ).parsed


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient | HTTPClient,
    pair: Unset | None | str = UNSET,
) -> Response[GetTickerResponse]:
    """Get Ticker Information

     Note: Today's prices start at midnight UTC. Leaving the pair parameter blank will return tickers for
    all tradable assets on Kraken.

    Args:
        pair (Union[Unset, None, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetTickerResponse]
    """

    kwargs = _get_kwargs(
        pair=pair,
    )

    response = await client.get_or_create_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: HTTPAuthenticatedClient | HTTPClient,
    pair: Unset | None | str = UNSET,
) -> GetTickerResponse | None:
    """Get Ticker Information

     Note: Today's prices start at midnight UTC. Leaving the pair parameter blank will return tickers for
    all tradable assets on Kraken.

    Args:
        pair (Union[Unset, None, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetTickerResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            pair=pair,
        )
    ).parsed
