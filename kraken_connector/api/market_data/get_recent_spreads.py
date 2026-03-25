from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import exceptions
from ...constants.api import API_VERSION_PREFIX
from ...http import HTTPAuthenticatedClient, HTTPClient
from ...schemas.get_recent_spreads_response import GetRecentSpreadsResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    pair: str,
    since: Union[Unset, None, int] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    params["pair"] = pair

    params["since"] = since

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": f"{API_VERSION_PREFIX}/public/Spread",
        "params": params,
    }


def _parse_response(
    *, client: Union[HTTPAuthenticatedClient, HTTPClient], response: httpx.Response
) -> Optional[GetRecentSpreadsResponse]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetRecentSpreadsResponse.from_dict(response.json())

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
    *, client: Union[HTTPAuthenticatedClient, HTTPClient], response: httpx.Response
) -> Response[GetRecentSpreadsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[HTTPAuthenticatedClient, HTTPClient],
    pair: str,
    since: Union[Unset, None, int] = UNSET,
) -> Response[GetRecentSpreadsResponse]:
    """Get Recent Spreads

     Returns the last ~200 top-of-book spreads for a given pair

    Args:
        pair (str):
        since (Union[Unset, None, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetRecentSpreadsResponse]
    """

    kwargs = _get_kwargs(
        pair=pair,
        since=since,
    )

    response = client.get_or_create_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[HTTPAuthenticatedClient, HTTPClient],
    pair: str,
    since: Union[Unset, None, int] = UNSET,
) -> Optional[GetRecentSpreadsResponse]:
    """Get Recent Spreads

     Returns the last ~200 top-of-book spreads for a given pair

    Args:
        pair (str):
        since (Union[Unset, None, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetRecentSpreadsResponse
    """

    return sync_detailed(
        client=client,
        pair=pair,
        since=since,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[HTTPAuthenticatedClient, HTTPClient],
    pair: str,
    since: Union[Unset, None, int] = UNSET,
) -> Response[GetRecentSpreadsResponse]:
    """Get Recent Spreads

     Returns the last ~200 top-of-book spreads for a given pair

    Args:
        pair (str):
        since (Union[Unset, None, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetRecentSpreadsResponse]
    """

    kwargs = _get_kwargs(
        pair=pair,
        since=since,
    )

    response = await client.get_or_create_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[HTTPAuthenticatedClient, HTTPClient],
    pair: str,
    since: Union[Unset, None, int] = UNSET,
) -> Optional[GetRecentSpreadsResponse]:
    """Get Recent Spreads

     Returns the last ~200 top-of-book spreads for a given pair

    Args:
        pair (str):
        since (Union[Unset, None, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetRecentSpreadsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            pair=pair,
            since=since,
        )
    ).parsed
