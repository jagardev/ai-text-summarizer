import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Get the Postgres URL from the .env file
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")

# Create the async engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

# Create an async Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Create a Base class for future tables
Base = declarative_base()

# Dependency generator (to use with routers)
async def get_db():
    async with SessionLocal() as db:
        yield db
