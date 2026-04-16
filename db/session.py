from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from core.config import settings

Base = declarative_base()
database_url = settings.DATABASE_URL

engine = create_engine(url=database_url)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()