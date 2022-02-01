from fastapi import HTTPException, status
from sqlalchemy.orm import Session


from src import models, schemas
from . import util
from .hashing import get_password_hash


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, user_email: str):
    return db.query(models.User).filter(models.User.email == user_email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(name=user.name, email=user.email,
                          hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def create_user_item(db: Session, item: schemas.ItemCreate, owner_id: int):
    if item.price <= 0:
        raise util.item_price_exception
    db_item = models.Item(**item.dict(), owner_id=owner_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def create_item_review(db: Session, user_id: int, item_id: int, review: schemas.ReviewCreate):
    db_review = models.Review(
        **review.dict(), user_id=user_id, item_id=item_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def get_all_reviews(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Review).offset(skip).limit(limit).all()


def get_user_item_review(db: Session, user_id: int, item_id: int):
    return db.query(models.Review).filter(
        models.Review.user_id == user_id, models.Review.item_id == item_id).first()
