from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "sqlite:///./paper_polish.db"

    # AI服务配置 - 智谱GLM
    zhipuai_api_key: str = ""
    zhipuai_model: str = "glm-4-flash"

    # 应用配置
    max_text_length: int = 10000
    batch_size: int = 5

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
