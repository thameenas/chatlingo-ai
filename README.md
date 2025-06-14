# Language WhatsApp Bot

A WhatsApp bot that provides interactive scenarios in Kannada language.

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd kannada-whatsapp-bot
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
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
```

## Local Development

Run the development server:
```bash
python app.py
```

The server will start at `http://localhost:5000`

## Deployment on Render

1. Create a Render account at https://render.com

2. Connect your GitHub repository to Render:
   - Click "New +" in the Render dashboard
   - Select "Web Service"
   - Connect your GitHub repository
   - Select the repository

3. Configure the deployment:
   - Name: `kannada-whatsapp-scenarios` (or your preferred name)
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Plan: `Free`

4. Set up environment variables in Render:
   - Go to the "Environment" tab
   - Add the following variables:
     - `GEMINI_API_KEY`
     - `TWILIO_ACCOUNT_SID`
     - `TWILIO_AUTH_TOKEN`
   - The `DATABASE_URL` will be automatically set by Render

5. Deploy:
   - Click "Create Web Service"
   - Render will automatically deploy your application
   - You can monitor the deployment in the "Events" tab

6. Access your application:
   - Once deployed, Render will provide a URL like `https://kannada-whatsapp-scenarios.onrender.com`
   - Update your Twilio webhook URL to point to this new URL

## Database

The application uses PostgreSQL for data persistence. The database is automatically provisioned by Render and includes:

- `last_day_number` table: Stores the last day number for each phone number
- `chat_history` table: Stores the chat history with timestamps

The database connection is automatically configured using the `DATABASE_URL` environment variable provided by Render.

## API Endpoints

- `POST /api/chat`: Handle chat messages
  - Body: `{"user_msg": "message", "session_id": "user_id"}`
  - Returns: `{"response": "bot_response"}`

- `POST /api/reset`: Reset chat history
  - Body: `{"session_id": "user_id"}`
  - Returns: `{"response": "Chat history cleared"}`

## License

[Your chosen license] 
