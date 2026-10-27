from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SignupRequest(BaseModel):
    """The body of POST /api/v1/auth/signup."""

    email: EmailStr
    # NIST SP 800-63B: a minimum length and no composition rules. The maximum
    # stops huge inputs from making Argon2 do expensive work.
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """The body of POST /api/v1/auth/login."""

    email: EmailStr
    # Only the cap that protects Argon2. A minimum would lock out existing users
    # if the signup rules ever got stricter.
    password: str = Field(max_length=128)


class TokenResponse(BaseModel):
    """A successful login: the OAuth2 response shape most clients expect."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """A user as the API returns it. Never includes the password hash."""

    # Lets model_validate read a SQLAlchemy User's attributes, not just a dict
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    created_at: datetime
