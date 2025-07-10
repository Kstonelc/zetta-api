from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings
from utils.logger import logger

DATABASE_URL = settings.DB_URL

engine = create_engine(DATABASE_URL, echo=False)
session = sessionmaker(bind=engine)


Base = declarative_base()


def check_db_connection():
    engine.connect()
