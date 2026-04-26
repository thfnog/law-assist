# LawAssist AI - MVP

Vertical AI Assistant for Law Firms to automate administrative workflows.

## Features
- **Client Onboarding**: Automatically creates Trello card, Google Drive folder, and generates a contract from a template.
- **Search**: Find client information in the database and Trello cards.
- **WhatsApp Integration**: Responds to messages via Evolution API.

## Tech Stack
- **Backend**: FastAPI + LangGraph + SQLModel
- **Database**: PostgreSQL
- **LLM**: OpenAI GPT-4o-mini
- **Integrations**: Trello, Google Drive, Google Docs, Evolution API (WhatsApp)

## Setup Instructions

### 1. External Requirements
- **Trello**: Get API key and token from [Trello Power-Up Admin](https://trello.com/power-ups/admin).
- **Google Cloud**:
  - Create a project.
  - Enable Drive and Docs APIs.
  - Create a **Service Account** and download the JSON key. Save it as `backend/service-account.json`.
- **Evolution API**: Ensure you have an instance running and obtained the API Key.

### 2. Environment Variables
Copy `.env.example` to `.env` and fill in the values:
```bash
cp backend/.env.example backend/.env
```

### 3. Running with Docker
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.
The Frontend can be opened by double-clicking `frontend/index.html`.

## API Endpoints
- `POST /chat`: Simple chat interface `{ "message": "..." }`
- `POST /webhook/whatsapp`: Webhook for Evolution API events.
- `GET /health`: Health check.

## Project Structure
```text
/backend
  /app
    /api           # FastAPI routes
    /core          # Configuration
    /graph         # LangGraph orchestration
    /playbooks     # Specialized agent logic
    /tools         # Integration wrappers
    /models        # DB Schema
  main.py          # Entry point
/frontend          # Chat UI
```
