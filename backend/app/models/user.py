from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    history = relationship("UserPolishHistory", back_populates="user")


class UserPolishHistory(Base):
    __tablename__ = "user_polish_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    original_text = Column(Text, nullable=False)
    polished_text = Column(Text)
    operation_type = Column(String(50))
    style = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="history")
