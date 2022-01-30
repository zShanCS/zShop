from sqlalchemy import Column, Integer, String, ForeignKey, Float, SMALLINT
from sqlalchemy.orm import relationship

from .database import Base


class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rating = Column(SMALLINT, index=True)
    review = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    item_id = Column(Integer, ForeignKey('items.id'))

    reviewer = relationship('User', back_populates='reviews')
    item = relationship('Item', back_populates='reviews')


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True)
    price = Column(Float, index=True, nullable=False)
    description = Column(String)

    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship('User', back_populates='items')
    reviews = relationship('Review', back_populates='item')


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)

    items = relationship('Item', back_populates='owner')
    reviews = relationship('Review', back_populates='reviewer')
