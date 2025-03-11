from datetime import date
from typing import Annotated, AsyncContextManager, List, Sequence, cast

from celery.result import AsyncResult, GroupResult
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from authentication.user_management import check_user_has_token
from core.database import get_session
from core.logger_configuration import app_logger
from models.transactions import Transaction
from models.users import UserBalance
from repositories.transactions import take_transactions
from schemas.statistic import ResponseStatisticModel
from schemas.transactions import (
    RequestTransactionModel,
    TransactionModel,
)
from services.payment import process_payment
from services.preconditions import (
    ensure_valid_transaction,
    ensure_valid_user_balance,
)
from services.refund import process_refund
from services.rollback import make_roll_back
from statistic.helpers import generate_date_ranges
from statistic.tasks.processing import calculate_statistics_for_all_dates

# from statistic.tasks.responses import create_statistic_response
# from statistic.tasks.transactions import (
#     calculate_not_rollbacked_deposit_amount,
#     calculate_not_rollbacked_transactions,
#     calculate_not_rollbacked_withdraw_amount,
#     calculate_transactions,
# )
# from statistic.tasks.users import (
#     calculate_registered_and_deposit_users,
#     calculate_registered_and_not_rollbacked_deposit_users,
#     calculate_registered_users,
# )
from validators.statisctic import check_weeks_count
from validators.transactions import (
    check_transaction_status,
    check_transactions_exist,
)

SESSION_DEPENDENCY = Annotated[
    AsyncContextManager[AsyncSession], Depends(get_session)
]

router = APIRouter()


@router.get(
    "/transactions",
    response_model=Sequence[TransactionModel] | None,
    status_code=status.HTTP_200_OK,
    description="Get all transactions",
    response_description="All transactions returned successfully",
    dependencies=[Depends(check_user_has_token)],
)
async def get_transactions(
    session_manager: SESSION_DEPENDENCY,
):
    app_logger.info("Received GET request for /transactions endpoint")
    async with session_manager as session:
        transactions: Sequence[Transaction] = await take_transactions(
            session=session,
        )
        check_transactions_exist(transactions=transactions)
        transactions = cast(Sequence[Transaction], transactions)
        app_logger.info(
            f"Fetched {len(transactions)} transactions from database"
        )
        return transactions


@router.get(
    "/users/{user_id:int}/transactions",
    response_model=Sequence[TransactionModel] | None,
    status_code=status.HTTP_200_OK,
    description="Get transactions by user id",
    response_description="Transactions returned successfully",
    dependencies=[Depends(check_user_has_token)],
)
async def get_transaction_by_user_id(
    session_manager: SESSION_DEPENDENCY,
    user_id: int,
):
    app_logger.info(
        f"Received GET request for /users/{user_id}/" f"transactions endpoint"
    )
    async with session_manager as session:
        transactions: Sequence[Transaction] = await take_transactions(
            session=session,
            user_id=user_id,
        )
        check_transactions_exist(transactions=transactions)
        transactions = cast(Sequence[Transaction], transactions)
        app_logger.info(
            f"Fetched {len(transactions)} transactions from database"
        )
        return transactions


@router.get(
    "/transactions/{current_status:str}",
    response_model=Sequence[TransactionModel] | None,
    status_code=status.HTTP_200_OK,
    description="Get transactions by status",
    response_description="Transactions returned successfully",
    dependencies=[Depends(check_user_has_token)],
)
async def get_transaction_by_status(
    session_manager: SESSION_DEPENDENCY,
    current_status: str,
):
    app_logger.info(
        f"Received GET request for /transactions/" f"{current_status} endpoint"
    )
    check_transaction_status(transaction_status=current_status)
    async with session_manager as session:
        transactions: Sequence[Transaction] = await take_transactions(
            session=session,
            status=current_status,
        )
        check_transactions_exist(transactions=transactions)
        transactions = cast(Sequence[Transaction], transactions)
        app_logger.info(
            f"Fetched {len(transactions)} transactions from database"
        )
        return transactions


@router.get(
    "/users/{user_id:int}/transactions/{current_status:str}",
    response_model=List[TransactionModel] | None,
    status_code=status.HTTP_200_OK,
    description="Get transactions by user id and status",
    response_description="Transactions returned successfully",
    dependencies=[Depends(check_user_has_token)],
)
async def get_transaction_by_user_id_and_status(
    session_manager: SESSION_DEPENDENCY,
    user_id: int,
    current_status: str,
):
    app_logger.info(
        f"Received GET request for /users/{user_id}"
        f"/transactions/{current_status}"
    )
    check_transaction_status(transaction_status=current_status)
    async with session_manager as session:
        transactions: Sequence[Transaction] = await take_transactions(
            session=session,
            user_id=user_id,
            status=current_status,
        )
        check_transactions_exist(transactions=transactions)
        transactions = cast(Sequence[Transaction], transactions)
        app_logger.info(
            f"Fetched {len(transactions)} transactions from database"
        )
        return transactions


@router.post(
    "/users/{user_id:int}/transactions/refund",
    response_model=TransactionModel,
    status_code=status.HTTP_201_CREATED,
    description="Create top up transaction",
    response_description="Top up transaction created successfully",
    dependencies=[Depends(check_user_has_token)],
)
async def add_top_up_transaction(  # noqa: WPS210
    session_manager: SESSION_DEPENDENCY,
    user_id: int,
    transaction_data: RequestTransactionModel,
):
    app_logger.info(
        f"Received POST request for /users/{user_id}/"
        "transactions/refund endpoint "
    )
    async with session_manager as session:
        transaction: Transaction = await process_refund(
            session=session,
            user_id=user_id,
            transaction_data=transaction_data,
        )
        app_logger.info(
            f"Topping up transaction ID={transaction.id} "
            f"for user ID={user_id} processed successfully."
        )
        return transaction


@router.post(
    "/users/{user_id:int}/transactions/deduct",
    response_model=TransactionModel,
    status_code=status.HTTP_201_CREATED,
    description="Create deduct transaction",
    response_description="Deduct transaction created successfully",
    dependencies=[Depends(check_user_has_token)],
)
async def add_deduct_transaction(  # noqa: WPS210
    session_manager: SESSION_DEPENDENCY,
    user_id: int,
    transaction_data: RequestTransactionModel,
):
    app_logger.info(
        f"Received POST request for /users/{user_id}"
        f"/transactions/deduct/ endpoint "
    )
    async with session_manager as session:
        new_transaction: Transaction = await process_payment(
            session=session,
            user_id=user_id,
            transaction_data=transaction_data,
        )
        app_logger.info(
            f"Withdrawal transaction ID={new_transaction.id} "
            f"for user ID={user_id} processed successfully."
        )
        return new_transaction


@router.patch(
    "/users/{user_id:int}/transactions/{transaction_id:int}",
    response_model=TransactionModel | None,
    status_code=status.HTTP_200_OK,
    description="Rollback transaction",
    response_description="Transaction rollbacked successfully",
    dependencies=[Depends(check_user_has_token)],
)
async def rollback_transaction(
    session_manager: SESSION_DEPENDENCY,
    user_id: int,
    transaction_id: int,
):
    app_logger.info(
        f"Received PATCH request for /users/{user_id}/"
        f"transactions/{transaction_id} endpoint"
    )
    async with session_manager as session:
        user_transaction: Transaction = await ensure_valid_transaction(
            session=session,
            user_id=user_id,
            transaction_id=transaction_id,
        )
        user_balance: UserBalance = await ensure_valid_user_balance(
            session=session,
            currency=user_transaction.currency,
            user_id=user_id,
        )
        roll_backed_transaction: Transaction = await make_roll_back(
            session=session,
            transaction=user_transaction,
            user_balance=user_balance,
        )
    app_logger.info(
        f"Transaction with ID {transaction_id} for user with ID {user_id}"
        f" roll backed successfully"
    )
    return roll_backed_transaction


# @router.get(
#     "/transactions/analysis/period/{weeks_count:int}",
#     status_code=status.HTTP_200_OK,
#     description="Show statistics about transactions.",
#     response_description="Statistics returned successfully.",
#     dependencies=[Depends(check_user_has_token)],
# )
# async def get_transaction_analysis(weeks_count: int) -> dict[str, str]:
#     app_logger.info("Received GET request for /transactions/analysis/period"
#                     " endpoint")
#     check_weeks_count(weeks_count=weeks_count)
#     date_ranges: List[tuple[date, date]] = generate_date_ranges(
#         weeks_count=weeks_count
#     )
#
#     statistics_workflow = chord(
#         [
#             calculate_registered_users.s(date_ranges),
#             calculate_registered_and_deposit_users.s(date_ranges),
#             calculate_registered_and_not_rollbacked_deposit_users.s(
#                 date_ranges
#             ),
#             calculate_transactions.s(date_ranges),
#             calculate_not_rollbacked_transactions.s(date_ranges),
#             calculate_not_rollbacked_deposit_amount.s(date_ranges),
#             calculate_not_rollbacked_withdraw_amount.s(date_ranges),
#         ]
#     )( create_statistic_response.s(date_ranges))
#
#     statistics_workflow = calculate_registered_users.s(date_ranges).apply_async()
#     app_logger.info(
#             f"Statistics workflow created with ID: {statistics_workflow.id}"
#         )
#     return {"Statistics workflow ID": statistics_workflow.id}
@router.get(
    "/transactions/analysis/period/{weeks_count:int}",
    status_code=status.HTTP_200_OK,
    description="Show statistics about transactions.",
    response_description="Statistics returned successfully.",
    dependencies=[Depends(check_user_has_token)],
)
async def get_transaction_analysis(weeks_count: int) -> dict[str, str]:
    app_logger.info(
        "Received GET request for /transactions/analysis/period" " endpoint"
    )
    check_weeks_count(weeks_count=weeks_count)
    date_ranges: List[tuple[date, date]] = generate_date_ranges(
        weeks_count=weeks_count
    )
    try:
        statistics_workflow: AsyncResult = (
            calculate_statistics_for_all_dates.s(date_ranges).apply_async()
        )
        app_logger.info(
            f"Statistics workflow created with ID: {statistics_workflow.id}"
        )
        return {"Statistics workflow ID": statistics_workflow.id}
    except Exception as exc:
        app_logger.error(
            f"Error occurred while creating statistics workflow: {exc}"
        )
        return {"error": "Error occurred while creating statistics workflow"}


@router.get(
    "/transactions/analysis/status/{statistics_workflow_id:str}",
    status_code=status.HTTP_200_OK,
    description="Show statistics about transactions.",
    response_description="Statistics returned successfully.",
    dependencies=[Depends(check_user_has_token)],
)
async def get_statistics_workflow_status(
    statistics_workflow_id: str,
) -> dict[str, str]:
    app_logger.info(
        "Received GET request for /transactions/analysis/status" " endpoint"
    )
    statistics_result = AsyncResult(statistics_workflow_id)

    if not statistics_result:
        app_logger.info(
            f"Statistics workflow ID {statistics_workflow_id} " f"not found."
        )
        return {
            "statistics_workflow_id": statistics_workflow_id,
            "status": "NOT FOUND",
        }

    if statistics_result.ready():
        app_logger.info(
            f"Showing statistics workflow ID {statistics_workflow_id} "
        )
        # return {
        #     "statistics_workflow_id": statistics_workflow_id,
        #     "status": "SUCCESS",
        #     "results": [
        #         ResponseStatisticModel(**result)
        #         for result in statistics_result.result
        #     ],
        # }
        if statistics_result.children:
            results = []
            for group in statistics_result.children:
                try:
                    if isinstance(group, GroupResult):
                        group_results = group.join()
                        app_logger.info(f"Extracted Group Results: {group_results}")
                        results.append(group_results)
                    else:
                        app_logger.warning(f"Unexpected result type: {type(group)}")
                except Exception as e:
                    app_logger.error(f"Error retrieving results from GroupResult: {e}")
            app_logger.info(f"Final Extracted RESULTS: {results}")

    elif statistics_result.failed():
        app_logger.info(
            f"Statistics workflow ID {statistics_workflow_id}"
            f" failed {statistics_result.traceback} "
        )
        return {
            "statistics_workflow_id": statistics_workflow_id,
            "status": "FAILURE",
            "details": str(statistics_result.traceback),
        }
    else:
        app_logger.info(
            f"Statistics workflow ID {statistics_workflow_id} "
            f"is not ready yet. "
        )
        return {
            "statistics_workflow_id": statistics_workflow_id,
            "status": statistics_result.status,
        }
