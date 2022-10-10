from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, poolclass=NullPool )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
