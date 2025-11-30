# Chatlingo AI - WhatsApp Kannada Learning Bot

A WhatsApp chatbot that teaches spoken Kannada written in English.

## Tech Stack

- **Backend:** Python FastAPI
- **Database:** Supabase (PostgreSQL)
- **LLM:** OpenAI GPT-4o-mini
- **Messaging:** WhatsApp Cloud API
- **Hosting:** Render

## Project Structure

```
chatlingo-ai/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI app entry point
│   ├── config.py             # Configuration management
│   ├── routers/              # API endpoints (to be added)
│   ├── services/             # Business logic (to be added)
│   └── utils/                # Helper functions (to be added)
├── .env                      # Environment variables (create from .env.example)
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- OpenAI API key
- WhatsApp Cloud API credentials
- Supabase account

### 2. Clone & Install

```bash
# Clone the repository
git clone <repository-url>
cd chatlingo-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate


# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and fill in your credentials
# - OPENAI_API_KEY
# - WHATSAPP_ACCESS_TOKEN
# - WHATSAPP_PHONE_ID
# - WHATSAPP_VERIFY_TOKEN
# - SUPABASE_URL
# - SUPABASE_KEY
```

### 4. Run the Application

```bash
# Run with uvicorn
python -m app.main

# Or use uvicorn directly
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 5. Verify Installation

Visit `http://localhost:8000/health` to check if the server is running.
