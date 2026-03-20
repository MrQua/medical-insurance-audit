"""应用配置"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类"""

    # ========== Database ==========
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/medical_audit"

    # ========== DeepSeek API ==========
    deepseek_api_key: str = ""  # DeepSeek API Key
    deepseek_base_url: str = "https://api.deepseek.com"  # DeepSeek API 地址
    deepseek_model: str = "deepseek-chat"  # 模型名称

    # ========== App ==========
    upload_dir: str = "uploads"
    max_file_size: str = "50MB"

    # ========== Logging ==========
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
