from datetime import datetime

from sqlalchemy import Column, TIMESTAMP, VARCHAR, Integer, Boolean, Text, ForeignKey, CHAR, BigInteger, SmallInteger
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import BYTEA

Base = declarative_base()


class Menu(Base):
    __tablename__: str = "menu"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer)
    name = Column(Text)
    photo = Column(BYTEA)
    type_id = Column(Integer, ForeignKey("types.id", ondelete="NO ACTION"))
    price = Column(Text)
    size_id = Column(Integer, ForeignKey("sizes.id", ondelete="NO ACTION"))
    description = Column(Text)


class PositionMenu(Base):
    __tablename__ = 'position_menu'

    id = Column(Integer, primary_key=True)
    name = Column(Text)


class Type(Base):
    __tablename__: str = "types"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


class Size(Base):
    __tablename__: str = "sizes"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


class Basket(Base):
    __tablename__: str = "baskets"
    
    id = Column(Integer, primary_key=True)
    pizza_id = Column(Integer, default=1)
    count = Column(Integer, default=1)
    user_id = Column(BigInteger(), default=1)

    


