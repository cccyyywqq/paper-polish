from abc import ABC, abstractmethod
from typing import List
from zhipuai import ZhipuAI
from ..config import get_settings

settings = get_settings()


class AIService(ABC):
    @abstractmethod
    async def polish_text(self, text: str, style: str = "academic") -> str:
        pass

    @abstractmethod
    async def anti_ai_detection(self, text: str) -> str:
        pass

    @abstractmethod
    async def get_suggestions(self, text: str) -> List[str]:
        pass


class ZhipuAIService(AIService):
    def __init__(self):
        self.client = ZhipuAI(api_key=settings.zhipuai_api_key)
        self.model = settings.zhipuai_model

    async def polish_text(self, text: str, style: str = "academic") -> str:
        prompts = {
            "academic": "你是一位专业的学术论文编辑。请将以下文本润色为严谨的学术论文风格，保持原意但提升表达质量和专业性：",
            "natural": "你是一位优秀的写作助手。请将以下文本润色得更自然流畅，增加可读性，同时保持学术性：",
            "formal": "你是一位学术写作专家。请将以下文本润色为正式的学术风格，使用专业术语和规范表达：",
        }

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompts.get(style, prompts["academic"])},
                {"role": "user", "content": text},
            ],
            temperature=0.7,
            max_tokens=4000,
        )
        return response.choices[0].message.content

    async def anti_ai_detection(self, text: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """你是一位学术写作专家。请将以下文本改写，使其：
1. 不被AI检测工具识别为AI生成
2. 保持学术性和准确性
3. 增加个人表达和独特视角
4. 调整句式结构，避免AI常见模式
5. 适当使用同义词替换和句式变换
6. 增加适当的过渡词和个人见解
7. 使用多样化的句式开头
8. 保持逻辑连贯性和专业性""",
                },
                {"role": "user", "content": text},
            ],
            temperature=0.8,
            max_tokens=4000,
        )
        return response.choices[0].message.content

    async def get_suggestions(self, text: str) -> List[str]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """请分析以下学术文本，提供3-5条具体的改进建议，每条建议不超过50字。请以列表形式返回，每行一条建议：""",
                },
                {"role": "user", "content": text},
            ],
            temperature=0.5,
            max_tokens=1000,
        )
        content = response.choices[0].message.content
        suggestions = [s.strip() for s in content.split("\n") if s.strip()]
        return suggestions[:5]


class LocalModelService(AIService):
    def __init__(self):
        self.available = False

    async def polish_text(self, text: str, style: str = "academic") -> str:
        if not self.available:
            return text
        return text

    async def anti_ai_detection(self, text: str) -> str:
        if not self.available:
            return text
        return text

    async def get_suggestions(self, text: str) -> List[str]:
        return ["本地模型暂未配置"]


class AIServiceFactory:
    @staticmethod
    def create_service(provider: str = "zhipuai") -> AIService:
        if provider == "zhipuai":
            return ZhipuAIService()
        elif provider == "local":
            return LocalModelService()
        else:
            raise ValueError(f"不支持的AI服务: {provider}")
