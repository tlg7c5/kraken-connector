from http import HTTPStatus
from typing import Any

import httpx

from ... import exceptions
from ...constants.api import API_VERSION_PREFIX
from ...http import HTTPAuthenticatedClient
from ...schemas.get_extended_balance_response import GetExtendedBalanceResponse
from ...security import get_nonce, sign_message
from ...types import Response, Unset


def _get_kwargs() -> dict[str, Any]:
    return {
        "method": "post",
        "url": f"{API_VERSION_PREFIX}/private/BalanceEx",
        "data": {"nonce": get_nonce()},
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> GetExtendedBalanceResponse | None:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetExtendedBalanceResponse.from_dict(response.json())

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
) -> Response[GetExtendedBalanceResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient,
) -> Response[GetExtendedBalanceResponse]:
    """Get Extended Balance

     Retrieve all extended account balances, including credits and held amounts. Balance available for
    trading is calculated as: `available balance = balance + credit - credit_used - hold_trade`

    **API Key Permissions Required:** `Funds permissions - Query`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetExtendedBalanceResponse]
    """

    kwargs = _get_kwargs()

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
) -> GetExtendedBalanceResponse | None:
    """Get Extended Balance

     Retrieve all extended account balances, including credits and held amounts. Balance available for
    trading is calculated as: `available balance = balance + credit - credit_used - hold_trade`

    **API Key Permissions Required:** `Funds permissions - Query`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetExtendedBalanceResponse
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient,
) -> Response[GetExtendedBalanceResponse]:
    """Get Extended Balance

     Retrieve all extended account balances, including credits and held amounts. Balance available for
    trading is calculated as: `available balance = balance + credit - credit_used - hold_trade`

    **API Key Permissions Required:** `Funds permissions - Query`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetExtendedBalanceResponse]
    """

    kwargs = _get_kwargs()

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
) -> GetExtendedBalanceResponse | None:
    """Get Extended Balance

     Retrieve all extended account balances, including credits and held amounts. Balance available for
    trading is calculated as: `available balance = balance + credit - credit_used - hold_trade`

    **API Key Permissions Required:** `Funds permissions - Query`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetExtendedBalanceResponse
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
