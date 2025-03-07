from fastapi import status

from exceptions.validation import BadRequestDataException

MAX_WEEKS_COUNT: int = 52


def check_weeks_count(weeks_count: int) -> None:
    if weeks_count > MAX_WEEKS_COUNT:
        raise BadRequestDataException(
            message="Too many weeks", status_code=status.HTTP_400_BAD_REQUEST
        )
