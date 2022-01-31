from datetime import datetime
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


@app.get('/token/')
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


@app.get("/users/{user_id}", tags=['User'], response_model=schemas.UserProfile)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    print(db_user.__dict__)
    return db_user


@app.get("/users/", tags=['User'], response_model=List[schemas.UserProfile])
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
    # disallow the user from reviewing same thing twice
    user_item_review = crud.get_user_item_review(
        db=db, user_id=user.id, item_id=item_id)
    if user_item_review:
        # means user already has a review for this item => disallow current review
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'User {user.id} already has a review for item {item_id}')
    item = crud.get_item(db=db, item_id=item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No Item with id: {item_id} found.')
    db_review = crud.create_item_review(
        db=db, item_id=item.id, user_id=user.id, review=review)
    return db_review


@app.get('/reviews', tags=['Review'], response_model=List[schemas.ReviewShowWithItem])
def get_all_reviews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all_reviews(db=db, skip=skip, limit=limit)


@app.post('/me/', response_model=schemas.UserProfile)
def get_current_user_detail(user: schemas.User = Depends(get_current_user)):
    return user


@app.get('/me/cart', tags=['Cart'], response_model=List[schemas.CartItemShow])
def get_current_user_cart(user: schemas.User = Depends(get_current_user)):
    return user.cart


@app.post('/me/cart/', tags=['Cart'])
def update_cart(item_id: int, new_quantity: int, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    if new_quantity < 1 or new_quantity > 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Quantity cant be less than 1 or more than 10.')
    item_query = db.query(models.Item).filter(models.Item.id == item_id)
    if not item_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No Item with id: {item_id} found.')
    # now we have item, we check if quanity is available in that item
    # we do this by checking if availbale quanity  plus cart quantity is less than or equal to new quantity

    # getting user's cart
    user_cart_item = db.query(models.Cart).filter(
        models.Cart.user_id == user.id, models.Cart.item_id == item_id)
    old_quantity = 0  # we assume it may or may not be in the cart

    new_cart_item = None
    # if item already present just update its quanity to new quantity
    if user_cart_item.first():
        # get quantity of item from cart
        old_quantity = user_cart_item.first().quantity
        # check if cart quantity plus stock quantity is less than new
        if item_query.first().available + old_quantity < new_quantity:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f'Quantity of {new_quantity} is not allowed at the moment. try less quanitity')
        # item is available so we just put the new quantity in to users cart and decrease total available
        user_cart_item.update({'last_updated': datetime.utcnow(
        ),  'quantity': new_quantity})
    else:
        if item_query.first().available < new_quantity:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f'Quantity of {new_quantity} is not allowed at the moment. try less quanitity')
        # means user didnt have this item in cart
        new_cart_item = models.Cart(last_updated=datetime.utcnow(
        ), user_id=user.id, item_id=item_id, quantity=new_quantity)
        db.add(new_cart_item)
    # now update item to have less available quantity
    item_query.update(
        {'available': item_query.first().available + old_quantity - new_quantity})
    db.commit()
    if new_cart_item:
        db.refresh(new_cart_item)
    return 'changes updated'


@app.delete('/me/cart/', tags=['Cart'])
def delete_cart_item(item_id: int, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    item_query = db.query(models.Item).filter(models.Item.id == item_id)
    if not item_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No Item with id: {item_id} found.')
    # item exists
    # now check that user actually has the item in thier cart
    user_cart_item = db.query(models.Cart).filter(
        models.Cart.user_id == user.id, models.Cart.item_id == item_id)
    if not user_cart_item.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No Item with id: {item_id} found in the users cart therefore cannot delete')
    # else item is in the cart
    old_quantity = user_cart_item.first().quantity
    # delete cart item
    user_cart_item.delete(synchronize_session=False)
    # re add item into stock for others to buy
    item_query.update(
        {'available': item_query.first().available + old_quantity})
    db.commit()
    return 'item deleted from cart'
