from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PolishRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000, description="需要润色的文本")
    style: str = Field(default="academic", description="润色风格: academic, natural, formal")
    ai_provider: str = Field(default="zhipuai", description="AI服务提供商: zhipuai, local")


class PolishResponse(BaseModel):
    original: str
    polished: str
    grammar_corrected: Optional[str] = None
    suggestions: List[str] = []
    success: bool = True
    message: str = "润色完成"


class AntiAIRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000, description="需要去AI化的文本")
    ai_provider: str = Field(default="zhipuai", description="AI服务提供商: zhipuai, local")


class AntiAIResponse(BaseModel):
    original: str
    processed: str
    naturalness_score: float = 0.0
    ai_detection_risk: float = 0.0
    suggestions: List[str] = []
    success: bool = True
    message: str = "去AI化处理完成"


class BatchPolishRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1, description="需要批量润色的文本列表")
    style: str = Field(default="academic", description="润色风格: academic, natural, formal")
    ai_provider: str = Field(default="zhipuai", description="AI服务提供商: zhipuai, local")


class BatchPolishResponse(BaseModel):
    results: List[str] = []
    success: bool = True
    message: str = "批量润色完成"


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000, description="需要分析的文本")


class AnalyzeResponse(BaseModel):
    ai_detection_risk: float
    naturalness_score: float
    risk_level: str


class PaperCreate(BaseModel):
    title: Optional[str] = None
    original_content: str


class PaperResponse(BaseModel):
    id: int
    title: Optional[str]
    original_content: str
    polished_content: Optional[str]
    anti_ai_content: Optional[str]
    naturalness_score: float
    ai_detection_risk: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
