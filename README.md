# Telegram Bot with YClients Integration

This bot provides a menu system for booking appointments with specialists through YClients API.

## Features

- 📋 **Services Menu** - View real-time services from YClients API with prices and duration
- 👥 **Masters Menu** - View actual specialists and their specializations from API
- 📅 **User Records** - View and manage user appointments with full details
- 💬 **AI Chat** - Intelligent conversation with AI assistant using real API data
- 🔄 **Interactive Menu** - Easy navigation with inline buttons
- 🔄 **Real-time Data** - All information comes directly from YClients API
- 🗑️ **Record Management** - Delete appointments directly from the bot

## Setup

1. **Install dependencies:**
   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Create a `.env` file with the following variables:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   GROQ_API_KEY=your_groq_api_key_here
   YCLIENTS_PARTNER_TOKEN=your_yclients_partner_token_here
   YCLIENTS_USER_TOKEN=your_yclients_user_token_here
   ```

3. **Run the bot:**
   ```bash
   python app.py
   ```

## Bot Commands

- `/start` - Start the bot and show main menu
- `/menu` - Show main menu
- Send any text message to chat with AI assistant

## Menu Options

- **📋 Услуги** - Shows available services with prices and duration
- **👥 Мастера** - Shows available specialists and their specializations
- **📅 Мои записи** - View and manage user appointments
- **📝 Записаться** - Create new appointment with AI assistance
- **💬 Чат с AI** - Enables AI chat mode

## How to Book an Appointment

1. **Register Phone**: Send your phone number (e.g., +79991234567)
2. **Start Booking**: Click "📝 Записаться" in main menu
3. **Describe Request**: Write your booking request (e.g., "Хочу записаться на маникюр к Арине на завтра в 14:00")
4. **AI Processing**: Bot will create real appointment in YClients system
5. **Confirmation**: Receive confirmation with appointment details

## User Records Features

- **View Records** - See all your appointments with full details
- **Record Details** - Date, time, master, services, status
- **Delete Records** - Remove appointments directly from bot
- **Status Tracking** - See appointment status (confirmed, completed, waiting, etc.)
- **Real Booking** - Create actual appointments in YClients system
- **Phone Registration** - Register phone number for appointment creation

## YClients Integration

The bot integrates with YClients API to:
- Fetch real-time service data directly from your YClients system
- Display actual available specialists and their specializations
- Show real service prices and duration from your database
- Handle company-specific data without hardcoded information
- Provide AI responses based on real API data only

## Testing API Connection

Before running the bot, test your YClients API connection:

```bash
python test_api.py
```

This will verify your tokens and show available services and masters.

## Requirements

- Python 3.11+
- Telegram Bot Token
- Groq API Key
- YClients Partner and User Tokens
