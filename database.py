import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Get the Postgres URL from the .env file
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")

# Create the engine (connects to PostgreSQL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for future tables
Base = declarative_base()

# Dependency generator (to use with routers)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()