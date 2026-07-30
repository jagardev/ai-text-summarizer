# SummarAIzer: AI Text Summarizer

A high-performance, full-stack web application designed for professional text summarization. It combines a stunning modern frontend built with **Astro & Tailwind CSS** and an asynchronous REST API backend powered by **FastAPI** and the **Groq inference engine (Llama 3.1)**. 

The project features persistent, continuous chat sessions with **User Isolation**, ensuring each browser maintains its own private history independently.

## Technology Stack

### Frontend (`/frontend`)
- **Framework:** Astro
- **Styling:** Tailwind CSS (Custom Dark Mode & Premium UI/UX aesthetics)
- **State Management:** Native DOM Manipulation & `localStorage` for User Isolation
- **Typography:** Space Grotesk & Montserrat via Google Fonts

### Backend (`/backend`)
- **Framework:** FastAPI (Asynchronous Python)
- **AI Integration:** Async Groq Python SDK (llama-3.1-8b-instant)
- **Database:** PostgreSQL, Async SQLAlchemy (ORM)
- **Testing:** Pytest (with `pytest-asyncio` and `pytest-mock` for professional async testing)
- **Data Validation:** Pydantic

## Key Features
- **Continuous Chat Sessions:** Append messages continuously in the same view rather than overwriting past questions.
- **User Isolation:** The frontend generates a unique `user_id` stored in `localStorage`, meaning every recruiter/user visiting the app will have a private, independent history stream.
- **Shift+Enter Support:** Multi-line text inputs that auto-expand, allowing for complex prompt formatting.

## Prerequisites

Ensure the following dependencies are installed prior to setup:
- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Optional for DB)
- A valid [Groq API Key](https://console.groq.com/keys)

## Installation and Local Setup

1. **Clone the repository:**
```bash
git clone https://github.com/jagardev/ai-text-summarizer.git
cd ai-text-summarizer
```

### Backend Setup
1. **Configure Environment:**
Navigate to the `backend` directory and create a `.env` file:
```env
GROQ_API_KEY=gsk_your_api_key_here
DB_NAME=ai_text_summarizer
DB_USER=admin
DB_PASSWORD=your_secure_password
DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}
```

2. **Initialize Database (Docker):**
```bash
cd backend
docker-compose up -d
```

3. **Install Dependencies and Run:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
*(Windows: `.\venv\Scripts\activate`)*
The API will be available at `http://127.0.0.1:8000`.

### Frontend Setup
1. **Install Dependencies:**
Open a new terminal and navigate to the `frontend` directory:
```bash
cd frontend
npm install
```

2. **Run Development Server:**
```bash
npm run dev
```
The UI will be accessible at `http://localhost:4321`.

## API Endpoints

- `POST /ai/summarize`: Expects `text_input`, `session_id`, and `user_id`. Queries Groq, persists the data, and returns the summary.
- `GET /ai/history?limit=15&user_id={id}`: Fetches all summaries for the specified `user_id` and groups them intelligently by `session_id` to reconstruct chat threads.

## Testing (Backend)
To execute the asynchronous, isolated Pytest suite:
```bash
cd backend
pytest tests/
```
