from datetime import datetime
from logging import lastResort
from typing import List, Optional
from pydantic import BaseModel


class Cart_DB(BaseModel):
    id: int
    last_updated: datetime
    user_id: int
    item_id: int
    quantity: int

    class Config():
        orm_mode = True


class ItemCreate(BaseModel):
    name: str
    price: float
    available: int
    description: Optional[str] = None


class ItemBase(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None

    class Config():
        orm_mode = True


class ItemInfo(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None

    class Config():
        orm_mode = True


class CartItemShow(BaseModel):
    item: ItemInfo
    last_updated: datetime
    quantity: int

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


class ItemShowCreate(Item):
    available: int

    class Config():
        orm_mode = True


class ItemShowOwner(ItemBase):
    available: int

    class Config():
        orm_mode = True


class UserCreate(UserBase):
    password: str

# for reading data from db


class User(UserBase):
    items: List[Item] = []

    class Config():
        orm_mode = True


class UserProfile(User):
    cart: List[CartItemShow] = []

    class Config():
        orm_mode = True


class UserOwnProfile(UserProfile):
    items: List[ItemShowOwner] = []

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
    item: ItemInfo


class ItemShow(ItemBase):
    reviews: List[ReviewShow] = []
    owner: UserBase

    class Config():
        orm_mode = True
