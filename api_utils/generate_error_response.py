"""
This module provides a function to generate error responses in JSON format.

The main functionality of this module is provided by the function
`generate_error_response`, which takes a status code, an error type, and an
error message as arguments to generate a JSON response containing an error
indication.

The FastAPI's `JSONResponse` is utilized to format the output.
The response includes the HTTP status code, and a content dictionary that
indicates the operation result is False, and includes the provided error
type and error message.
"""

from fastapi.responses import JSONResponse


def generate_error_response(
    status_code: int,
    error_message: str,
) -> JSONResponse:
    """
    Generate a JSON response indicating an error.

    This function builds a standard JSON response to indicate an error.
    It includes HTTP status code and a JSON content containing the result
    status (always False), along with the provided error type and error
    message.

    Args:
        status_code (int): HTTP status code for the response.
        error_message (str): A detailed message about the occurred error.

    Returns:
        JSONResponse: A FastAPI response object with status_code and
            a JSON content indicating error type and message.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error_message": error_message,
        },
    )
