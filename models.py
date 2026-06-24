from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from database import Base
from datetime import datetime

class UserData(Base):
    __tablename__ = "userdata"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class StressData(Base):
    __tablename__ = "stress_data"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("userdata.id"))

    sleep = Column(Float)
    work = Column(Float)
    mood = Column(Float)
    screen = Column(Float)
    activity = Column(Float)
    heart = Column(Float)
    spo2 = Column(Float)

    timestamp = Column(DateTime, default=datetime.utcnow)
    prediction = Column(String)