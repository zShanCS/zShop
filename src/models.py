from sqlalchemy import Column, Integer, String, ForeignKey, Float, SMALLINT, DateTime
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
    available = Column(Integer)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship('User', back_populates='items')
    reviews = relationship('Review', back_populates='item')
    carts = relationship('Cart', back_populates='item')


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)

    items = relationship('Item', back_populates='owner')
    reviews = relationship('Review', back_populates='reviewer')
    cart = relationship('Cart', back_populates='owner')


class Cart(Base):
    __tablename__ = 'carts'
    id = Column(Integer, primary_key=True, index=True)
    last_updated = Column(DateTime, index=True)

    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    item_id = Column(Integer, ForeignKey('items.id'), index=True)

    quantity = Column(Integer)

    owner = relationship('User', back_populates='cart')
    item = relationship('Item', back_populates='carts')
