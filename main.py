from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.orm.session import Session
from fastapi.security import OAuth2PasswordRequestForm

from src import crud, schemas, models
from src.database import engine, get_db
from src.token import create_access_token
from src.util import authenticate_user, login_exception, get_current_user

from src.oauth2 import oauth2_scheme

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


@app.post('/token', response_model=schemas.Token)
async def login_for_token_access(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(email=form_data.username,
                             password=form_data.password, db=db)
    if not user:
        raise login_exception
    access_token = create_access_token(data={"sub": user.email})
    return {'access_token': access_token, 'token_type': 'bearer'}


@app.get('/locked/')
async def read_locked_data(token: str = Depends(oauth2_scheme)):
    return {'token': token}


@app.get('/items/', tags=['Item'], response_model=List[schemas.Item])
def all_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_items(skip=skip, limit=limit, db=db)


@app.get('/item/{id}', tags=['Item'], response_model=schemas.ItemShow)
def get_item_by_id(id: int, db: Session = Depends(get_db)):
    item = crud.get_item(db=db, item_id=id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No Item with id: {id} found.')
    print(item.__dict__)
    return item


@app.post("/users/", tags=['User'],  response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user_email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/{user_id}", tags=['User'], response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    print(db_user.__dict__)
    return db_user


@app.get("/users/", tags=['User'], response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.post('/user/items', tags=['User'], response_model=schemas.Item)
def create_user_item(item: schemas.ItemCreate, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    return crud.create_user_item(db=db, item=item, owner_id=user.id)


@app.post('/items/{item_id}/review', tags=['Review'], response_model=schemas.ReviewShow)
def create_review(item_id: int, review: schemas.ReviewCreate, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    if review.rating < 0 or review.rating > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='rating must be between 0 and 5')
    if len(review.review) < 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='review text too small')
    item = crud.get_item(db=db, item_id=item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No Item with id: {item_id} found.')
    db_review = crud.create_item_review(
        db=db, item_id=item.id, user_id=user.id, review=review)
    return db_review


@app.get('/reviews', tags=['Review'], response_model=List[schemas.ReviewShow])
def get_all_reviews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all_reviews(db=db, skip=skip, limit=limit)
