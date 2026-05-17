import os
from fastapi import APIRouter, HTTPException, Depends
from groq import AsyncGroq
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from schemas import PromptRequest
from database import get_db
import models

""" We will use Groq and its model Llama 3 to summarize a given text extracted from Wikipedia.
    The official SDK of Groq is used to accomplish this.
"""

# Router initialization
router = APIRouter()

# Groq client initialization
# It automatically looks for the GROQ_API_KEY variable in the .env file
client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

# POST endpoint to summarize text using Groq and Llama 3
@router.post("/summarize")
async def summarize_text(request: PromptRequest, db: AsyncSession = Depends(get_db)) -> dict:
    """
    Insert a long text (max. 5000 characters) to get a summarized version.
    """
    try:
        # Call to the Groq API using the official SDK
        # We use Llama 3 (8B parameters), which is a fast open-source model free on Groq
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional assistant. Your task is to summarize the text provided by the user in a concise and clear manner.",
                },
                {
                    "role": "user",
                    "content": f"Summarize this text: {request.text_input}",
                }
            ],
            model="llama-3.1-8b-instant",
        )
        
        # Extract the text response from the Groq object
        final_summary = chat_completion.choices[0].message.content
        
        # Create a new instance using our object Summary
        new_summary = models.Summary(
            original_text=request.text_input,
            summary_text=final_summary
        )
        
        # Add the new instance to the session and commit it
        db.add(new_summary)
        await db.commit()
        await db.refresh(new_summary) #Refresh to obtain the generated ID
        
        # Return the clean JSON to the frontend
        return {
            "id": new_summary.id,
            "original_text": new_summary.original_text,
            "summary": new_summary.summary_text
        }
        
    except Exception as e:
        # Rollback in case the db fails, so we do not let any transactions half way
        await db.rollback()
        # Error handling to catch any SDK exception
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# GET Endpoint to make a query using SQLAlchemy, retrieving our history of summaries stored in our db
@router.get("/history")
async def get_summary_history(db: AsyncSession = Depends(get_db), limit: int = 10) -> list:
    """
    Obtain a history of texts that have been summarized.
    """
    try:
        # Query to our database using SQLAlchemy.
        # We ask for every summary, ordered by latest to oldest, limiting to 10 results maximum.
        result = await db.execute(
            select(models.Summary).order_by(models.Summary.created_at.desc()).limit(limit)
        )
        history = result.scalars().all()
        
        # Convert the objects to dictionaries
        formatted_history = []
        for item in history:
            formatted_history.append({
                "id": item.id,
                "original_text": item.original_text,
                "summary_text": item.summary_text,
                "created_at": item.created_at
            })
        
        return formatted_history
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")