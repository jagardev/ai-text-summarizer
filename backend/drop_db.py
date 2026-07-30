import asyncio
from database import engine
from models import Base

async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("Dropped tables successfully")

if __name__ == "__main__":
    asyncio.run(drop_tables())
