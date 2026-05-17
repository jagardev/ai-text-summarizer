# AI Text Summarizer API

A high-performance, fully asynchronous backend REST API built with FastAPI that utilizes the Groq inference engine (Llama 3.1 model) to generate text summaries. The project implements professional async/await patterns across all layers, adhering to Clean Architecture principles. It includes robust data persistence using PostgreSQL deployed via Docker containers and comprehensive test coverage with asynchronous Pytest execution using mocked dependencies.

## Technology Stack

- **Framework:** FastAPI (Asynchronous Python)
- **AI Integration:** Async Groq Python SDK (llama-3.1-8b-instant)
- **Database:** PostgreSQL, Async SQLAlchemy (ORM)
- **Testing:** Pytest (with `pytest-asyncio` and `pytest-mock` for professional async testing)
- **Infrastructure:** Docker, Docker Compose
- **Data Validation:** Pydantic

## Prerequisites

Ensure the following dependencies are installed prior to setup:

- [Python 3.10+](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- A valid [Groq API Key](https://console.groq.com/keys)

## Installation and Setup Configuration

1. **Clone the repository:**

```bash
git clone https://github.com/DkayMM/ai_text_summarizer.git
cd ai_text_summarizer
```

2. **Environment Variables Configuration:**
   Create a `.env` file in the root directory and populate it with the required credentials:

```env
GROQ_API_KEY=gsk_your_api_key_here
DB_NAME=ai_text_summarizer
DB_USER=admin
DB_PASSWORD=your_secure_password
DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}
```

3. **Initialize the Database Environment:**

```bash
docker-compose up -d
```

4. **Configure the Virtual Environment and Install Dependencies:**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

_(Note for Windows environments: use `.\venv\Scripts\activate` instead of `venv/bin/activate`)_

5. **Execute the Application Server:**

```bash
uvicorn main:app --reload
```

## API Documentation

Upon initializing the server, the interactive Swagger UI documentation can be accessed via `http://127.0.0.1:8000/docs`.

### Primary Endpoints:

- `POST /ai/summarize`: Processes a text payload, requests a summary from the Groq API, persists the transaction in the database, and returns the generated summary alongside its database ID.
- `GET /ai/history`: Retrieves the 10 most recent summaries stored in the PostgreSQL database, ordered by creation date.

## Testing

The project includes a robust, professional asynchronous testing suite built with `pytest` and `pytest-asyncio`. Testing is isolated and highly reliable, utilizing `pytest-mock` (specifically `AsyncMock` and `patch`) to simulate database interactions and external Groq API calls without requiring live connections.

To execute the test suite:

```bash
pytest tests/
```
