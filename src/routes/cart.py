from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlalchemy.orm.session import Session

from src import models, schemas
from src.database import get_db
from src.util import get_current_user

router = APIRouter(
    prefix='/users/me/cart',
    tags=['Cart']
)


@router.get('/',  response_model=List[schemas.CartItemShow])
def get_current_user_cart(user: schemas.User = Depends(get_current_user)):
    return user.cart


@router.post('/')
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


@router.delete('/')
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
