"""
This module defines a custom exception for errors related to Celery tasks.

It builds upon the base exception handling mechanism provided by
`BaseAPIException`to introduce a specific exception class for scenarios
where Celery tasks fail or unexpected issues occur during task management.

The exception defined in this module is intended to ensure consistent error
handling for Celery-related operations within the application.
"""

from core.base_exception import BaseAPIException


class CeleryException(BaseAPIException):
    """
    A custom exception class to handle Celery task-related errors.

    This exception is used to represent errors that occur during the execution
    or management of Celery tasks, such as task failures, timeout errors, or
    broker/worker-related issues.

    Inherits from:
        BaseAPIException: Provides a foundation for standardized error handling
        in the application.
    """

    ...
