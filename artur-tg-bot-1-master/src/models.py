from sqlalchemy import Integer, String, ForeignKey, Column, Date, DateTime
from sqlalchemy.sql import func

from datetime import date, datetime

from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Pass(Base):
    __tablename__ = "passes"
    
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    
    people = relationship("Person", back_populates="pass_obj")
    
    date_start: date = Column(Date)
    date_end: date = Column(Date)
    created_at: datetime = Column(DateTime, default=func.now())
    auto_model: str = Column(String)
    auto_plates: str = Column(String)

class Person(Base):
    __tablename__ = "people"
    
    id: int = Column(Integer, primary_key=True)
    name: int = Column(String, nullable=False)

    pass_id = Column(Integer, ForeignKey("passes.id"))
    pass_obj = relationship("Pass", back_populates="people")


class Vessel(Base):
    __tablename__ = 'vessels'
    id: int = Column(Integer,primary_key=True,autoincrement=True)

class Test(Base):
    __tablename__ = 'test'
    id: int = Column(Integer,primary_key=True,autoincrement=True)

class GenAct(Base):
    __tablename__ = 'gen_act'
    id: int = Column(Integer,primary_key=True,autoincrement=True)

class NotificationAct(Base):
    __tablename__ = 'notification_act'
    id: int = Column(Integer,primary_key=True,autoincrement=True)



class GenAct1(Base):
    __tablename__ = 'gen_act1'
    id: int = Column(Integer,primary_key=True,autoincrement=True)

class NotificationAct1(Base):
    __tablename__ = 'notification_act1'
    id: int = Column(Integer,primary_key=True,autoincrement=True)