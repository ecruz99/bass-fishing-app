from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.repositories.users import get_user_by_id
from app.security import InvalidTokenError, decode_access_token

# Reads "Authorization: Bearer <token>" (ADR 0003). auto_error=False hands a missing
# or non-Bearer header to us as None, so every failure gets the same 401 below.
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """FastAPI dependency: the user the request's access token belongs to.

    Rejects a missing or invalid token, a user that no longer exists, and a token
    issued before the user's token_version last changed (password change or
    log out everywhere). All of them get the same 401.
    """
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        # The HTTP spec says a 401 must name the auth scheme the client should use
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    try:
        claims = decode_access_token(credentials.credentials)
    except InvalidTokenError:
        raise unauthorized from None

    user = get_user_by_id(db, claims.user_id)
    if user is None or user.token_version != claims.token_version:
        raise unauthorized
    return user


# Lets endpoints write `user: CurrentUser` instead of repeating the Depends
CurrentUser = Annotated[User, Depends(get_current_user)]
