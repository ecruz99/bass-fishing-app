from sqlalchemy.orm import Session

from app.models import User


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """The user with this id, or None if there isn't one (for example, deleted)."""
    return db.get(User, user_id)
