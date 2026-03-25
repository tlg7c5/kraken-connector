from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import exceptions
from ...constants.api import API_VERSION_PREFIX
from ...constants.market_data import TradableAssetPairInfo
from ...http import HTTPAuthenticatedClient, HTTPClient
from ...schemas.get_tradable_asset_pairs_response import (
    GetTradableAssetPairsResponse,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    pair: Union[Unset, None, str] = UNSET,
    info: Union[Unset, None, TradableAssetPairInfo] = TradableAssetPairInfo.INFO,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    params["pair"] = pair

    json_info: Union[Unset, None, str] = UNSET
    if not isinstance(info, Unset):
        json_info = info.value if info else None

    params["info"] = json_info

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": f"{API_VERSION_PREFIX}/public/AssetPairs",
        "params": params,
    }


def _parse_response(
    *, client: Union[HTTPAuthenticatedClient, HTTPClient], response: httpx.Response
) -> Optional[GetTradableAssetPairsResponse]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetTradableAssetPairsResponse.from_dict(response.json())

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
) -> Response[GetTradableAssetPairsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[HTTPAuthenticatedClient, HTTPClient],
    pair: Union[Unset, None, str] = UNSET,
    info: Union[Unset, None, TradableAssetPairInfo] = TradableAssetPairInfo.INFO,
) -> Response[GetTradableAssetPairsResponse]:
    """Get Tradable Asset Pairs

     Get tradable asset pairs

    Args:
        pair (Union[Unset, None, str]):
        info (Union[Unset, None, TradableAssetPairInfo]):  Default:
            TradableAssetPairInfo.INFO.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetTradableAssetPairsResponse]
    """

    kwargs = _get_kwargs(
        pair=pair,
        info=info,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[HTTPAuthenticatedClient, HTTPClient],
    pair: Union[Unset, None, str] = UNSET,
    info: Union[Unset, None, TradableAssetPairInfo] = TradableAssetPairInfo.INFO,
) -> Optional[GetTradableAssetPairsResponse]:
    """Get Tradable Asset Pairs

     Get tradable asset pairs

    Args:
        pair (Union[Unset, None, str]):
        info (Union[Unset, None, TradableAssetPairInfo]):  Default:
            TradableAssetPairInfo.INFO.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetTradableAssetPairsResponse
    """

    return sync_detailed(
        client=client,
        pair=pair,
        info=info,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[HTTPAuthenticatedClient, HTTPClient],
    pair: Union[Unset, None, str] = UNSET,
    info: Union[Unset, None, TradableAssetPairInfo] = TradableAssetPairInfo.INFO,
) -> Response[GetTradableAssetPairsResponse]:
    """Get Tradable Asset Pairs

     Get tradable asset pairs

    Args:
        pair (Union[Unset, None, str]):
        info (Union[Unset, None, TradableAssetPairInfo]):  Default:
            TradableAssetPairInfo.INFO.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetTradableAssetPairsResponse]
    """

    kwargs = _get_kwargs(
        pair=pair,
        info=info,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[HTTPAuthenticatedClient, HTTPClient],
    pair: Union[Unset, None, str] = UNSET,
    info: Union[Unset, None, TradableAssetPairInfo] = TradableAssetPairInfo.INFO,
) -> Optional[GetTradableAssetPairsResponse]:
    """Get Tradable Asset Pairs

     Get tradable asset pairs

    Args:
        pair (Union[Unset, None, str]):
        info (Union[Unset, None, TradableAssetPairInfo]):  Default:
            TradableAssetPairInfo.INFO.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetTradableAssetPairsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            pair=pair,
            info=info,
        )
    ).parsed
