"""
Module for Testing Authentication and Token Functionality.

This module contains test cases designed to verify the behavior of the
authentication system in the FastAPI application. It tests endpoints
related to token generation and validation, ensuring proper responses
and functionality.

Key Features:
- **Token Generation Test**: Verifies the `/token` endpoint generates
 a valid access token.
- **Token Validation Test**: Ensures the generated access token can be
 verified and checked against application logic.

Dependencies:
- `pytest`: For writing and running test cases.
- `fastapi.status`: For HTTP status code constants.
- `httpx.AsyncClient`: An asynchronous HTTP client for interacting with
 the application.
- `authentication.user_management.check_user_has_token`: Function to
 validate the generated tokens.

Examples:
The test cases simulate form data submissions for login and validate
both HTTP responses and token functionality.
"""

from typing import Dict

import pytest
from fastapi import status
from httpx import AsyncClient

from authentication.user_management import check_user_has_token


@pytest.mark.asyncio
async def test_login_for_access_token_async(async_client: AsyncClient) -> None:
    """
    Test the `/token` endpoint for generating an access token.

    This test sends login credentials to the `/token` endpoint and validates
    that a valid access token is returned in the response. It checks the
    response status, verifies the token type, and confirms the presence of the
    `access_token` field in the response.

    Args:
        async_client (AsyncClient): An asynchronous HTTP client for interacting
            with the FastAPI application.
    """
    form_data: Dict[str, str] = {
        "username": "fourth_user",
        "password": "<PASSWORD4>",
    }

    response = await async_client.post(url="/token", timeout=5, data=form_data)
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_user_has_token(async_client: AsyncClient) -> None:
    """
    Test token validation functionality using `check_user_has_token`.

    This test sends login credentials to the `/token` endpoint, retrieves the
    generated access token, and validates it using the `check_user_has_token`
    function. The test ensures that the validation process correctly identifies
    the token as valid.

    Args:
        async_client (AsyncClient): An asynchronous HTTP client for interacting
            with the FastAPI application.
    """
    form_data: Dict[str, str] = {
        "username": "fourth_user",
        "password": "<PASSWORD4>",
    }

    response = await async_client.post(url="/token", timeout=5, data=form_data)
    response_data = response.json()

    assert check_user_has_token(response_data["access_token"])
