# Language WhatsApp Bot

A WhatsApp bot that provides interactive scenarios in Kannada language with automatic daily nudges, built using the Model-Service-Controller-Repository (MSCR) architecture. This application uses the WhatsApp Cloud API for messaging.

## Architecture

This application follows the **Model-Service-Controller-Repository (MSCR)** pattern:

- **Models**: Data structures and database entities
- **Services**: Business logic and external integrations
- **Controllers**: HTTP request/response handling
- **Repositories**: Data access and persistence layer

### Architecture Benefits:
- **Separation of Concerns**: Each layer has a specific responsibility
- **Testability**: Easy to unit test individual components
- **Maintainability**: Changes in one layer don't affect others
- **Scalability**: Easy to add new features or modify existing ones

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd chatlingo-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following variables:
```
GEMINI_API_KEY=your_gemini_api_key
WHATSAPP_API_TOKEN=your_whatsapp_api_token
WHATSAPP_PHONE_NUMBER_ID=your_whatsapp_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_custom_verification_token
DATABASE_URL=your_postgresql_connection_string
```

## Local Development

Run the development server:
```bash
python app.py
```

The server will start at `http://localhost:8000`

## Daily Nudge Feature

The application automatically sends daily nudges to all users at **9:00 AM IST** (3:30 AM UTC). 

### How it works:
- **Scheduled Job**: Runs daily at 9:00 AM IST using APScheduler
- **User Discovery**: Finds all users from the `last_day_number` table
- **Personalized Content**: Sends the first prompt of each user's current day
- **WhatsApp Delivery**: Uses WhatsApp Cloud API to send messages directly to users

### Testing Nudges:
You can manually trigger nudges for testing:
```bash
# Using curl
curl -X POST http://localhost:8000/api/nudges/send

# Or run the test script
python test_nudges.py
```

### Nudge Behavior:
- Users receive the actual first prompt of their daily lesson
- No need to type "start" or "day X" - the lesson begins automatically
- Messages are sent via WhatsApp using the WhatsApp Cloud API

## Deployment on Render

1. Create a Render account at https://render.com

2. Connect your GitHub repository to Render:
   - Click "New +" in the Render dashboard
   - Select "Web Service"
   - Connect your GitHub repository
   - Select the repository

3. Configure the deployment:
   - Name: `chatlingo-ai` (or your preferred name)
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Plan: `Free`

4. Set up environment variables in Render:
   - Go to the "Environment" tab
   - Add the following variables:
     - `GEMINI_API_KEY`
     - `WHATSAPP_API_TOKEN`
     - `WHATSAPP_PHONE_NUMBER_ID`
     - `WHATSAPP_VERIFY_TOKEN`
   - The `DATABASE_URL` will be automatically set by Render

5. Deploy:
   - Click "Create Web Service"
   - Render will automatically deploy your application
   - You can monitor the deployment in the "Events" tab

6. Access your application:
   - Once deployed, Render will provide a URL like `https://chatlingo.ai.onrender.com`
   - Set up your WhatsApp webhook in the Meta Developer Dashboard:
     - Webhook URL: `https://your-app-url.com/whatsapp-webhook`
     - Verify token: The same value you set for `WHATSAPP_VERIFY_TOKEN`
     - Subscribe to the `messages` webhook field

## Database

The application uses PostgreSQL for data persistence. The database is automatically provisioned by Render and includes:

- `last_day_number` table: Stores the last day number and original phone number for each user
- `chat_history` table: Stores the chat history with timestamps

The database connection is automatically configured using the `DATABASE_URL` environment variable provided by Render.

## API Endpoints

- `POST /api/chat`: Handle chat messages
  - Body: `{"user_msg": "message", "session_id": "user_id"}`
  - Returns: `{"response": "bot_response"}`

- `POST /api/reset`: Reset chat history
  - Body: `{"session_id": "user_id"}`
  - Returns: `{"response": "Chat history cleared"}`

- `POST /api/nudges/send`: Manually trigger daily nudges (for testing)
  - Returns: `{"response": "Daily nudges sent successfully"}`

## File Structure

```
chatlingo-ai/
├── app.py                    # Main Flask application (routing only)
├── scheduler.py             # Background job scheduler
├── test_nudges.py           # Test script for nudge functionality
├── requirements.txt         # Python dependencies
├── scenarios.json           # 30-day learning scenarios
├── prompt_template.txt      # AI prompt template
├── models/                  # Data models layer
│   ├── __init__.py
│   ├── user.py             # User-related models
│   └── chat.py             # Chat-related models
├── repositories/            # Data access layer
│   ├── __init__.py
│   ├── database.py         # Database configuration and session management
│   ├── user_repository.py  # User data operations
│   └── chat_repository.py  # Chat data operations
├── services/               # Business logic layer
│   ├── __init__.py
│   ├── llm_service.py      # LLM/Gemini integration
│   ├── chat_service.py     # Chat and nudge business logic
│   └── whatsapp_service.py # WhatsApp Cloud API integration
├── controllers/            # HTTP request/response layer
│   ├── __init__.py
│   └── chat_controller.py  # Chat and nudge HTTP endpoints
└── static/                 # Web interface files
    ├── index.html
    ├── script.js
    └── refreshui.js
```

## Architecture Layers

### Models Layer (`models/`)
- **`user.py`**: `LastDayNumber` model for user progress tracking
- **`chat.py`**: `ChatHistory` model for message storage

### Repositories Layer (`repositories/`)
- **`database.py`**: Database configuration and session management
- **`user_repository.py`**: Handles all user-related database operations
- **`chat_repository.py`**: Handles all chat-related database operations

### Services Layer (`services/`)
- **`llm_service.py`**: Manages LLM/Gemini integration and prompt generation
- **`chat_service.py`**: Orchestrates chat functionality, nudge sending, and user interactions
- **`whatsapp_service.py`**: Handles WhatsApp Cloud API integration for messaging

### Controllers Layer (`controllers/`)
- **`chat_controller.py`**: Handles HTTP requests for chat functionality and nudge operations

### Infrastructure
- **`scheduler.py`**: Background job scheduling for daily nudges
- **`app.py`**: Main Flask application with route definitions

## License

[Your chosen license]

## WhatsApp Cloud API Setup

### Prerequisites
1. A Meta Developer account (https://developers.facebook.com/)
2. A WhatsApp Business account
3. A phone number registered with WhatsApp Business

### Setup Steps
1. Create a Meta App in the Meta Developer Dashboard
2. Set up WhatsApp in the app
3. Get your Phone Number ID from the WhatsApp > Getting Started page
4. Generate a temporary access token or set up a System User for permanent access
5. Create a custom verification token (any random string) for webhook verification
6. Configure your webhook URL in the Meta Developer Dashboard:
   - URL: `https://your-app-url.com/whatsapp-webhook`
   - Verification Token: The value you set for `WHATSAPP_VERIFY_TOKEN`
   - Subscribe to the `messages` webhook field

### Testing
1. Send a message to your WhatsApp Business number
2. The webhook should receive the message and your application should respond
3. Check your application logs for any errors

### Troubleshooting
- Ensure your webhook URL is publicly accessible
- Verify that your access token has the correct permissions
- Check that your webhook is properly verified and subscribed to the `messages` field
- Monitor your application logs for detailed error messages