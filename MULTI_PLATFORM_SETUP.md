# Multi-Platform Bot Setup Instructions

## Environment Variables

Add these variables to your `.env` file:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# YClients API Configuration
YCLIENTS_PARTNER_TOKEN=your_yclients_partner_token_here
YCLIENTS_USER_TOKEN=your_yclients_user_token_here

# Groq API Configuration (for AI responses)
GROQ_API_KEY=your_groq_api_key_here

# Green API Configuration (for WhatsApp)
GREEN_API_ID=your_green_api_id_here
GREEN_API_TOKEN=your_green_api_token_here
```

## Getting Green API Credentials

1. Go to https://greenapi.com/
2. Register an account
3. Get your `idInstance` and `apiTokenInstance`
4. Add them to `.env` as `GREEN_API_ID` and `GREEN_API_TOKEN`

## Running the Bots

### Option 1: Run both bots together
```bash
python run_bots.py
```

### Option 2: Run bots separately
```bash
# Telegram bot only
python app.py

# WhatsApp bot only
python whatsapp_bot.py
```

## Features

Both bots share the same functionality:
- ✅ YClients API integration
- ✅ Real-time service and master data
- ✅ Booking creation and management
- ✅ AI-powered responses
- ✅ Phone number validation
- ✅ Service validation
- ✅ No duplicate responses

## Architecture

- `bot_core.py` - Shared business logic
- `app.py` - Telegram bot
- `whatsapp_bot.py` - WhatsApp bot
- `run_bots.py` - Multi-platform launcher
- `yclients_client.py` - YClients API client
