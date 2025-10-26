#!/bin/bash

# Multi-Platform Bot Startup Script
# Uruchamia oba boty (Telegram + WhatsApp) jednocześnie

echo "🚀 Starting Multi-Platform Bot System..."

# Sprawdź czy Python jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nie jest zainstalowany!"
    exit 1
fi

# Sprawdź czy plik .env istnieje
if [ ! -f ".env" ]; then
    echo "❌ Plik .env nie istnieje!"
    echo "📝 Utwórz plik .env z wymaganymi zmiennymi środowiskowymi"
    exit 1
fi

# Sprawdź czy wymagane pakiety są zainstalowane
echo "📦 Sprawdzanie zależności..."
python3 -c "import telegram, yclients, groq, whatsapp_chatbot" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 Instalowanie zależności..."
    pip3 install -r requirements.txt
fi

# Uruchom boty
echo "🎯 Uruchamianie botów..."
python3 run_bots.py
