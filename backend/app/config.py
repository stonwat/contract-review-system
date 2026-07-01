"""应用配置：从环境变量读取。"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置。所有值从环境变量读取，.env 文件作为后备。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 应用
    app_env: str = "dev"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # 数据库
    database_url: str = "postgresql+asyncpg://app:apppassword@localhost:5432/contract_review"

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "contract-files"
    minio_secure: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # 认证
    jwt_secret: str = "change-me-to-a-random-secret-key"
    jwt_expire_hours: int = 24
    agent_api_key: str = "change-me-to-a-random-agent-api-key"

    # LLM
    llm_base_url: str = "https://api.example.com/v1"
    llm_api_key: str = "your-llm-api-key"
    llm_model: str = "qwen2.5-72b"

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """单例配置，避免重复解析环境变量。"""
    return Settings()


settings = get_settings()
