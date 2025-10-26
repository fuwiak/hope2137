#!/bin/bash
# Multi-Platform Bot Setup Script

echo "🤖 Multi-Platform Bot Setup"
echo "=========================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+ first."
    echo "💡 Install from: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm first."
    exit 1
fi

echo "✅ npm found: $(npm --version)"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Install Node.js dependencies
echo ""
echo "📦 Installing Node.js dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Node.js dependencies installed"
else
    echo "❌ Failed to install Node.js dependencies"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# AI Configuration
GROQ_API_KEY=your_groq_api_key_here

# YClients API Configuration
YCLIENTS_PARTNER_TOKEN=your_yclients_partner_token_here
YCLIENTS_USER_TOKEN=your_yclients_user_token_here
EOF
    echo "✅ .env template created"
    echo "📝 Please edit .env file with your API keys"
else
    echo "✅ .env file found"
fi

# Create directories
echo ""
echo "📁 Creating directories..."
mkdir -p logs whatsapp-sessions

echo "✅ Setup completed!"
echo ""
echo "🚀 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: python multi_bot.py (for both bots)"
echo "3. Or run: python app.py (Telegram only)"
echo "4. Or run: python whatsapp_bot.py (WhatsApp only)"
echo ""
echo "📱 For WhatsApp bot:"
echo "1. Run the bot"
echo "2. Scan QR code with your phone"
echo "3. Bot will be connected to your WhatsApp"
echo ""
echo "🎉 Enjoy your multi-platform bot!"
