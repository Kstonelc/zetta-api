from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings

engine = create_engine(settings.DB_URL, echo=False)
session = sessionmaker(bind=engine)


Base = declarative_base()


# Fastapi 依赖 注入DB会话
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()
