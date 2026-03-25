from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import exceptions
from ...constants.api import API_VERSION_PREFIX
from ...http import HTTPAuthenticatedClient
from ...schemas.cancel_withdrawal_request import (
    CancelWithdrawalRequest,
)
from ...schemas.cancel_withdrawal_response import CancelWithdrawalResponse
from ...security import sign_message
from ...types import Response, Unset


def _get_kwargs(
    form_data: CancelWithdrawalRequest,
) -> Dict[str, Any]:
    return {
        "method": "post",
        "url": f"{API_VERSION_PREFIX}/private/WithdrawCancel",
        "data": form_data.to_dict(),
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> Optional[CancelWithdrawalResponse]:
    if response.status_code == HTTPStatus.OK:
        response_200 = CancelWithdrawalResponse.from_dict(response.json())

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
) -> Response[CancelWithdrawalResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient,
    form_data: CancelWithdrawalRequest,
) -> Response[CancelWithdrawalResponse]:
    """Request WithdrawFundsRequest Cancelation

     Cancel a recently requested withdrawal, if it has not already been successfully processed.

    **API Key Permissions Required:** `Funds permissions - Withdraw`, unless withdrawal is a
    `WalletTransfer`, then no permissions are required.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[CancelWithdrawalResponse]
    """

    kwargs = _get_kwargs(
        form_data=form_data,
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
    form_data: CancelWithdrawalRequest,
) -> Optional[CancelWithdrawalResponse]:
    """Request WithdrawFundsRequest Cancelation

     Cancel a recently requested withdrawal, if it has not already been successfully processed.

    **API Key Permissions Required:** `Funds permissions - Withdraw`, unless withdrawal is a
    `WalletTransfer`, then no permissions are required.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        CancelWithdrawalResponse
    """

    return sync_detailed(
        client=client,
        form_data=form_data,
    ).parsed


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient,
    form_data: CancelWithdrawalRequest,
) -> Response[CancelWithdrawalResponse]:
    """Request WithdrawFundsRequest Cancelation

     Cancel a recently requested withdrawal, if it has not already been successfully processed.

    **API Key Permissions Required:** `Funds permissions - Withdraw`, unless withdrawal is a
    `WalletTransfer`, then no permissions are required.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[CancelWithdrawalResponse]
    """

    kwargs = _get_kwargs(
        form_data=form_data,
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
    form_data: CancelWithdrawalRequest,
) -> Optional[CancelWithdrawalResponse]:
    """Request WithdrawFundsRequest Cancelation

     Cancel a recently requested withdrawal, if it has not already been successfully processed.

    **API Key Permissions Required:** `Funds permissions - Withdraw`, unless withdrawal is a
    `WalletTransfer`, then no permissions are required.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        CancelWithdrawalResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            form_data=form_data,
        )
    ).parsed
