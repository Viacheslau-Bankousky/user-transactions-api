from datetime import datetime
from typing import Dict, List, Set, cast
from core.constants import DEFAULT_AMOUNT
from models.enums import UserStatusEnum

BALANCES: List[Dict[str, str | float]] = [
    {"currency": "USD", "amount": DEFAULT_AMOUNT},
    {"currency": "EUR", "amount": DEFAULT_AMOUNT},
    {"currency": "AUD", "amount": DEFAULT_AMOUNT},
    {"currency": "CAD", "amount": DEFAULT_AMOUNT},
    {"currency": "ARS", "amount": DEFAULT_AMOUNT},
    {"currency": "PLN", "amount": DEFAULT_AMOUNT},
    {"currency": "BTC", "amount": DEFAULT_AMOUNT},
    {"currency": "ETH", "amount": DEFAULT_AMOUNT},
    {"currency": "DOGE", "amount": DEFAULT_AMOUNT},
    {"currency": "USDT", "amount": DEFAULT_AMOUNT},
]


def check_get_user_response_assertation(
    response_data: Dict,
    expected_user_id: int,
    expected_user_name: str,
    expected_email: str,
) -> None:
    assert response_data["id"] == expected_user_id
    assert response_data["name"] == expected_user_name
    assert response_data["email"] == expected_email
    validate_datetime_format(response_data["created"])
    assert response_data["status"] == UserStatusEnum.ACTIVE
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
    response_data: Dict[str, str | float | List],
    expected_currencies: Set,
    expected_money_sum: Set,
) -> None:
    assert "balances" in response_data.keys()
    user_balances = cast(
        List[Dict[str, str | float]], response_data.get("balances")
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
