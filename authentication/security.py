"""
This module provides functions for secure password hashing and verification.

The primary functionalities include:
- Generating a hashed version of a plain password suitable for secure storage.
- Verifying that a provided plain password matches a previously hashed
 password.

The `passlib` library is utilized to handle password hashing and verification,
relying on the bcrypt algorithm for security.
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain password matches a given hashed password.

    This function checks if the provided plain password, when hashed,
    corresponds to the stored hashed password. It uses bcrypt hashing
    algorithm for verification.

    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The hashed password to check against.

    Returns:
        bool: True if the plain password matches the hashed password;
                False otherwise.

    Notes:
        - Use this function to authenticate users by comparing their submitted
            password with an existing hashed password in the database
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain text password for secure storage.

    This function generates a hashed version of the provided password
    using the bcrypt hashing algorithm. The hashed password can be stored
    safely in a database or other persistent storage.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: A hashed representation of the provided password.

    Notes:
        - Hashed passwords cannot be reversed into their original plain
         text form.
        - Use this function to securely store user passwords during
         registration or password update.
    """
    return pwd_context.hash(password)
