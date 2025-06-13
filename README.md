# Kannada WhatsApp Bot

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

## Deployment

### Heroku

1. Create a Heroku account and install the Heroku CLI
2. Login to Heroku:
```bash
heroku login
```

3. Create a new Heroku app:
```bash
heroku create your-app-name
```

4. Set environment variables:
```bash
heroku config:set GEMINI_API_KEY=your_gemini_api_key
heroku config:set TWILIO_ACCOUNT_SID=your_twilio_account_sid
heroku config:set TWILIO_AUTH_TOKEN=your_twilio_auth_token
```

5. Deploy:
```bash
git push heroku main
```

### Other Platforms

The application can be deployed to any platform that supports Python web applications (e.g., DigitalOcean, AWS, Google Cloud Platform). Make sure to:

1. Set up the required environment variables
2. Use gunicorn as the WSGI server
3. Configure the platform to use the `Procfile`

## Database

The application uses SQLite for data persistence. The database file (`chat.db`) will be created automatically when the application starts.

## API Endpoints

- `POST /api/chat`: Handle chat messages
  - Body: `{"user_msg": "message", "session_id": "user_id"}`
  - Returns: `{"response": "bot_response"}`

- `POST /api/reset`: Reset chat history
  - Body: `{"session_id": "user_id"}`
  - Returns: `{"response": "Chat history cleared"}`

## License

[Your chosen license] 