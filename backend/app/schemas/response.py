from pydantic import BaseModel
from typing import Optional, Any, List
from datetime import datetime


class BaseResponse(BaseModel):
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Any] = None


class UploadResponse(BaseModel):
    success: bool = True
    message: str = "文件上传成功"
    filename: str
    text: str
    char_count: int


class TokenResponse(BaseModel):
    success: bool = True
    message: str = "登录成功"
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    success: bool = True
    message: str = "操作成功"
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class HistoryItemResponse(BaseModel):
    id: int
    original_text: str
    polished_text: str
    operation_type: str
    style: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class HistoryListResponse(BaseModel):
    success: bool = True
    message: str = "获取成功"
    data: List[HistoryItemResponse] = []


class ProgressResponse(BaseModel):
    task_id: str
    message: str = "任务已创建"
