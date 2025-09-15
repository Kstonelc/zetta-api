from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    BASE_URL: str
    # 数据库配置
    # API_KEY
    QIANWEN_API_KEY: str
    # 向量数据库
    VECTOR_DB_HOST: str
    VECTOR_DB_PORT: int
    # 数据库
    DB_URL: str

    # 邮箱
    MAIL_USERNAME:  str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str

    class Config:
        env_file = ".env"


settings = Settings()
