from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    # 数据库配置
    # API_KEY
    QIANWEN_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
