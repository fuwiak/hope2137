#!/bin/bash

# Start both bots in background
echo "🚀 Starting Multi-Platform Bot System..."

# Start Telegram bot in background
echo "🤖 Starting Telegram Bot..."
python3 app.py &
TELEGRAM_PID=$!

# Start WhatsApp bot in background  
echo "📱 Starting WhatsApp Bot..."
python3 whatsapp_bot.py &
WHATSAPP_PID=$!

# Function to handle shutdown
cleanup() {
    echo "🛑 Shutting down bots..."
    kill $TELEGRAM_PID $WHATSAPP_PID 2>/dev/null
    wait $TELEGRAM_PID $WHATSAPP_PID 2>/dev/null
    echo "✅ Bots stopped successfully!"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

echo "✅ Both bots started successfully!"
echo "📊 Telegram Bot PID: $TELEGRAM_PID"
echo "📊 WhatsApp Bot PID: $WHATSAPP_PID"

# Wait for processes
wait $TELEGRAM_PID $WHATSAPP_PID