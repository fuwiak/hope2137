#!/usr/bin/env python3
"""Test WhatsApp Bot connectivity"""
import os
import time
from dotenv import load_dotenv
from whatsapp_chatbot_python import GreenAPIBot, Notification

load_dotenv()

GREEN_API_ID = os.getenv("GREEN_API_ID")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")

print(f"🔍 Testing WhatsApp Bot...")
print(f"📱 Green API ID: {GREEN_API_ID}")
print(f"🔑 Token: {GREEN_API_TOKEN[:10]}...")

# Initialize bot
bot = GreenAPIBot(GREEN_API_ID, GREEN_API_TOKEN)
print("✅ Bot initialized")

# Test message handler
@bot.router.message()
def test_handler(notification: Notification) -> None:
    print(f"📨 Received message!")
    print(f"📄 Message: {notification.message_text}")
    print(f"👤 From: {notification}")
    print(f"🔍 Attributes: {dir(notification)}")
    
    # Send reply
    bot.api.sending.sendMessage(
        chatId=notification.chat,
        message="✅ Bot działa! Otrzymałem twoją wiadomość."
    )

print("🚀 Starting bot... (Send a message to WhatsApp +7 993 955 4531)")
print("Press Ctrl+C to stop")

try:
    bot.run_forever()
except KeyboardInterrupt:
    print("\n🛑 Bot stopped")

