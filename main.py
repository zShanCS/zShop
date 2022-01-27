from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.orm.session import Session
from fastapi.security import OAuth2PasswordBearer

from src import crud, schemas, models
from src.database import engine, get_db

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

models.Base.metadata.create_all(bind=engine)


@app.get('/locked/')
async def read_locked_data(token: str = Depends(oauth2_scheme)):
    return {'token': token}


@app.get('/items/', tags=['Item'], response_model=List[schemas.Item])
def all_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_items(skip=skip, limit=limit, db=db)


@app.get('/item/{id}', tags=['Item'], response_model=schemas.Item)
def get_item_by_id(id: int, db: Session = Depends(get_db)):
    item = crud.get_item(db=db, item_id=id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No Item with id: {id} found.')
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
    return db_user


@app.get("/users/", tags=['User'], response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.post('/user/{user_id}/items', tags=['User'], response_model=schemas.Item)
def create_user_item(user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    user = crud.get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'no user with {user_id} found')
    return crud.create_user_item(db=db, item=item, owner_id=user.id)
