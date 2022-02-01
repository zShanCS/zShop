from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm.session import Session
from typing import List

from src import crud, schemas
from src.database import get_db
from src.util import get_current_user


router = APIRouter(
    prefix='/users',
    tags=['User']
)


@router.get("/",  response_model=List[schemas.UserProfile])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.post("/",   response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user_email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@router.get("/{user_id}",  response_model=schemas.UserProfile)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    print(db_user.__dict__)
    return db_user


@router.get('/me/', response_model=schemas.UserOwnProfile)
def get_current_user_detail(user: schemas.User = Depends(get_current_user)):
    return user
