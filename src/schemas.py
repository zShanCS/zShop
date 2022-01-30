from typing import List, Optional
from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass

# for reading data from db


class Item(ItemBase):
    id: int
    owner_id: int

    class Config():
        orm_mode = True


class UserBase(BaseModel):
    name: Optional[str] = None
    email: str


class UserCreate(UserBase):
    password: str

# for reading data from db


class User(UserBase):
    id: int
    items: List[Item] = []

    class Config():
        orm_mode = True


class UserInDB(User):
    hashed_password: str
