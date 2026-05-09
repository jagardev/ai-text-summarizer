import os
from fastapi import APIRouter, HTTPException
from groq import Groq
from schemas import PromptRequest

""" We will use Groq and its model Llama 3 to summarize a given text extracted from Wikipedia.
    The official SDK of Groq is used to accomplish this.
"""

# Router initialization
router = APIRouter()

# Groq client initialization
# It automatically looks for the GROQ_API_KEY variable in the .env file
client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)

# POST endpoint to summarize text using Groq and Llama 3
@router.post("/summarize")
def summarize_text(request: PromptRequest):
    try:
        # Call to the Groq API using the official SDK
        # We use Llama 3 (8B parameters), which is a fast open-source model free on Groq
        chat_completion = client.chat.completions.create(
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
        
        # Return the clean JSON to the frontend
        return {
            "original_text": request.text_input,
            "summary": final_summary
        }
        
    except Exception as e:
        # Error handling to catch any SDK exception
        raise HTTPException(status_code=500, detail=f"Groq AI Error: {str(e)}")