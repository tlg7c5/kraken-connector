from http import HTTPStatus
from typing import Any

import httpx

from ... import exceptions
from ...constants.api import API_VERSION_PREFIX
from ...http import HTTPAuthenticatedClient
from ...schemas.get_deposit_methods_request import GetDepositMethodsRequest
from ...schemas.get_deposit_methods_response import GetDepositMethodsResponse
from ...security import sign_message
from ...types import Response, Unset


def _get_kwargs(
    form_data: GetDepositMethodsRequest,
) -> dict[str, Any]:
    return {
        "method": "post",
        "url": f"{API_VERSION_PREFIX}/private/DepositMethods",
        "data": form_data.to_dict(),
    }


def _parse_response(
    *, client: HTTPAuthenticatedClient, response: httpx.Response
) -> GetDepositMethodsResponse | None:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetDepositMethodsResponse.from_dict(response.json())

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
) -> Response[GetDepositMethodsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: HTTPAuthenticatedClient,
    form_data: GetDepositMethodsRequest,
) -> Response[GetDepositMethodsResponse]:
    """Get Deposit Methods

     Retrieve methods available for depositing a particular asset.

    **API Key Permissions Required:** `Funds permissions - Query` and `Funds permissions - Deposit`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetDepositMethodsResponse]
    """

    kwargs = _get_kwargs(
        form_data=form_data,
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
    form_data: GetDepositMethodsRequest,
) -> GetDepositMethodsResponse | None:
    """Get Deposit Methods

     Retrieve methods available for depositing a particular asset.

    **API Key Permissions Required:** `Funds permissions - Query` and `Funds permissions - Deposit`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetDepositMethodsResponse
    """

    return sync_detailed(
        client=client,
        form_data=form_data,
    ).parsed


async def asyncio_detailed(
    *,
    client: HTTPAuthenticatedClient,
    form_data: GetDepositMethodsRequest,
) -> Response[GetDepositMethodsResponse]:
    """Get Deposit Methods

     Retrieve methods available for depositing a particular asset.

    **API Key Permissions Required:** `Funds permissions - Query` and `Funds permissions - Deposit`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        Response[GetDepositMethodsResponse]
    """

    kwargs = _get_kwargs(
        form_data=form_data,
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
    form_data: GetDepositMethodsRequest,
) -> GetDepositMethodsResponse | None:
    """Get Deposit Methods

     Retrieve methods available for depositing a particular asset.

    **API Key Permissions Required:** `Funds permissions - Query` and `Funds permissions - Deposit`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and HTTPClient.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than HTTPClient.timeout.

    Returns:
        GetDepositMethodsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            form_data=form_data,
        )
    ).parsed
