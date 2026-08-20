from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Float,  DateTime, Boolean
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    password = Column(String)
    last_read_date = Column(DateTime, nullable=True)
    reading_streak = Column(Integer, default=0)
    avg_reading_speed = Column(Float, nullable=True)
    tbr_list = relationship("TbrBook", cascade="all, delete-orphan")

class Book(Base):
    __tablename__ = "all_books"

    book_id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    cover_id = Column(Integer)
    total_pages = Column(Integer)
    avg_rating = Column(Float)

class TbrBook(Base):
    __tablename__ = "tbr_books"

    tbr_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    book_id = Column(Integer, ForeignKey("all_books.book_id"))

    session_started_at = Column(Float, default=None)
    session_ended_at = Column(Float, default=None)
    current_page = Column(Integer, default=0)
    pages_per_min = Column(Float, default=0)
    status = Column(String, default="TBR")
    user_rating = Column(Float, nullable=True)
    last_read = Column(DateTime, nullable=True)
    progress = Column(Integer, nullable=True)
    favourite = Column(Boolean, default=False)