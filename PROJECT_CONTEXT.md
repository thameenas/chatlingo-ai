# Chatlingo AI - Complete Project Context

> **Purpose**: This document provides comprehensive context for any LLM or developer to understand the entire Chatlingo AI project before making changes or additions.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Environment Configuration](#environment-configuration)
5. [Database Schema](#database-schema)
6. [Application Architecture](#application-architecture)
7. [Core Services](#core-services)
8. [API Endpoints](#api-endpoints)
9. [Data Models (Pydantic Schemas)](#data-models-pydantic-schemas)
10. [LLM Prompts](#llm-prompts)
11. [User Flow & State Machine](#user-flow--state-machine)
12. [Key Features](#key-features)
13. [Dependencies](#dependencies)
14. [Setup & Deployment](#setup--deployment)

---

## Project Overview

**Chatlingo AI** is a WhatsApp chatbot designed to teach spoken Bangalore Kannada (Kanglish) to English speakers through conversational learning. The bot uses LLM-powered natural language understanding to:

- Teach Kannada written in English script ("Kanglish")
- Provide roleplay practice scenarios based on real Bangalore situations
- Offer casual conversation practice for language learning
- Give gentle corrections and suggested replies to keep users engaged

### Core Concept
The bot writes Kannada using English letters (not Kannada script), making it accessible to learners who don't know the script. It uses casual, street-level Bangalore Kannada with common slang like "maadi", "bidi", "guru", "sakkath", "machha".

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend Framework** | Python FastAPI |
| **Database** | Supabase (PostgreSQL) |
| **LLM Provider** | OpenAI GPT-4o-mini (primary) or OpenRouter (alternative) |
| **Messaging Platform** | WhatsApp Cloud API |
| **HTTP Client** | httpx (async) |
| **Data Validation** | Pydantic v2 |
| **Server** | Uvicorn |
| **Hosting** | Render (recommended) |

---

## Project Structure

```
chatlingo-ai/
├── app/
│   ├── __init__.py              # Package init, version: 0.1.0
│   ├── config.py                # Pydantic Settings configuration
│   ├── main.py                  # FastAPI app entry point
│   ├── prompts/
│   │   ├── base_system.txt      # System prompt for general chat mode
│   │   └── practice_scenarios_system.txt  # System prompt for roleplay scenarios
│   ├── routers/
│   │   └── webhook.py           # WhatsApp webhook endpoints
│   ├── schemas/
│   │   ├── __init__.py          # Schema exports
│   │   ├── db.py                # Database Pydantic models
│   │   └── whatsapp.py          # WhatsApp webhook payload models
│   └── services/
│       ├── __init__.py          # Services package init
│       ├── llm_service.py       # LLM provider abstraction (OpenAI/OpenRouter)
│       ├── message_processor.py # Core message handling logic
│       ├── supabase_service.py  # Database operations
│       └── whatsapp_service.py  # WhatsApp API client
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── README.md                    # Basic project documentation
├── requirements.txt             # Python dependencies (pinned versions)
├── schema.sql                   # Database schema DDL
└── seed_scenarios.sql           # Initial scenario data
```

---

## Environment Configuration

### Required Environment Variables

```bash
# OpenAI Configuration (required if using OpenAI)
OPENAI_API_KEY=sk-your-openai-api-key-here

# OpenRouter Configuration (optional alternative)
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# LLM Configuration
LLM_PROVIDER=openai              # Options: "openai" | "openrouter"
LLM_MODEL=gpt-4o-mini            # Model name to use

# WhatsApp Cloud API Configuration (required)
WHATSAPP_ACCESS_TOKEN=your-whatsapp-access-token-here
WHATSAPP_PHONE_ID=your-phone-number-id-here
WHATSAPP_VERIFY_TOKEN=your-custom-verify-token-here

# Supabase Configuration (required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key-here

# Application Configuration
ENVIRONMENT=development          # Options: development | staging | production
DEBUG=true                       # Enable debug logging
PORT=8000                        # Server port
```

### Configuration Class ([`app/config.py`](app/config.py))

Uses `pydantic_settings.BaseSettings` for type-safe configuration:
- Loads from `.env` file automatically
- Case-insensitive environment variable matching
- Supports OpenAI and OpenRouter as LLM providers with fallback logic

---

## Database Schema

### Tables

#### 1. `users` - User State Management
```sql
CREATE TABLE users (
    phone_number TEXT PRIMARY KEY,     -- WhatsApp phone number (unique identifier)
    name TEXT,                          -- Optional user name
    current_mode TEXT DEFAULT 'menu',   -- Current bot state: 'menu', 'practice_scenario', 'random_chat'
    current_scenario_id INT,            -- Active scenario ID (if in practice_scenario mode)
    current_session_id UUID,            -- Session UUID for conversation context
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 2. `scenarios` - Practice Scenario Definitions
```sql
CREATE TABLE scenarios (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL,                -- Display title (e.g., "Ordering Coffee")
    bot_persona TEXT NOT NULL,          -- Character the bot plays (e.g., "Friendly Cafe Owner")
    situation_seed TEXT NOT NULL,       -- Context for the scenario
    opening_line TEXT NOT NULL          -- Initial message from bot (may be overridden by LLM)
);
```

#### 3. `chat_history` - Conversation Logs
```sql
CREATE TABLE chat_history (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    phone_number TEXT NOT NULL REFERENCES users(phone_number),
    role TEXT NOT NULL,                 -- 'user' or 'assistant'
    mode TEXT,                          -- Mode when message was sent
    scenario_id INT REFERENCES scenarios(id),
    session_id UUID,                    -- Links messages within a session
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 4. `user_progress` - Scenario Completion Tracking
```sql
CREATE TABLE user_progress (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    phone_number TEXT NOT NULL REFERENCES users(phone_number),
    scenario_id INT NOT NULL REFERENCES scenarios(id),
    status TEXT DEFAULT 'completed',
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(phone_number, scenario_id)
);
```

#### 5. Indexes
```sql
CREATE INDEX idx_chat_history_lookup ON chat_history(phone_number, created_at DESC);
```

### Seed Data - Initial Scenarios

| Title | Bot Persona | Situation |
|-------|-------------|-----------|
| Ordering Coffee | Friendly Cafe Owner | Customer ordering coffee at a local darshini |
| Auto Rickshaw Ride | Busy Auto Driver | Negotiating a ride to MG Road |
| Buying Vegetables | Vegetable Vendor | Buying fresh vegetables at the market |
| Asking Directions | Helpful Stranger | Lost in Jayanagar looking for the metro station |

---

## Application Architecture

### Entry Point ([`app/main.py`](app/main.py))

The FastAPI application:
- Initializes logging based on `DEBUG` setting
- Includes the webhook router at `/whatsapp-webhook`
- Exposes `/health` endpoint for monitoring
- Runs with Uvicorn on configurable port

### Request Flow

```
WhatsApp Cloud API
        │
        ▼
┌─────────────────────────────────────────────────┐
│  GET /whatsapp-webhook (Verification)           │
│  POST /whatsapp-webhook (Message Reception)     │
└─────────────────────────────────────────────────┘
        │
        ▼  (Background Task)
┌─────────────────────────────────────────────────┐
│         MessageProcessor.process_webhook()      │
│  ┌─────────────────────────────────────────┐    │
│  │ 1. Mark message as read                 │    │
│  │ 2. Get/create user from DB              │    │
│  │ 3. Route based on message type:         │    │
│  │    - Text → _handle_text_message()      │    │
│  │    - Interactive → _handle_interactive()│    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
        │
        ▼
┌───────────────┬───────────────┬─────────────────┐
│ SupabaseService│ LLMService   │ WhatsAppService │
│ (DB ops)       │ (AI responses)│ (Send messages) │
└───────────────┴───────────────┴─────────────────┘
```

---

## Core Services

### 1. Message Processor ([`app/services/message_processor.py`](app/services/message_processor.py))

**Purpose**: Core orchestration logic that handles all incoming messages and routes them appropriately.

**Key Components**:

- **`MENU_BUTTONS`**: Main menu options
  ```python
  MENU_BUTTONS = [
      {"id": "practice_scenario_start", "title": "🎭 Practice Scenarios"},
      {"id": "sos_helper", "title": "🚑 SOS Helper"},
      {"id": "random_chat", "title": "☕ Random Chat"}
  ]
  ```

- **`process_webhook()`**: Entry point for all webhooks
  - Marks message as read immediately
  - Retrieves/creates user
  - Routes to appropriate handler

- **`_handle_text_message()`**: Text message routing
  - Global commands: "menu", "hi", "hello", "start", "restart" → Main menu
  - Routes based on `user.current_mode`

- **`_handle_interactive_message()`**: Button/list selection handling
  - Button: practice_scenario_start, random_chat, sos_helper
  - List: scenario selection (scenario_{id})

- **`_start_scenario()`**: Initializes a practice scenario session
  - Creates new session UUID
  - Updates user mode
  - Generates dynamic opening via LLM

- **`_handle_practice_scenario_flow()`**: Manages ongoing scenario conversation
  - Exit commands: "exit", "quit", "stop", "menu", "end"
  - Retrieves session-filtered history
  - Generates LLM response

- **`_handle_chat_flow()`**: Random chat mode conversation

### 2. LLM Service ([`app/services/llm_service.py`](app/services/llm_service.py))

**Purpose**: Abstraction layer for LLM providers using Strategy pattern.

**Architecture**:
```
LLMService (Main wrapper)
    │
    ├── OpenAIService (BaseLLMService)
    │       └── Uses OpenAI's AsyncOpenAI client
    │
    └── OpenRouterService (BaseLLMService)
            └── Uses OpenAI client with custom base_url
```

**Key Methods**:
- `get_chat_response(history)`: For random chat mode
  - Uses `base_system.txt` prompt
  - Temperature: 0.7, Max tokens: 150

- `get_practice_scenario_response(history, scenario)`: For practice scenarios
  - Uses `practice_scenarios_system.txt` prompt with scenario variables
  - Temperature: 0.8, Max tokens: 200

**Provider Selection Logic**:
1. If `LLM_PROVIDER=openrouter` and API key exists → OpenRouterService
2. Otherwise → OpenAIService (default)

### 3. Supabase Service ([`app/services/supabase_service.py`](app/services/supabase_service.py))

**Purpose**: All database operations using Supabase Python client (no ORM).

**Key Functions**:

| Function | Purpose |
|----------|---------|
| `get_or_create_user(phone)` | Retrieve or create user by phone number |
| `update_user_mode(phone, mode, scenario_id?, session_id?)` | Update user state |
| `add_message(phone, role, content, mode, session_id?, scenario_id?)` | Log message to history |
| `get_recent_messages(phone, limit=10, session_id?)` | Get conversation history (chronological) |
| `get_all_scenarios()` | List all available scenarios |
| `get_scenario_by_id(id)` | Get specific scenario |
| `mark_scenario_complete(phone, scenario_id)` | Record completion (upsert) |

### 4. WhatsApp Service ([`app/services/whatsapp_service.py`](app/services/whatsapp_service.py))

**Purpose**: WhatsApp Cloud API client for sending messages.

**Base URL**: `https://graph.facebook.com/v22.0/{phone_id}`

**Key Methods**:

| Method | Purpose |
|--------|---------|
| `mark_message_as_read(message_id)` | Send read receipt |
| `send_text_message(to_phone, content)` | Send plain text |
| `send_interactive_buttons(to_phone, body, buttons)` | Send up to 3 buttons |
| `send_interactive_list_message(to_phone, body, button_text, sections)` | Send list menu (up to 10 items) |

---

## API Endpoints

### Webhook Router ([`app/routers/webhook.py`](app/routers/webhook.py))

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/whatsapp-webhook` | Webhook verification (WhatsApp handshake) |
| POST | `/whatsapp-webhook` | Receive incoming messages |
| GET | `/health` | Health check endpoint |

**Webhook Verification Parameters**:
- `hub.mode` → Must equal "subscribe"
- `hub.verify_token` → Must match `WHATSAPP_VERIFY_TOKEN`
- `hub.challenge` → Returned as plain text response

**Message Processing**: Uses `BackgroundTasks` to return 200 OK immediately while processing asynchronously.

---

## Data Models (Pydantic Schemas)

### Database Models ([`app/schemas/db.py`](app/schemas/db.py))

```python
class UserSchema(BaseModel):
    phone_number: str
    current_mode: str = 'menu'
    current_scenario_id: Optional[int] = None
    current_session_id: Optional[str] = None
    joined_at: Optional[datetime] = None

class ScenarioSchema(BaseModel):
    id: int
    title: str
    bot_persona: str
    situation_seed: str
    opening_line: str

class ChatMessageSchema(BaseModel):
    phone_number: str
    role: str           # 'user' or 'assistant'
    mode: str           # 'menu', 'practice_scenario', 'random_chat'
    scenario_id: Optional[int] = None
    session_id: Optional[str] = None
    content: str
    created_at: datetime

class UserProgressSchema(BaseModel):
    phone_number: str
    scenario_id: int
    status: str         # 'completed'
    completed_at: Optional[datetime] = None
```

### WhatsApp Webhook Models ([`app/schemas/whatsapp.py`](app/schemas/whatsapp.py))

```python
# Nested structure for WhatsApp webhook payload
WhatsAppWebhook
├── object: str
└── entry: List[EntryObject]
    └── changes: List[ChangeObject]
        └── value: ValueObject
            ├── messaging_product: str
            └── messages: List[WhatsAppMessage]
                ├── from_: str (alias='from')
                ├── id: str
                ├── type: str
                ├── text: Optional[TextObject]
                │   └── body: str
                └── interactive: Optional[InteractiveObject]
                    ├── type: str
                    ├── button_reply: Optional[ButtonReply]
                    │   ├── id: str
                    │   └── title: str
                    └── list_reply: Optional[ListReply]
                        ├── id: str
                        ├── title: str
                        └── description: Optional[str]
```

---

## LLM Prompts

### Base System Prompt ([`app/prompts/base_system.txt`](app/prompts/base_system.txt))

Used for: **Random Chat Mode**

**Character**: Friendly, patient, witty Kannada teacher from Bangalore

**Key Rules**:
1. Use "Kanglish" (Kannada in English script)
2. Casual, encouraging tone with emojis
3. Use Bangalore slang: "maadi", "bidi", "guru", "sakkath", "machha"
4. Keep responses short (1-3 sentences) for WhatsApp

**Internal Process**:
1. Think in English first
2. Translate to spoken Bangalore Kannada (NOT textbook)
3. Output Kanglish with English meaning

**Response Format**:
1. Reply in Kanglish + English meaning in parentheses
2. Optional gentle correction with "💡 Better way:"
3. **ALWAYS** provide 2-3 suggested reply options

### Practice Scenarios Prompt ([`app/prompts/practice_scenarios_system.txt`](app/prompts/practice_scenarios_system.txt))

Used for: **Practice Scenario Mode**

**Dynamic Variables** (injected at runtime):
- `{scenario_title}` - e.g., "Ordering Coffee"
- `{bot_persona}` - e.g., "Friendly Cafe Owner"
- `{situation_seed}` - Context description

**Key Rules**:
1. Role-play naturally within scenario
2. **NEVER** use Kannada script - English letters only
3. Use Kannada numbers (ondu, eradu, mooru)
4. Gentle corrections: "almost correct — small correction"
5. Bot leads conversation progression
6. Scenario never ends on its own

**Output Format** (strictly enforced):
```
Bot reply (Kannada in English letters):
<your Kannada reply>

English meaning:
<line-by-line translation to English>

Suggested replies for user:
1) <simple beginner option>
2) <slightly advanced / casual option>
```

---

## User Flow & State Machine

### User Modes

```
┌─────────┐
│  menu   │ (Default state)
└────┬────┘
     │
     ├─── practice_scenario_start (button) ──► Scenario List
     │                                               │
     │                                    scenario_{id} (list)
     │                                               │
     │                                               ▼
     │                                    ┌──────────────────────┐
     │                                    │ practice_scenario    │
     │                                    │ (current_scenario_id)│
     │                                    │ (current_session_id) │
     │                                    └──────────────────────┘
     │                                               │
     │                              "exit/quit/stop/menu/end"
     │                                               │
     │◄──────────────────────────────────────────────┘
     │
     ├─── random_chat (button) ──────────► ┌──────────────┐
     │                                      │ random_chat  │
     │                                      └──────────────┘
     │                                               │
     │                              "menu/hi/hello/start/restart"
     │◄──────────────────────────────────────────────┘
     │
     └─── sos_helper (button) ──────────► Coming Soon (returns to menu)
```

### Global Commands (work in any mode)
- "menu", "hi", "hello", "start", "restart" → Returns to main menu

### Session Management
- Each practice scenario session gets a unique UUID
- Chat history is filtered by `session_id` for context
- Prevents old conversation bleeding into new sessions

---

## Key Features

### ✅ Implemented

1. **Multi-mode Learning**
   - Practice Scenarios: Roleplay real Bangalore situations
   - Random Chat: Freeform conversation practice

2. **Smart LLM Integration**
   - Strategy pattern for provider flexibility
   - OpenAI and OpenRouter support
   - Separate prompts for different modes

3. **WhatsApp Interactive UI**
   - Button menus (up to 3 options)
   - List menus (up to 10 options)
   - Read receipts for UX

4. **Conversation Context**
   - Session-based history tracking
   - Up to 50 messages of context
   - Scenario-specific memory isolation

5. **Gentle Teaching Approach**
   - Never says "wrong"
   - Always provides suggested replies
   - Progressive difficulty in suggestions

### 🚧 Planned / Not Implemented

1. **SOS Helper** - Quick translation feature (placeholder exists)
2. **User name collection** - Schema supports but not implemented
3. **Progress tracking** - `mark_scenario_complete()` exists but not called
4. **Voice messages** - WhatsApp supports but not handled

---

## Dependencies

### Core Dependencies (from [`requirements.txt`](requirements.txt))

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.122.0 | Web framework |
| uvicorn | 0.38.0 | ASGI server |
| pydantic | 2.12.5 | Data validation |
| pydantic-settings | 2.6.1 | Configuration management |
| python-dotenv | 1.0.1 | .env file loading |
| openai | 1.54.0 | OpenAI API client |
| supabase | 2.3.4 | Supabase client |
| httpx | 0.25.2 | Async HTTP client |
| psycopg2 | 2.9.11 | PostgreSQL adapter |
| SQLAlchemy | 2.0.44 | (Not actively used) |

---

## Setup & Deployment

### Local Development

```bash
# 1. Clone and setup
git clone <repository-url>
cd chatlingo-ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Setup database
# Run schema.sql in Supabase SQL editor
# Run seed_scenarios.sql for initial data

# 4. Run the application
python -m app.main
# OR
uvicorn app.main:app --reload --port 8000

# 5. Expose for WhatsApp (use ngrok for local testing)
ngrok http 8000
# Configure webhook URL in Meta Developer Console
```

### Production Deployment (Render)

1. Connect GitHub repository to Render
2. Set environment variables in Render dashboard
3. Configure build command: `pip install -r requirements.txt`
4. Configure start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Update WhatsApp webhook URL to Render domain

### Health Check

```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "environment": "development"}
```

---

## Important Notes for Modifications

1. **Adding New Scenarios**: Insert into `scenarios` table with `title`, `bot_persona`, `situation_seed`, `opening_line`

2. **Changing LLM Behavior**: Modify prompts in `app/prompts/` directory

3. **Adding New Message Types**: Update `WhatsAppMessage` schema and `message_processor.py`

4. **New User Modes**: 
   - Add to `update_user_mode()` allowed values
   - Add handler in `_handle_text_message()` switch
   - Add button in `MENU_BUTTONS`

5. **Database Changes**: 
   - Update `schema.sql`
   - Update corresponding Pydantic schemas in `app/schemas/db.py`
   - Update `supabase_service.py` functions

---

*Last Updated: February 2026*
*Version: 0.1.0*
