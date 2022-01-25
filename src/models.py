from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

from .database import Base


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True)
    price = Column(Float, index=True, nullable=False)
    description = Column(String)

    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship('User', back_populates='items')


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)

    items = relationship('Item', back_populates='owner')
