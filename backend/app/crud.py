from sqlalchemy.orm import Session
from backend.app import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Password utils
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

# User CRUD
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

# Leaderboard
def leaderboard(db: Session, n: int):
    return db.query(models.User).order_by(models.User.points.desc()).limit(n).all()

# Action logging
def log_action(db: Session, user_id: int, action_code: str, meta_data: str = None):
    action = db.query(models.ActionType).filter(models.ActionType.code == action_code).first()
    if not action:
        return None

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None

    user.points += action.points
    user_action = models.UserAction(
        user_id=user_id,
        action_code=action_code,
        points_awarded=action.points,
        meta_data=meta_data,
    )

    db.add(user_action)
    db.commit()
    db.refresh(user_action)
    return user_action
