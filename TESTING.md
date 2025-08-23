# Testing the WhatsApp Cloud API Integration

This document provides step-by-step instructions for testing the WhatsApp Cloud API integration locally before deploying to Render.

## Prerequisites

1. A Meta Developer account with WhatsApp Business API access
2. Your WhatsApp API Token, Phone Number ID, and a custom Verification Token
3. Ngrok or a similar tool to expose your local server to the internet

## Setup Environment Variables

1. Create or update your `.env` file with the following variables:
```
GEMINI_API_KEY=your_gemini_api_key
WHATSAPP_API_TOKEN=your_whatsapp_api_token
WHATSAPP_PHONE_NUMBER_ID=your_whatsapp_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_custom_verification_token
DATABASE_URL=your_postgresql_connection_string
```

## Local Testing Steps

### 1. Start Your Local Server

```bash
# Install dependencies if you haven't already
pip install -r requirements.txt

# Start the Flask server
python app.py
```

Your server should start on port 8000 by default.

### 2. Expose Your Local Server

Use Ngrok to expose your local server to the internet:

```bash
ngrok http 8000
```

Ngrok will provide you with a public URL (e.g., `https://a1b2c3d4.ngrok.io`).

### 3. Configure Webhook in Meta Developer Dashboard

1. Go to your Meta Developer Dashboard
2. Navigate to your WhatsApp app
3. Go to the "Webhooks" section
4. Set up a webhook with the following details:
   - Callback URL: `https://your-ngrok-url/whatsapp-webhook`
   - Verify Token: The same value you set for `WHATSAPP_VERIFY_TOKEN`
   - Subscribe to the `messages` field

### 4. Test Webhook Verification

When you save the webhook configuration, Meta will send a verification request to your webhook. Your application should respond with the challenge value.

Check your application logs to see if the verification was successful.

### 5. Send a Test Message

1. Find your test WhatsApp number in the Meta Developer Dashboard
2. Add this number to your phone contacts
3. Open WhatsApp and start a chat with this contact
4. Send a simple message like "start" or "hello"

### 6. Check Application Logs

Watch your Flask application logs for:
1. Incoming webhook data
2. Message parsing
3. Response generation
4. Message sending

You should see logs for each step of the process.

### 7. Verify Response

You should receive a response from the bot on WhatsApp.

## Troubleshooting

### Webhook Verification Issues

If webhook verification fails:
- Check that your ngrok URL is correct and includes `/whatsapp-webhook`
- Verify that your verification token matches exactly
- Ensure your Flask app is running and accessible via ngrok

### Message Reception Issues

If your webhook isn't receiving messages:
- Check that you've subscribed to the `messages` webhook field
- Verify that your ngrok tunnel is still active
- Add more detailed logging in your webhook handler

### Message Sending Issues

If you're not receiving responses:
- Check your WhatsApp API Token and Phone Number ID
- Verify that your access token has the correct permissions
- Check the response from the WhatsApp API for error messages

### Debug Logging

Add these lines to your webhook handler for more detailed logging:

```python
@app.route("/whatsapp-webhook", methods=["POST"])
def whatsapp_webhook():
    print("Webhook called!")
    print(f"Headers: {request.headers}")
    data = request.get_json()
    print(f"Data: {json.dumps(data, indent=2)}")
    # Rest of your code...
```

## Deployment to Render

Once you've verified that the integration works locally, you can deploy to Render:

1. Update your environment variables in Render
2. Deploy your application
3. Update your webhook URL in the Meta Developer Dashboard to point to your Render URL
4. Test the integration again with your deployed application

## Common Issues

1. **Rate Limiting**: WhatsApp Cloud API has rate limits for test numbers
2. **24-Hour Window**: WhatsApp has a 24-hour messaging window policy
3. **Webhook Timeouts**: Ensure your webhook responds within 20 seconds
4. **Message Format**: Check that you're sending messages in the correct format