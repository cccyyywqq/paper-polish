from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class HistoryCreate(BaseModel):
    original_text: str
    polished_text: str
    operation_type: str
    style: Optional[str] = None


class HistoryResponse(BaseModel):
    id: int
    original_text: str
    polished_text: str
    operation_type: str
    style: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
