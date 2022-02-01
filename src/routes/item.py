from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm.session import Session


from src import crud, schemas
from src.database import get_db
from src.util import get_current_user


router = APIRouter(
    prefix='/items',
    tags=['Item']
)


@router.get('/', response_model=List[schemas.Item])
def all_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_items(skip=skip, limit=limit, db=db)


@router.post('/', response_model=schemas.ItemShowCreate)
def create_user_item(item: schemas.ItemCreate, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    return crud.create_user_item(db=db, item=item, owner_id=user.id)


@router.get('/{id}', response_model=schemas.ItemShow)
def get_item_by_id(id: int, db: Session = Depends(get_db)):
    item = crud.get_item(db=db, item_id=id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No Item with id: {id} found.')
    print(item.__dict__)
    return item


@router.post('/{item_id}/review',  response_model=schemas.ReviewShow)
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
