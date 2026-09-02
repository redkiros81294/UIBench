"""
Backend configuration via environment variables.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseModel):
    url: str = Field(default="mongodb://localhost:27017/uibench", description="MongoDB connection URI")
    db_name: str = Field(default="uibench", description="Database name")


class SecuritySettings(BaseModel):
    secret_key: str = Field(default="change-me-in-production", description="JWT signing secret")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token TTL")


class CORSSettings(BaseModel):
    allow_origins: List[str] = Field(default_factory=lambda: ["*"], description="Allowed CORS origins")
    allow_methods: List[str] = Field(default_factory=lambda: ["*"], description="Allowed HTTP methods")
    allow_headers: List[str] = Field(default_factory=lambda: ["*"], description="Allowed HTTP headers")
    allow_credentials: bool = Field(default=False, description="Allow credentials in CORS")


class Settings(BaseSettings):
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    cors: CORSSettings = Field(default_factory=CORSSettings)
    api_prefix: str = Field(default="/api", description="Global API prefix")

    model_config = {"env_nested_delimiter": "__", "env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
