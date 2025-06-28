# ChatLingo AI - Application Overview

This is a **WhatsApp-based language learning bot** that helps Malayalam speakers learn **spoken Kannada** through interactive, scenario-based conversations.

## Core Functionality

**30-Day Learning Journey:**
- Each day focuses on a specific real-life scenario (from `scenarios.json`)
- Scenarios include: "Self Introduction", "Grocery Shopping", "At a Restaurant", etc.
- Progressive difficulty building from simple phrases to full conversations

**Smart Conversation Flow:**
- Users can type "start" to begin Day 1
- Users can type "day X" to jump to any specific day (1-30)
- The AI maintains context and builds on previous conversations
- Responses include:
  - Kannada phrase (in Latin script)
  - English translation
  - Malayalam word-by-word meaning
  - Suggested reply prompts

**Dual Interface:**
- **WhatsApp**: Primary interface via Twilio webhook (`/webhook`)
- **Web Chat**: Testing interface at root URL (`/`)

## Architecture

**Backend (Flask + PostgreSQL):**
- **`app.py`**: Main Flask application with webhook and API endpoints
- **`models.py`**: Database models for chat history and user progress tracking
- **PostgreSQL**: Stores chat history and user day progression

**AI Integration:**
- **Google Gemini AI**: Powers the conversational responses
- **Twilio**: Handles WhatsApp integration

**Frontend:**
- **`static/index.html`**: Web interface for testing the bot
- **`static/script.js`**: Frontend JavaScript for chat functionality

## Database Schema

**`last_day_number` table:**
- `phone` (hashed): User identifier
- `day_number`: Current day in the 30-day program

**`chat_history` table:**
- `id`: Auto-incrementing primary key
- `phone` (hashed): User identifier
- `message`: Chat message content
- `role`: 'user' or 'model'
- `timestamp`: Message timestamp

## API Endpoints

1. **`POST /webhook`**: Twilio WhatsApp webhook
2. **`POST /api/chat`**: Web chat interface
3. **`POST /api/reset`**: Reset chat history
4. **`GET /`**: Serve web interface

## AI Prompt Strategy

The system uses a sophisticated prompt template that:
- Positions the AI as a friendly Kannada tutor
- Provides context about the current day's scenario
- Instructs the AI to respond in a WhatsApp-style, conversational manner
- Includes translation guidance and reply suggestions
- Maintains a supportive, encouraging tone

## Security Features

- Phone numbers are hashed before database storage
- Environment variables for sensitive API keys
- Session-based chat history management

## Deployment Ready

The app is configured for deployment on Render with:
- **`Procfile`**: Gunicorn WSGI server configuration
- **`render.yaml`**: Render deployment configuration
- **`runtime.txt`**: Python version specification
- **`requirements.txt`**: All dependencies listed 