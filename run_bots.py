#!/usr/bin/env python3
"""
Skrypt do uruchamiania botów Telegram i WhatsApp równolegle
"""
import os
import sys
import time
import threading
import logging
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

def run_telegram_bot():
    """Run Telegram bot in separate thread"""
    try:
        log.info("🚀 Starting Telegram Bot...")
        from app import main as telegram_main
        telegram_main()
    except Exception as e:
        log.error(f"❌ Telegram Bot error: {e}")

def run_whatsapp_bot():
    """Run WhatsApp bot in separate thread"""
    try:
        log.info("🚀 Starting WhatsApp Bot...")
        from whatsapp_bot import main as whatsapp_main
        whatsapp_main()
    except Exception as e:
        log.error(f"❌ WhatsApp Bot error: {e}")

def main():
    """Start both bots"""
    log.info("🎯 Starting Multi-Platform Bot System...")
    
    # Check environment variables
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "YCLIENTS_PARTNER_TOKEN", 
        "YCLIENTS_USER_TOKEN",
        "GROQ_API_KEY"
    ]
    
    optional_vars = [
        "GREEN_API_ID",
        "GREEN_API_TOKEN"
    ]
    
    missing_required = [var for var in required_vars if not os.getenv(var)]
    if missing_required:
        log.error(f"❌ Missing required environment variables: {missing_required}")
        sys.exit(1)
    
    missing_optional = [var for var in optional_vars if not os.getenv(var)]
    if missing_optional:
        log.warning(f"⚠️ Missing optional environment variables: {missing_optional}")
        log.warning("⚠️ WhatsApp bot will not start")
    
    # Start Telegram bot
    telegram_thread = threading.Thread(target=run_telegram_bot, name="TelegramBot")
    telegram_thread.daemon = True
    telegram_thread.start()
    
    # Start WhatsApp bot if credentials are available
    whatsapp_thread = None
    if not missing_optional:
        whatsapp_thread = threading.Thread(target=run_whatsapp_bot, name="WhatsAppBot")
        whatsapp_thread.daemon = True
        whatsapp_thread.start()
        log.info("✅ Both bots started successfully!")
    else:
        log.info("✅ Telegram bot started successfully!")
        log.info("ℹ️ WhatsApp bot skipped due to missing credentials")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
            
            # Check if threads are still alive
            if not telegram_thread.is_alive():
                log.error("❌ Telegram bot thread died!")
                break
                
            if whatsapp_thread and not whatsapp_thread.is_alive():
                log.error("❌ WhatsApp bot thread died!")
                break
                
    except KeyboardInterrupt:
        log.info("🛑 Shutting down bots...")
        log.info("✅ Bots stopped successfully!")

if __name__ == "__main__":
    main()
