from sqlalchemy.orm import Session
from .models import User, History
from ..models import schemas
from ..core import security

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_profile(db: Session, user_id: int, profile: schemas.UserUpdate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        if profile.medical_history is not None:
            db_user.medical_history = profile.medical_history
        if profile.preferences is not None:
            db_user.preferences = profile.preferences
        db.commit()
        db.refresh(db_user)
    return db_user

def get_history(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(History).filter(History.owner_id == user_id).order_by(History.timestamp.desc()).offset(skip).limit(limit).all()

def create_user_history(db: Session, history: schemas.HistoryResponse, user_id: int):
    db_history = History(**history.dict(exclude={'id', 'owner_id', 'timestamp'}), owner_id=user_id)
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history
