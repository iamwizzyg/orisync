from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


def register_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user account.
    Raises ValueError if the email is already registered.
    """
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise ValueError("Email already registered")

    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, email: str, password: str) -> str:
    """
    Verify credentials and return a JWT access token.
    Raises ValueError if credentials are invalid.

    Note: The error message is deliberately vague.
    Saying "email not found" vs "wrong password" separately
    lets attackers enumerate valid email addresses.
    Always return the same message for both failure cases.
    """
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid email or password")

    if not user.is_active:
        raise ValueError("Account is inactive")

    token = create_access_token(data={"sub": user.email})
    return token
