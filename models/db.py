from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

engine = create_engine(settings.DB_URL, pool_pre_ping=True, echo=False)
session = sessionmaker(bind=engine)


# Fastapi 依赖 注入DB会话
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()
