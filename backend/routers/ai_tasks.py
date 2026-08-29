import os
from fastapi import APIRouter, HTTPException, Depends, Request
from rate_limiter import limiter
from groq import AsyncGroq
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

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
@limiter.limit("5/minute") # 5 prompts per minute at max
async def summarize_text(request: Request, payload: PromptRequest, db: AsyncSession = Depends(get_db)) -> dict:
    """
    Insert a long text (max. 10.000 characters) to get a summarized version.
    """
    try:
        # Call to the Groq API using the official SDK
        # We use Llama 3 (8B parameters), which is a fast open-source model free on Groq
        try:
            chat_completion = await client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional assistant. Your task is to summarize the text provided by the user in a concise and clear manner.",
                    },
                    {
                        "role": "user",
                        "content": f"Summarize this text: {payload.text_input}",
                    }
                ],
                model="llama-3.3-70b-versatile",
            )
        except Exception as e:
            # Fallback model in case of failure
            print(f"Primary model failed ({e}), trying fallback model...")
            chat_completion = await client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional assistant. Your task is to summarize the text provided by the user in a concise and clear manner.",
                    },
                    {
                        "role": "user",
                        "content": f"Summarize this text: {payload.text_input}",
                    }
                ],
                model="llama-3.1-8b-instant",
            )
        
        # Extract the text response from the Groq object
        final_summary = chat_completion.choices[0].message.content
        
        # Create a new instance using our object Summary
        new_summary = models.Summary(
            user_id=payload.user_id,
            session_id=payload.session_id,
            original_text=payload.text_input,
            summary_text=final_summary
        )
        
        # Add the new instance to the session and commit it
        db.add(new_summary)
        await db.commit()
        await db.refresh(new_summary) #Refresh to obtain the generated ID
        
        # Return the clean JSON to the frontend
        return {
            "id": new_summary.id,
            "session_id": new_summary.session_id,
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
@limiter.limit("60/minute") # Increased limit to allow frequent page refreshes
async def get_summary_history(request: Request, user_id: str, db: AsyncSession = Depends(get_db), limit: int = 10) -> list:
    """
    Obtain a history of texts that have been summarized.
    """
    try:
        # Query to our database using SQLAlchemy.
        # We ask for every summary of the user, ordered by oldest to newest to reconstruct the chat properly.
        result = await db.execute(
            select(models.Summary).where(models.Summary.user_id == user_id).order_by(models.Summary.created_at.asc())
        )
        history = result.scalars().all()
        
        # Group by session_id
        sessions = {}
        for item in history:
            if item.session_id not in sessions:
                sessions[item.session_id] = []
            sessions[item.session_id].append({
                "id": item.id,
                "original_text": item.original_text,
                "summary_text": item.summary_text,
                "created_at": item.created_at
            })
        
        # Convert the dictionary to a list, ordered by the latest created_at of their last message
        formatted_history = []
        for session_id, messages in sessions.items():
            formatted_history.append({
                "session_id": session_id,
                "messages": messages
            })
            
        # Sort sessions by the created_at of their latest message descending, and limit to `limit`
        formatted_history.sort(key=lambda x: x["messages"][-1]["created_at"], reverse=True)
        formatted_history = formatted_history[:limit]
        
        return formatted_history
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# DELETE Endpoint to remove a specific chat session from the database
@router.delete("/history/{session_id}")
@limiter.limit("20/minute")
async def delete_summary_history(request: Request, session_id: str, user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Delete a specific chat session and all its summaries from history.
    """
    try:
        # Delete from DB
        result = await db.execute(
            delete(models.Summary).where(
                (models.Summary.session_id == session_id) & (models.Summary.user_id == user_id)
            )
        )
        await db.commit()
        return {"status": "success", "message": "Chat deleted successfully", "deleted_rows": result.rowcount}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")