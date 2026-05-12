from dotenv import load_dotenv
from fastapi import FastAPI

# Load dotenv config before loading our custom modules
load_dotenv()

# Load our AI module
from routers import ai_tasks

# Import tools to build our database
import models
from database import engine

# API Initialization with metadata for Swagger UI
app = FastAPI(
    title="AI Text Summarizer API",
    description="A robust backend REST API leveraging Groq's Llama 3.1 for text summarization.",
    version="1.0.0"
)

# Command SQLAlchemy to create the tables in the database if they don't exist
models.Base.metadata.create_all(bind=engine)

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





