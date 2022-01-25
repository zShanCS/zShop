from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.sqltypes import Float
from .database import Base


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    price = Column(Float)
