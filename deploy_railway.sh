#!/bin/bash

# Railway Deployment Script
echo "🚀 Deploying Telegram Bot to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Create new project or link to existing
echo "📦 Creating/linking Railway project..."
railway link

# Set environment variables
echo "🔧 Setting environment variables..."
railway variables set TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN"
railway variables set GROQ_API_KEY="$GROQ_API_KEY"
railway variables set YCLIENTS_PARTNER_TOKEN="$YCLIENTS_PARTNER_TOKEN"
railway variables set YCLIENTS_USER_TOKEN="$YCLIENTS_USER_TOKEN"

# Deploy
echo "🚀 Deploying to Railway..."
railway up

# Get deployment URL
echo "🌐 Getting deployment URL..."
railway domain

echo "✅ Deployment complete!"
echo "🔍 Check health: https://your-app.railway.app/health"
echo "📊 Monitor logs: railway logs"

