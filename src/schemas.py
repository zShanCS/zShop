from typing import List, Optional
from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    price: float
    stock:int
    description: Optional[str] = None


class ItemBase(ItemCreate):
    id: int

    class Config():
        orm_mode = True


# for reading data from db


class UserBase(BaseModel):
    id: int
    name: Optional[str] = None
    email: str

    class Config():
        orm_mode = True


class Item(ItemBase):
    owner: UserBase

    class Config():
        orm_mode = True


class UserCreate(UserBase):
    password: str

# for reading data from db


class User(UserBase):
    items: List[ItemBase] = []

    class Config():
        orm_mode = True


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class ReviewCreate(BaseModel):
    rating: int
    review: str


class ReviewBase(ReviewCreate):
    id: int

    class Config():
        orm_mode = True


class Review(ReviewBase):

    user_id: int
    item_id: int

    class Config():
        orm_mode = True


class ReviewShow(ReviewBase):
    reviewer: UserBase


class ReviewShowWithItem(ReviewShow):
    item: ItemBase


class ItemShow(ItemBase):
    id: int
    owner_id: int
    reviews: List[ReviewShow] = []
    owner: UserBase

    class Config():
        orm_mode = True

