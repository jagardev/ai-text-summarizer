# AI Text Summarizer API

A backend REST API built with FastAPI that utilizes the high-performance Groq inference engine (Llama 3.1 model) to generate text summaries. The project implements Clean Architecture principles and includes data persistence using PostgreSQL deployed via Docker containers.

## Technology Stack

*   **Framework:** FastAPI (Python)
*   **AI Integration:** Groq Python SDK (llama-3.1-8b-instant)
*   **Database:** PostgreSQL, SQLAlchemy (ORM)
*   **Infrastructure:** Docker, Docker Compose
*   **Data Validation:** Pydantic

## Prerequisites

Ensure the following dependencies are installed prior to setup:
*   [Python 3.10+](https://www.python.org/downloads/)
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/)
*   A valid [Groq API Key](https://console.groq.com/keys)

## Installation and Setup Configuration

1. **Clone the repository:**
```bash
git clone [https://github.com/DkayMM/AI-Wrapper](https://github.com/DkayMM/AI-Wrapper)
cd AI-Wrapper
```

2. **Environment Variables Configuration:**
Create a `.env` file in the root directory and populate it with the required credentials:
```env
GROQ_API_KEY=gsk_your_api_key_here
DB_NAME=AI_WRAPPER_TEST
DB_USER=admin
DB_PASSWORD=your_secure_password
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}
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
*(Note for Windows environments: use `.\venv\Scripts\activate` instead of `venv/bin/activate`)*

5. **Execute the Application Server:**
```bash
uvicorn main:app --reload
```

## API Documentation

Upon initializing the server, the interactive Swagger UI documentation can be accessed via `http://127.0.0.1:8000/docs`.

### Primary Endpoints:

*   `POST /ai/summarize`: Processes a text payload, requests a summary from the Groq API, persists the transaction in the database, and returns the generated summary alongside its database ID.
*   `GET /ai/history`: Retrieves the 10 most recent summaries stored in the PostgreSQL database, ordered by creation date.