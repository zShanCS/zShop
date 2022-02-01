from typing import List
from fastapi import FastAPI
from fastapi.params import Depends
from sqlalchemy.orm.session import Session

from src import models
from src.database import engine, get_db

from src.routes import auth, item, user, cart


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(item.router)
app.include_router(cart.router)


# @app.get('/reviews', tags=['Review'], response_model=List[ReviewSchema.ReviewShowWithItem])
# def get_all_reviews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return crud.get_all_reviews(db=db, skip=skip, limit=limit)
