import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


def require_basic_auth(
    credentials: HTTPBasicCredentials = Depends(security),
) -> str:
    expected_username = os.getenv("BASIC_AUTH_USERNAME", "admin")
    expected_password = os.getenv("BASIC_AUTH_PASSWORD", "secret")

    username_is_valid = secrets.compare_digest(
        credentials.username,
        expected_username,
    )
    password_is_valid = secrets.compare_digest(
        credentials.password,
        expected_password,
    )

    if not username_is_valid or not password_is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
