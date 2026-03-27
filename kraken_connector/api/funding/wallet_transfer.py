from http import HTTPStatus
from typing import Any

import httpx

from ... import exceptions
from ...constants.api import API_VERSION_PREFIX
from ...http import HTTPAuthenticatedClient
from ...schemas.wallet_transfer_request import WalletTransferRequest
from ...schemas.wallet_transfer_response import WalletTransferResponse
from ...security import sign_message
from ...types import Response, Unset


def _get_kwargs(
    form_data: WalletTransferRequest,
) -> dict[str, Any]:
    return {
        "method": "post",
        "url": f"{API_VERSION_PREFIX}/private/WalletTransfer",
        "data": form_data.to_dict(),
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> WalletTransferResponse | None:
    if response.status_code == HTTPStatus.OK:
        response_200 = WalletTransferResponse.from_dict(response.json())

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
) -> Response[WalletTransferResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient,
    form_data: WalletTransferRequest,
) -> Response[WalletTransferResponse]:
    r"""Request Wallet Transfer

     Transfer from a Kraken spot wallet to a Kraken Futures wallet. Note that a transfer in the other
    direction must be requested via the Kraken Futures API endpoint for [withdrawals to Spot
    wallets](https://docs.futures.kraken.com/\#http-api-trading-v3-api-transfers-initiate-withdrawal-to-
    spot-wallet).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[WalletTransferResponse]
    """

    kwargs = _get_kwargs(
        form_data=form_data,
    )

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
    form_data: WalletTransferRequest,
) -> WalletTransferResponse | None:
    r"""Request Wallet Transfer

     Transfer from a Kraken spot wallet to a Kraken Futures wallet. Note that a transfer in the other
    direction must be requested via the Kraken Futures API endpoint for [withdrawals to Spot
    wallets](https://docs.futures.kraken.com/\#http-api-trading-v3-api-transfers-initiate-withdrawal-to-
    spot-wallet).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        WalletTransferResponse
    """

    return sync_detailed(
        client=client,
        form_data=form_data,
    ).parsed


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient,
    form_data: WalletTransferRequest,
) -> Response[WalletTransferResponse]:
    r"""Request Wallet Transfer

     Transfer from a Kraken spot wallet to a Kraken Futures wallet. Note that a transfer in the other
    direction must be requested via the Kraken Futures API endpoint for [withdrawals to Spot
    wallets](https://docs.futures.kraken.com/\#http-api-trading-v3-api-transfers-initiate-withdrawal-to-
    spot-wallet).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[WalletTransferResponse]
    """

    kwargs = _get_kwargs(
        form_data=form_data,
    )

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
    form_data: WalletTransferRequest,
) -> WalletTransferResponse | None:
    r"""Request Wallet Transfer

     Transfer from a Kraken spot wallet to a Kraken Futures wallet. Note that a transfer in the other
    direction must be requested via the Kraken Futures API endpoint for [withdrawals to Spot
    wallets](https://docs.futures.kraken.com/\#http-api-trading-v3-api-transfers-initiate-withdrawal-to-
    spot-wallet).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        WalletTransferResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            form_data=form_data,
        )
    ).parsed
