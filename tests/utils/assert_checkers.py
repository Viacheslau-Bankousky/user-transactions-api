"""
Module for Response Validation and Assertion in API Testing.

This module provides a set of utility functions used for validating
and asserting API responses related to user data, transactions,
and statistical data. The module primarily focuses on ensuring
that the API responses match the expected structure, formatting,
and contents.

Key Features:
- **Balance Validation**: Ensures that expected currencies and amounts
  are correctly represented in the response.
- **Date Format Validation**: Verifies that dates in the responses
  follow a specific format.
- **User Data Validation**: Validates the correctness of user-related
  fields in response data.
- **Transaction Data Validation**: Confirms the accuracy of transaction
  details, including amounts, currencies, and statuses.
- **Statistical Data Validation**: Asserts the correctness of response
  data for statistical outputs.

Dependencies:
- The `datetime` module for date parsing and format validation.
- The `decimal` module for precise handling of financial amounts.
- A custom enum `UserStatusEnum` for validating user status values.

Constants:
- **BALANCES**: A list of dictionaries representing expected balances in
  different currencies, initially set to `0.00`.

Functions:
- **assert_get_user_response**: Validates the user data in the response,
  ensuring all attributes match the expected values.
- **check_balance**: Checks if the balance data, either as a list or
  a single object, matches the predefined balances structure.
- **assert_currency_response**: Validates currency and amount data
  within user balance responses.
- **validate_datetime_format**: Asserts that a given date string matches
  the specified date format.
- **assert_user_change_response**: Verifies that user update responses
  contain the expected values after changes.
- **assert_transaction_response**: Validates transaction details,
  such as amount, currency, status, and purpose.
- **assert_statistics_response**: Ensures all statistical details in
  a JSON response meet the expected values and format.

Examples:
These functions are often used in test suites where API responses
are compared to predefined expectations to verify the correctness
of backend implementation.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Set, cast

from models.enums import UserStatusEnum

BALANCES: List[Dict[str, str]] = [
    {"currency": "USD", "amount": "0.00"},
    {"currency": "EUR", "amount": "0.00"},
    {"currency": "AUD", "amount": "0.00"},
    {"currency": "CAD", "amount": "0.00"},
    {"currency": "ARS", "amount": "0.00"},
    {"currency": "PLN", "amount": "0.00"},
    {"currency": "BTC", "amount": "0.00"},
    {"currency": "ETH", "amount": "0.00"},
    {"currency": "DOGE", "amount": "0.00"},
    {"currency": "USDT", "amount": "0.00"},
]


def assert_get_user_response(
    response_data: Dict,
    expected_user_id: int,
    expected_user_name: str,
    expected_email: str,
    expected_user_status: UserStatusEnum,
) -> None:
    """
    Validate the user data in the response.

    Ensures the response contains the correct user ID, name, email,
    status, and balance. Also validates the format of the creation date.

    Args:
        response_data (Dict): The API response containing user data.
        expected_user_id (int): The expected user ID.
        expected_user_name (str): The expected user name.
        expected_email (str): The expected email address.
        expected_user_status (UserStatusEnum): The expected user status.

    Raises:
        AssertionError: If any of the response fields do not match
                        the expected values.
    """
    assert response_data["id"] == expected_user_id
    assert response_data["name"] == expected_user_name
    assert response_data["email"] == expected_email
    validate_datetime_format(response_data["created"])
    assert response_data["status"] == expected_user_status
    check_balance(response_data=response_data)


def check_balance(response_data: List[Dict] | Dict) -> None:
    """
    Validate the balances in the response.

    Ensures that the response contains the predefined currencies
    and that all amounts are correctly initialized to `0.00`.

    Args:
        response_data (List[Dict] | Dict): The API response containing
                                               balance data.

    Raises:
        AssertionError: If the balance data is missing, has incorrect
                        currencies or unexpected amounts.
    """
    expected_currencies = {balance.get("currency") for balance in BALANCES}
    expected_money_sum = {balance.get("amount") for balance in BALANCES}
    if isinstance(response_data, list):
        for balance_item in response_data:
            assert_currency_response(
                response_data=balance_item,
                expected_currencies=expected_currencies,
                expected_money_sum=expected_money_sum,
            )
    else:
        assert_currency_response(
            response_data=response_data,
            expected_currencies=expected_currencies,
            expected_money_sum=expected_money_sum,
        )


def assert_currency_response(
    response_data: Dict[str, str | List],
    expected_currencies: Set,
    expected_money_sum: Set,
) -> None:
    """
    Validate the currency data in the response.

    Ensures all currencies and amounts within the user balances match
    the expected sets.

    Args:
        response_data (Dict[str, str | List]): The API response containing
                                                  currency and balance data.
        expected_currencies (Set): The set of expected currency codes.
        expected_money_sum (Set): The set of expected amounts.

    Raises:
        AssertionError: If the currencies or amounts in the response
                        do not match the expected values.
    """
    assert "balances" in response_data.keys()
    user_balances = cast(List[Dict[str, str]], response_data.get("balances"))
    estimated_currencies = {
        balance.get("currency") for balance in user_balances
    }
    estimated_money_sums = {balance.get("amount") for balance in user_balances}
    assert estimated_currencies == expected_currencies
    assert estimated_money_sums == expected_money_sum


def validate_datetime_format(
    date_str: str, date_format: str = "%Y-%m-%dT%H:%M:%S.%f"
) -> None:
    """
    Validate the format of a date string.

    Ensures that the provided `date_str` matches the specified string format.
    The default format includes a full timestamp with fraction seconds.

    Args:
        date_str (str): The date string to validate.
        date_format (str): The expected date format (default is
                               `%Y-%m-%dT%H:%M:%S.%f`).

    Raises:
        AssertionError: If the date string does not match the expected format.
    """
    try:
        datetime.strptime(date_str, date_format)
    except ValueError:
        raise AssertionError(f"Date {date_str} doesnt match {date_format}")


def assert_user_change_response(
    response_data: Dict,
    expected_user_id: int,
    expected_user_name: str,
    expected_email: str,
    expected_user_status: str,
) -> None:
    """
    Validate the response after a user update.

    Ensures the response contains the correct attributes for a user
    after it has been updated, including ID, name, email, and status.

    Args:
        response_data (Dict): The API response containing updated user data.
        expected_user_id (int): The expected user ID.
        expected_user_name (str): The expected user name.
        expected_email (str): The expected email address.
        expected_user_status (str): The expected user status.

    Raises:
        AssertionError: If any of the response fields do not match
                        the expected values.
    """
    assert response_data["id"] == expected_user_id
    assert response_data["name"] == expected_user_name
    assert response_data["email"] == expected_email
    validate_datetime_format(response_data["created"])
    assert response_data["status"] == expected_user_status


def assert_transaction_response(
    response_data: Dict,
    expected_amount: Decimal,
    expected_currency: str,
    expected_user_id: int,
    expected_status: str,
    expected_purpose: str,
) -> None:
    """
    Validate the transaction data in the response.

    Ensures that the transaction response contains accurate details
    for user ID, amount, currency, transaction status, purpose,
    and creation date.

    Args:
        response_data (Dict): The API response containing transaction data.
        expected_amount (Decimal): The expected transaction amount.
        expected_currency (str): The expected currency code.
        expected_user_id (int): The expected user ID for the transaction.
        expected_status (str): The expected transaction status.
        expected_purpose (str): The expected purpose of the transaction.

    Raises:
        AssertionError: If any of the transaction fields do not match
                        the expected values.
    """
    assert response_data["user_id"] == expected_user_id
    assert response_data["amount"] == expected_amount
    assert response_data["currency"] == expected_currency
    assert response_data["status"] == expected_status
    validate_datetime_format(response_data["created"])
    assert response_data["purpose"] == expected_purpose


def assert_statistics_response(
    response_data: Dict,
    **kwargs,
) -> None:
    """
    Validate the statistical data in the response.

    Ensures the response meets the expected values for user registration,
    deposits, withdrawals, transactions, and rollbacks. Also verifies
    the format of the start and end dates.

    Args:
        response_data (Dict): The API response containing statistical data.
        **kwargs: Expected values for various statistics
                    (e.g., registered user count, deposit amounts).

    Raises:
        AssertionError: If the statistical data does not match the
                        expected values or dates are incorrectly formatted.
    """
    validate_datetime_format(
        date_str=response_data["start_date"], date_format="%Y-%m-%d"
    )
    validate_datetime_format(
        date_str=response_data["end_date"], date_format="%Y-%m-%d"
    )
    assert (
        response_data["registered_users_count"]
        == kwargs["registered_users_count"]
    )
    assert (
        response_data["registered_and_deposit_users_count"]
        == kwargs["registered_and_deposit_users_count"]
    )
    assert (
        response_data["registered_and_not_rollbacked_deposit_users_count"]
        == kwargs["registered_and_not_rollbacked_deposit_users_count"]
    )
    assert (
        response_data["not_rollbacked_deposit_amount"]
        == kwargs["not_rollbacked_deposit_amount"]
    )
    assert (
        response_data["not_rollbacked_withdraw_amount"]
        == kwargs["not_rollbacked_withdraw_amount"]
    )
    assert response_data["transactions_count"] == kwargs["transactions_count"]
    assert (
        response_data["not_rollbacked_transactions_count"]
        == kwargs["not_rollbacked_transactions_count"]
    )
