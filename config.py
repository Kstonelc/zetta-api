from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    # 数据库配置
    # API_KEY
    QIANWEN_API_KEY: str
    # 向量数据库
    VECTOR_DB_HOST: str
    VECTOR_DB_PORT: int

    class Config:
        env_file = ".env"


settings = Settings()
