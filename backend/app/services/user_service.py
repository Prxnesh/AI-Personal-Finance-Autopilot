from sqlalchemy.orm import Session
from ..models import User
from ..schemas import UserCreate
from ..utils.auth import get_password_hash, verify_password


def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user with hashed password
    """
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise ValueError("Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Authenticate user with email and password
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


def get_user_by_email(db: Session, email: str) -> User:
    """
    Get user by email
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User:
    """
    Get user by ID
    """
    return db.query(User).filter(User.id == user_id).first()
