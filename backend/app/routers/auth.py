from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.exceptions import EmailAlreadyRegisteredError
from app.schemas.auth import SignupRequest, UserResponse
from app.services.auth import register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(
    body: SignupRequest, db: Annotated[Session, Depends(get_db)]
) -> UserResponse:
    """Create an account. The client logs in separately to get a token."""
    try:
        user = register_user(db, body.email, body.password)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        ) from None
    return UserResponse.model_validate(user)
