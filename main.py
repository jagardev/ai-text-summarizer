from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from random import *
import requests
from schemas import PromptRequest

# Load dotenv config before loading our custom modules
load_dotenv()

# Load our AI module
from routers import ai_tasks

# API Initialization
app = FastAPI()

# Including the routers
app.include_router(ai_tasks.router, prefix="/ai", tags=["Artificial Intelligence"])

# Creation of an endpoint
@app.get("/")
def read_root():
    return {"message": "testing fastapi"}

# Endpoint to roll a dice with random number
@app.get("/dice")
def roll_dice():
    dice_number = randint(1, 6)
    return {"message": f"You rolled the number {dice_number}"}

# Dynamic endpoint with user input and type hinting
@app.get("/dice/{sides}")
def dynamic_roll_dice(sides: int):
    dice_number = randint(1, sides)
    return {"message": f"Your dice has {sides} sides and you rolled the number {dice_number}"}

# POST endpoint using a Model with Pydantic. GET request to external API and parse data to JSON.
@app.post("/analyze")
def analyze_text(request: PromptRequest):
    request_text = request.text_input
    response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{request_text}")
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Sorry, we couldn't find that word.")
    data = response.json()
    first_definition = data[0]["meanings"][0]["definitions"][0]["definition"]
    return {"Your word:": request_text, "Definition:": first_definition}






