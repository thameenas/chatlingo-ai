# Telegram Bot Setup Guide

This guide will help you set up Chatlingo AI to work with Telegram.

## Prerequisites

- A Telegram account
- Your Chatlingo AI backend deployed and accessible via HTTPS

## Step 1: Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Start a chat with BotFather and send `/newbot`
3. Follow the prompts:
   - Choose a **display name** for your bot (e.g., "Chatlingo AI")
   - Choose a **username** for your bot (must end in 'bot', e.g., "chatlingo_ai_bot")
4. BotFather will give you a **bot token** that looks like:
   ```
   1234567890:ABCdefGhIjKlmNoPQRsTUVwxyZ
   ```
5. **Save this token** - you'll need it for configuration

## Step 2: Configure Environment Variables

Add the following to your `.env` file:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
TELEGRAM_WEBHOOK_SECRET=your-random-secret-string-here
```

**Notes:**
- `TELEGRAM_BOT_TOKEN`: The token you got from BotFather
- `TELEGRAM_WEBHOOK_SECRET`: A random string for webhook security (you create this yourself)
  - Example: `my_super_secret_webhook_token_123`
  - This protects your webhook from unauthorized requests

## Step 3: Set the Webhook

Once your application is deployed and running, set the webhook URL using one of these methods:

### Option A: Using cURL

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-domain.com/telegram-webhook",
    "secret_token": "your-random-secret-string-here"
  }'
```

Replace:
- `<YOUR_BOT_TOKEN>` with your actual bot token
- `https://your-domain.com` with your deployed domain
- `your-random-secret-string-here` with your TELEGRAM_WEBHOOK_SECRET

### Option B: Using the API Endpoint

Your app exposes a helper endpoint. Just navigate to:

```
https://your-domain.com/telegram-webhook-info
```

This will show your current webhook status.

### Option C: Programmatically (Python)

```python
import httpx
import asyncio

async def setup_webhook():
    from app.services.telegram_service import telegram_service
    
    webhook_url = "https://your-domain.com/telegram-webhook"
    secret = "your-random-secret-string-here"
    
    result = await telegram_service.set_webhook(webhook_url, secret)
    print(result)

# Run it
asyncio.run(setup_webhook())
```

## Step 4: Test Your Bot

1. Open Telegram and search for your bot using its username (e.g., `@chatlingo_ai_bot`)
2. Click **Start** or send `/start`
3. You should receive the main menu with buttons:
   - 🎭 Practice Scenarios
   - 🚑 SOS Helper
   - ☕ Random Chat

## Important Notes

### WhatsApp vs Telegram

Both platforms can run **simultaneously**:
- **WhatsApp users** are identified by their phone number
- **Telegram users** are identified by their chat_id (numeric)
- They share the same database, but users are kept separate
- All conversation logic, scenarios, and LLM integration work the same way

### Webhook Requirements

- Your webhook URL **must use HTTPS** (not HTTP)
- Telegram doesn't support `localhost` - use **ngrok** for local testing:
  ```bash
  ngrok http 8000
  # Use the https URL provided by ngrok
  ```

### Differences from WhatsApp

**Advantages:**
- ✅ No business verification needed
- ✅ Instant setup (< 5 minutes)
- ✅ Free forever
- ✅ Better button support
- ✅ No rate limits for small bots

**UI Differences:**
- Uses **inline keyboards** instead of WhatsApp's interactive buttons
- List menus are converted to inline keyboard buttons
- Markdown formatting supported for text

## Troubleshooting

### "Webhook not set" error

Check your webhook status:
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

### Bot not responding

1. Check logs for errors: `DEBUG=true` in `.env`
2. Verify webhook URL is correct and accessible
3. Ensure `TELEGRAM_BOT_TOKEN` is set correctly
4. Check that your server is running and accessible via HTTPS

### Testing Locally

For local development:
1. Install ngrok: `brew install ngrok` (Mac) or download from ngrok.com
2. Run your app: `uvicorn app.main:app --reload --port 8000`
3. In another terminal: `ngrok http 8000`
4. Use the ngrok HTTPS URL for webhook setup
5. Keep ngrok running while testing

## Example: Complete Setup Flow

```bash
# 1. Add to .env
echo "TELEGRAM_BOT_TOKEN=1234567890:ABCdefGhIjKlmNoPQRsTUVwxyZ" >> .env
echo "TELEGRAM_WEBHOOK_SECRET=my_secret_token_xyz" >> .env

# 2. Start your app
uvicorn app.main:app --reload

# 3. In another terminal, start ngrok (for local testing)
ngrok http 8000
# Note the HTTPS URL (e.g., https://abc123.ngrok.io)

# 4. Set webhook
curl -X POST "https://api.telegram.org/bot1234567890:ABCdefGhIjKlmNoPQRsTUVwxyZ/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://abc123.ngrok.io/telegram-webhook",
    "secret_token": "my_secret_token_xyz"
  }'

# 5. Test in Telegram
# Open Telegram, search for your bot, send /start
```

## Bot Commands

You can set bot commands in BotFather for a better UX:

```
/start - Start the bot and show main menu
/menu - Show main menu
```

To set them:
1. Message @BotFather
2. Send `/setcommands`
3. Select your bot
4. Send:
   ```
   start - Start the bot and show main menu
   menu - Show main menu
   ```

## Production Deployment

When deploying to production (e.g., Render, Heroku):

1. Set environment variables in your hosting dashboard
2. Use your production domain for webhook URL
3. After deployment, update webhook:
   ```bash
   curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://your-production-domain.com/telegram-webhook",
       "secret_token": "your-secret-token"
     }'
   ```

---

Need help? Check the [Telegram Bot API documentation](https://core.telegram.org/bots/api)
