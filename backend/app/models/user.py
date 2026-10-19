from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Stored lowercased by the auth service, so the unique index is case-insensitive
    # in practice. 320 is the longest address the email RFCs allow.
    email: Mapped[str] = mapped_column(String(320), unique=True)
    # An Argon2 hash string from pwdlib, never the password itself
    hashed_password: Mapped[str] = mapped_column(String(255))
    # Included in every JWT; incrementing it invalidates all of the user's tokens
    token_version: Mapped[int] = mapped_column(default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
