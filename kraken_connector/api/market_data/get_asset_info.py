from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import exceptions
from ...constants.api import API_VERSION_PREFIX
from ...http import HTTPAuthenticatedClient, HTTPClient
from ...schemas.get_asset_info_response import GetAssetInfoResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    asset: Union[Unset, None, str] = UNSET,
    aclass: Union[Unset, None, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    params["asset"] = asset

    params["aclass"] = aclass

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": f"{API_VERSION_PREFIX}/public/Assets",
        "params": params,
    }


def _parse_response(
    *, client: Union[HTTPAuthenticatedClient, HTTPClient], response: httpx.Response
) -> Optional[GetAssetInfoResponse]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetAssetInfoResponse.from_dict(response.json())

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
) -> Response[GetAssetInfoResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[HTTPAuthenticatedClient, HTTPClient],
    asset: Union[Unset, None, str] = UNSET,
    aclass: Union[Unset, None, str] = UNSET,
) -> Response[GetAssetInfoResponse]:
    """Get Asset Info

     Get information about the assets that are available for deposit, withdrawal, trading and staking.

    Args:
        asset (Union[Unset, None, str]):
        aclass (Union[Unset, None, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetAssetInfoResponse]
    """

    kwargs = _get_kwargs(
        asset=asset,
        aclass=aclass,
    )

    response = client.get_or_create_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[HTTPAuthenticatedClient, HTTPClient],
    asset: Union[Unset, None, str] = UNSET,
    aclass: Union[Unset, None, str] = UNSET,
) -> Optional[GetAssetInfoResponse]:
    """Get Asset Info

     Get information about the assets that are available for deposit, withdrawal, trading and staking.

    Args:
        asset (Union[Unset, None, str]):
        aclass (Union[Unset, None, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetAssetInfoResponse
    """

    return sync_detailed(
        client=client,
        asset=asset,
        aclass=aclass,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[HTTPAuthenticatedClient, HTTPClient],
    asset: Union[Unset, None, str] = UNSET,
    aclass: Union[Unset, None, str] = UNSET,
) -> Response[GetAssetInfoResponse]:
    """Get Asset Info

     Get information about the assets that are available for deposit, withdrawal, trading and staking.

    Args:
        asset (Union[Unset, None, str]):
        aclass (Union[Unset, None, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetAssetInfoResponse]
    """

    kwargs = _get_kwargs(
        asset=asset,
        aclass=aclass,
    )

    response = await client.get_or_create_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[HTTPAuthenticatedClient, HTTPClient],
    asset: Union[Unset, None, str] = UNSET,
    aclass: Union[Unset, None, str] = UNSET,
) -> Optional[GetAssetInfoResponse]:
    """Get Asset Info

     Get information about the assets that are available for deposit, withdrawal, trading and staking.

    Args:
        asset (Union[Unset, None, str]):
        aclass (Union[Unset, None, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetAssetInfoResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            asset=asset,
            aclass=aclass,
        )
    ).parsed
