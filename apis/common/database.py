import uuid
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    BigInteger,
    String,
    ForeignKey,
    Boolean,
    TIMESTAMP,
    JSON,DateTime, func
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from common.env import MQSQL_CONNECTION_STRING
# Replace with your actual MySQL database credentials

engine = create_engine(MQSQL_CONNECTION_STRING, echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    number = Column(String(20), nullable=False)
    country = Column(Integer, nullable=False)
    address = Column(Integer, nullable=False)


class Organizer(Base):
    __tablename__ = "organizers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)


class EventType(Base):
    __tablename__ = "event_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String(255), nullable=False)


class BookingHistory(Base):
    __tablename__ = "booking_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    attended = Column(Boolean, default=False)

# Create all tables
# Base.metadata.create_all(engine)
