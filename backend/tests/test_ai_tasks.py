import pytest
import pytest_asyncio
import datetime
from httpx import AsyncClient, ASGITransport

from main import app
from database import get_db

# Mark all tests in this module as asynchronous
pytestmark = pytest.mark.asyncio

# Use pytest_asyncio instead of standard pytest for async fixtures
@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

# Dummy object accessible with .method notation
class DummySummary:
    """Simple DTO to bypass SQLAlchemy model requirements in tests."""
    def __init__(self, id, original_text, summary_text, created_at):
        self.id = id
        self.original_text = original_text
        self.summary_text = summary_text
        self.created_at = created_at
        
class MockGroqResponse:
    """Simulates the nested object structure returned by the Groq SDK."""
    def __init__(self, content):
        self.message = type('obj', (object,), {'content': content})
        self.choices = [type('obj', (object,), {'message': self.message})]

# /history TEST
async def test_get_summary_history(async_client, mocker):
    
    # Mock data setup
    fake_date = datetime.datetime.now(datetime.timezone.utc)
    mock_data = [
        DummySummary(1, "Text 1", "Summary 1", fake_date),
        DummySummary(2, "Text 2", "Summary 2", fake_date)
    ]

    # Build the SQLAlchemy method chain: execute() -> scalars() -> all()
    mock_session = mocker.AsyncMock()
    mock_result = mocker.MagicMock()
    mock_scalars = mocker.MagicMock()

    mock_scalars.all.return_value = mock_data
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    # Override DB dependency
    def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db

    # Execution
    response = await async_client.get("/ai/history")

    # Assertions
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert data[0]["summary_text"] == "Summary 1"

    # Cleanup
    app.dependency_overrides.clear()

# /summarize TEST
async def test_post_summarize(async_client, mocker):
    

    # Mock the Groq API SDK (Monkey Patching)
    # We intercept the exact path where the Groq client is executed in the router
    mock_groq = mocker.patch("routers.ai_tasks.client.chat.completions.create")
    mock_groq.return_value = MockGroqResponse("This is a mocked AI summary generated instantly without network.")


    # Mock the Database Write Operations
    mock_session = mocker.AsyncMock()

    # The db.refresh() method modifies the object in place to add the generated ID
    # We use a side_effect to simulate this behavior automatically
    async def mock_refresh(instance):
        instance.id = 99
        
    mock_session.refresh.side_effect = mock_refresh

    def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db

    # Execution
    # We MUST send more than 10 characters to pass our Pydantic schema
    payload = {
        "text_input": "This text is long enough to bypass the Pydantic minimum length validation."
    }
    
    response = await async_client.post("/ai/summarize", json=payload)

    # Assertions
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == 99
    assert data["summary"] == "This is a mocked AI summary generated instantly without network."
    
    # Verify that the router actually attempted to call Groq and save to DB
    mock_groq.assert_called_once()
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

    # Cleanup
    app.dependency_overrides.clear()

# Rate limiting test
async def test_rate_limiter_blocks_abuse(async_client):
    """
    Test that making more than 5 requests in a minute triggers a 429 error.
    """
    for _ in range(6):
        response = await async_client.get("/ai/history")
    
    # Assert that the 6th request is blocked
    assert response.status_code == 429