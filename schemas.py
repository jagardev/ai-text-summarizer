from pydantic import BaseModel

# Model for POST requests
class PromptRequest(BaseModel):
    text_input: str
    max_words: int