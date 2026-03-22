from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import os


class Settings(BaseSettings):
    # 环境配置
    environment: str = "development"
    debug: bool = True

    # 数据库配置
    database_url: str = "sqlite:///./paper_polish.db"

    # AI服务配置 - 智谱GLM
    zhipuai_api_key: str = ""
    zhipuai_model: str = "glm-4-flash"

    # 认证安全配置
    app_secret_key: str = "change-this-to-a-random-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080  # 7 days

    # CORS 配置 (生产环境必须显式配置)
    cors_origins: str = ""

    # 应用配置
    max_text_length: int = 10000
    batch_size: int = 5
    max_file_size_mb: int = 10

    # LLM 配置
    llm_max_retries: int = 3
    llm_timeout: int = 60
    llm_max_concurrent: int = 3

    class Config:
        env_file = ".env"

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.cors_origins:
            if self.is_production:
                return []
            return ["http://localhost:3000", "http://localhost:5173"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_debug(self) -> bool:
        if self.is_production:
            return False
        return self.debug

    @property
    def safe_config(self) -> dict:
        return {
            "environment": self.environment,
            "debug": self.is_debug,
            "cors_origins": self.cors_origins_list,
            "database_type": self.database_url.split(":")[0],
            "llm_max_retries": self.llm_max_retries,
            "llm_timeout": self.llm_timeout,
            "llm_max_concurrent": self.llm_max_concurrent,
        }


@lru_cache()
def get_settings():
    return Settings()
