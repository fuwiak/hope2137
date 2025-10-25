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
PORT=8000
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

## 🔍 Health Check

Your bot will be available at:
- **Health Check**: `https://your-app.railway.app/health`
- **Telegram Bot**: Works via webhook/polling

## 📊 Monitoring

- **Logs**: Available in Railway dashboard
- **Metrics**: CPU, Memory, Network usage
- **Health**: Automatic health checks every 30s

## 🛠️ Troubleshooting

### Common Issues:

1. **Build Fails**: Check Dockerfile syntax
2. **Bot Not Responding**: Verify environment variables
3. **Health Check Fails**: Check Flask app is running

### Debug Commands:

```bash
# Check if bot is running
curl https://your-app.railway.app/health

# Check logs
railway logs
```

## 🔄 Updates

To update your bot:

1. Push changes to GitHub
2. Railway will automatically redeploy
3. Monitor deployment status

## 📝 Notes

- **Port**: Railway sets `PORT` environment variable automatically
- **Health Check**: Required for Railway to know your app is healthy
- **Logs**: Available in Railway dashboard under "Deployments"
- **Scaling**: Railway can auto-scale based on usage

## 🎯 Success Indicators

✅ **Deployment Successful** when you see:
- Build completed without errors
- Health check returns `200 OK`
- Bot responds to `/start` command
- Logs show "Bot started successfully"

## 🆘 Support

If you encounter issues:
1. Check Railway logs
2. Verify environment variables
3. Test locally first
4. Check Railway documentation
