from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), index=True)
    original_content = Column(Text, nullable=False)
    polished_content = Column(Text)
    anti_ai_content = Column(Text)
    polish_style = Column(String(50))  # academic, natural, formal
    naturalness_score = Column(Float, default=0.0)
    ai_detection_risk = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    history = relationship("app.models.paper.PolishHistory", back_populates="paper")


class PolishHistory(Base):
    __tablename__ = "polish_history"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), index=True)
    version = Column(Integer, default=1)
    content = Column(Text, nullable=False)
    operation_type = Column(String(50))  # polish, anti_ai
    changes_summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    paper = relationship("Paper", back_populates="history")
