# 🚀 Railway Deployment Guide

## 📋 Prerequisites

1. **Railway Account**: [railway.app](https://railway.app)
2. **GitHub Repository**: Push your code to GitHub
3. **Environment Variables**: Prepare your `.env` variables

## 🔧 Environment Variables

Set these in Railway dashboard:

```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
YCLIENTS_PARTNER_TOKEN=your_yclients_partner_token
YCLIENTS_USER_TOKEN=your_yclients_user_token
```

## 🚀 Deployment Steps

### 1. Connect to Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository

### 2. Configure Environment Variables

1. Go to your project dashboard
2. Click on "Variables" tab
3. Add all required environment variables
4. Click "Deploy"

### 3. Monitor Deployment

1. Check the "Deployments" tab
2. Wait for build to complete
3. Check logs for any errors

## 📊 Monitoring

- **Logs**: Available in Railway dashboard
- **Metrics**: CPU, Memory, Network usage
- **Bot Status**: Check logs for "🚀 Starting Telegram Bot..."

## 🛠️ Troubleshooting

### Common Issues:

1. **Build Fails**: Check Dockerfile syntax
2. **Bot Not Responding**: Verify environment variables
3. **Import Errors**: Check requirements.txt

### Debug Commands:

```bash
# Test locally first
python test_local.py

# Check logs
railway logs
```

## 🔄 Updates

To update your bot:

1. Push changes to GitHub
2. Railway will automatically redeploy
3. Monitor deployment status

## 📝 Notes

- **No Web Server**: This is a pure Telegram bot, no HTTP server needed
- **Polling Mode**: Bot uses Telegram polling (no webhook needed)
- **Logs**: Available in Railway dashboard under "Deployments"
- **Scaling**: Railway can auto-scale based on usage

## 🎯 Success Indicators

✅ **Deployment Successful** when you see:
- Build completed without errors
- Logs show "🚀 Starting Telegram Bot..."
- Bot responds to `/start` command
- No import errors in logs

## 🆘 Support

If you encounter issues:
1. Check Railway logs
2. Verify environment variables
3. Test locally first: `python test_local.py`
4. Check Railway documentation
