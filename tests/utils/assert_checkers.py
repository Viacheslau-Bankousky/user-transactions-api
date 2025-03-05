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


def check_get_user_response_assertation(
    response_data: Dict,
    expected_user_id: int,
    expected_user_name: str,
    expected_email: str,
    expected_user_status: UserStatusEnum,
) -> None:
    assert response_data["id"] == expected_user_id
    assert response_data["name"] == expected_user_name
    assert response_data["email"] == expected_email
    validate_datetime_format(response_data["created"])
    assert response_data["status"] == expected_user_status
    check_balance(response_data=response_data)


def check_balance(response_data: List[Dict] | Dict) -> None:
    expected_currencies = {balance.get("currency") for balance in BALANCES}
    expected_money_sum = {balance.get("amount") for balance in BALANCES}
    if isinstance(response_data, list):
        for balance_item in response_data:
            check_currency_response_assertation(
                response_data=balance_item,
                expected_currencies=expected_currencies,
                expected_money_sum=expected_money_sum,
            )
    else:
        check_currency_response_assertation(
            response_data=response_data,
            expected_currencies=expected_currencies,
            expected_money_sum=expected_money_sum,
        )


def check_currency_response_assertation(
    response_data: Dict[str, str | List],
    expected_currencies: Set,
    expected_money_sum: Set,
) -> None:
    assert "balances" in response_data.keys()
    user_balances = cast(
        List[Dict[str, str]], response_data.get("balances")
    )
    estimated_currencies = {
        balance.get("currency") for balance in user_balances
    }
    estimated_money_sums = {balance.get("amount") for balance in user_balances}
    assert estimated_currencies == expected_currencies
    assert estimated_money_sums == expected_money_sum


def validate_datetime_format(
    date_str: str, date_format: str = "%Y-%m-%dT%H:%M:%S.%f"
) -> None:
    try:
        datetime.strptime(date_str, date_format)
    except ValueError:
        raise AssertionError(f"Date {date_str} doesnt match {date_format}")


def check_user_change_response(
    response_data: Dict,
    expected_user_id: int,
    expected_user_name: str,
    expected_email: str,
    expected_user_status: str,
) -> None:
    assert response_data["id"] == expected_user_id
    assert response_data["name"] == expected_user_name
    assert response_data["email"] == expected_email
    validate_datetime_format(response_data["created"])
    assert response_data["status"] == expected_user_status


def check_transaction_response_assertation(
    response_data: Dict,
    expected_amount: Decimal,
    expected_currency: str,
    expected_user_id: int,
    expected_status: str,
    expected_purpose: str,
) -> None:
    assert response_data["user_id"] == expected_user_id
    assert response_data["amount"] == expected_amount
    assert response_data["currency"] == expected_currency
    assert response_data["status"] == expected_status
    validate_datetime_format(response_data["created"])
    assert response_data["purpose"] == expected_purpose
