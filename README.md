# Chatlingo AI 🗣️

A **multi-platform chatbot** that teaches spoken Bangalore Kannada (Kanglish) to English speakers through conversational learning.

## 🌟 Features

- 🎭 **Practice Scenarios**: Roleplay real Bangalore situations (ordering coffee, taking an auto, etc.)
- ☕ **Random Chat**: Freeform conversation practice
- 🧠 **AI-Powered**: Uses GPT-4/Claude for natural, adaptive responses
- 📱 **Multi-Platform**: Works on both **WhatsApp** and **Telegram**
- 🔤 **Kanglish**: Kannada written in English letters (no script knowledge needed)
- 💡 **Smart Teaching**: Gentle corrections with suggested replies

## 📚 Tech Stack

- **Backend**: Python FastAPI
- **Database**: Supabase (PostgreSQL)
- **LLM**: OpenAI GPT-4o-mini or OpenRouter (Claude, etc.)
- **Platforms**: WhatsApp Cloud API + Telegram Bot API
- **Hosting**: Render / Heroku / any cloud with HTTPS

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Supabase account (free tier works)
- OpenAI API key OR OpenRouter API key
- (Optional) WhatsApp Cloud API credentials
- (Optional) Telegram Bot Token

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd chatlingo-ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 5. Setup database
# Run schema.sql in your Supabase SQL editor
# Run seed_scenarios.sql for initial practice scenarios

# 6. Run the application
python -m app.main
# OR
uvicorn app.main:app --reload --port 8000
```

## 🔧 Configuration

Edit your `.env` file with the following:

```bash
# LLM Configuration (pick one)
OPENAI_API_KEY=sk-your-key-here
# OR
OPENROUTER_API_KEY=your-key-here
LLM_PROVIDER=openai  # or "openrouter"
LLM_MODEL=gpt-4o-mini

# Supabase (required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# WhatsApp (optional - if you want WhatsApp support)
WHATSAPP_ACCESS_TOKEN=your-token
WHATSAPP_PHONE_ID=your-phone-id
WHATSAPP_VERIFY_TOKEN=your-verify-token

# Telegram (optional - if you want Telegram support)
TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
TELEGRAM_WEBHOOK_SECRET=your-random-secret

# App Settings
ENVIRONMENT=development
DEBUG=true
PORT=8000
```

## 📱 Platform Setup

### WhatsApp Setup

1. Create a Meta Developer account
2. Set up WhatsApp Cloud API
3. Get your access token, phone ID, and verify token
4. Configure webhook URL: `https://your-domain.com/whatsapp-webhook`
5. Add credentials to `.env`

**Note**: WhatsApp requires business verification for production use.

### Telegram Setup (Recommended for Quick Start)

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow prompts
3. Copy the bot token to `.env`
4. Set webhook: 
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-domain.com/telegram-webhook"}'
   ```

**See [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) for detailed instructions.**

## 🗄️ Database Schema

The app uses 4 main tables:

- **users**: User state and progress (`phone_number` stores both phone numbers and Telegram chat IDs)
- **scenarios**: Practice scenario definitions
- **chat_history**: Conversation logs
- **user_progress**: Scenario completion tracking

Run `schema.sql` and `seed_scenarios.sql` in your Supabase SQL editor.

## 📖 Usage

### For Users

**On Telegram:**
1. Search for your bot (e.g., `@chatlingo_ai_bot`)
2. Click Start or send `/start`
3. Choose an option from the menu

**On WhatsApp:**
1. Send "Hi" to your WhatsApp bot number
2. Follow the interactive menu

### Available Commands

- `menu`, `hi`, `hello`, `start`, `/start` - Show main menu
- `exit`, `quit`, `stop`, `end` - Exit current scenario
- Any natural language - Practice Kannada!

## 🎭 Practice Scenarios

Default scenarios included:
- ☕ **Ordering Coffee** - At a local darshini
- 🛺 **Auto Rickshaw Ride** - Negotiating to MG Road
- 🥬 **Buying Vegetables** - At the market
- 🗺️ **Asking Directions** - Lost in Jayanagar

Add more scenarios via the database!

## 🔍 Project Structure

```
chatlingo-ai/
├── app/
│   ├── routers/          # Webhook endpoints
│   │   ├── webhook.py           # WhatsApp webhooks
│   │   └── telegram_webhook.py  # Telegram webhooks
│   ├── services/         # Business logic
│   │   ├── message_processor.py # Platform-agnostic message handling
│   │   ├── telegram_service.py  # Telegram Bot API client
│   │   ├── whatsapp_service.py  # WhatsApp Cloud API client
│   │   ├── platform_adapter.py  # Unified platform interface
│   │   ├── conversation_engine.py # Core conversation logic
│   │   ├── llm_service.py       # LLM provider abstraction
│   │   └── supabase_service.py  # Database operations
│   ├── schemas/          # Pydantic models
│   │   ├── whatsapp.py   # WhatsApp webhook schemas
│   │   ├── telegram.py   # Telegram webhook schemas
│   │   └── db.py         # Database schemas
│   ├── prompts/          # LLM system prompts
│   ├── config.py         # Configuration
│   └── main.py           # FastAPI app entry point
├── schema.sql            # Database schema
├── seed_scenarios.sql    # Initial scenario data
├── requirements.txt
├── .env.example
└── README.md
```

## 🚢 Deployment

### Deploy to Render

1. Connect your GitHub repo to Render
2. Create a new Web Service
3. Set environment variables in Render dashboard
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Deploy!
7. Update webhook URLs with your Render domain

### Local Testing with ngrok

```bash
# Terminal 1: Run the app
uvicorn app.main:app --reload --port 8000

# Terminal 2: Expose with ngrok
ngrok http 8000

# Use the ngrok HTTPS URL for webhook setup
```

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### CLI Testing (without webhook)

```bash
# Test conversation logic directly
python cli.py --message "Namaskara! How do I say coffee?"
```

## 📝 Development

### Adding New Scenarios

```sql
INSERT INTO scenarios (title, bot_persona, situation_seed, opening_line)
VALUES (
    'Scenario Title',
    'Bot Character Description',
    'Situation context for the LLM',
    'Opening line from the bot'
);
```

### Modifying Bot Behavior

Edit the prompt files:
- `app/prompts/base_system.txt` - For random chat mode
- `app/prompts/practice_scenarios_system.txt` - For scenario mode

### Adding New Features

1. Multi-platform design: Use `platform_adapter.py` for UI operations
2. Business logic: Add to `conversation_engine.py` or `message_processor.py`
3. Database: Update `schema.sql`, `schemas/db.py`, and `supabase_service.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on both platforms (if applicable)
5. Submit a pull request

## 📄 License

MIT License - feel free to use and modify!

## 🙏 Acknowledgments

- Built for Bangalore Kannada learners
- Inspired by real language learning challenges
- Powered by AI for adaptive teaching

## 📞 Support

- Issues: [GitHub Issues](your-repo-url/issues)
- Documentation: [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)
- Telegram Setup: [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)

---

**Made with ❤️ for Bangalore Kannada learners**

*Maadi, guru! Chennagide! 🎉*
