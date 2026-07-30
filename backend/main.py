from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from rate_limiter import limiter

# Load dotenv config before loading our custom modules
load_dotenv()

# Load our AI module
from routers import ai_tasks

# Import tools to build our database
import models
from database import engine

# Command SQLAlchemy to create the tables in the database if they don't exist
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

# API Initialization with metadata for Swagger UI
app = FastAPI(
    lifespan=lifespan,
    title="AI Text Summarizer API",
    description="A robust backend REST API leveraging Groq's Llama 3.1 for text summarization.",
    version="1.0.0"
)

# Limiter initialize
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Define CORS headers permissions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Including the routers
app.include_router(ai_tasks.router, prefix="/ai", tags=["Artificial Intelligence"])

# Health check endpoint
@app.get("/", tags=["System"])
def health_check():
    """
    Root endpoint to verify the API is up and running.
    """
    return {
        "status": "online",
        "message": "AI Text Summarizer API is fully operational."
    }





