from datetime import date

from core.pydantic_base import BasePydanticModel


class ResponseStatisticModel(BasePydanticModel):
    start_date: date
    end_date: date
    registered_users_count: int
    registered_and_deposit_users_count: int
    registered_and_not_rollbacked_deposit_users_count: int
    not_rollbacked_deposit_amount: str
    not_rollbacked_withdraw_amount: str
    transactions_count: int
    not_rollbacked_transactions_count: int
