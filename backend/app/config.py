from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings, read from environment variables (and a local .env file)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # SQLAlchemy URL, e.g. postgresql+psycopg://user:password@host:5432/dbname
    database_url: str

    # Signs and verifies JWTs. Anyone with this key can forge a token for any user.
    # 32 is the minimum length RFC 7518 recommends for HS256.
    # Generate one with: python -c "import secrets; print(secrets.token_urlsafe(32))"
    jwt_secret_key: str = Field(min_length=32)
    # No refresh tokens yet, so this balances how long a stolen token works
    # against how often users have to log in again
    access_token_expire_minutes: int = 60


settings = Settings()  # type: ignore[call-arg]  # values come from the environment
