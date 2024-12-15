from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "123456"
    DB_NAME: str = "stockdb"
    DATABASE_URL: str = ""

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    CACHE_EXPIRE: int = 3600  # 缓存过期时间（秒）

    # 日志配置
    LOG_LEVEL: str = "DEBUG"

    class Config:
        env_file = ".env"
        extra = "allow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 如果没有直接设置 DATABASE_URL，则从其他配置构建
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )

settings = Settings() 