#!/usr/bin/env python3
"""
Multi-Platform Bot Launcher
Uruchamia równolegle Telegram i WhatsApp boty
"""

import asyncio
import logging
import signal
import sys
import os
from typing import List
import subprocess

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

class MultiPlatformBot:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.running = False
        
    async def start_telegram_bot(self):
        """Start Telegram bot"""
        try:
            log.info("🚀 Starting Telegram Bot...")
            process = subprocess.Popen([
                sys.executable, "app.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.processes.append(process)
            log.info("✅ Telegram Bot started")
            return process
            
        except Exception as e:
            log.error(f"❌ Error starting Telegram Bot: {e}")
            return None
    
    async def start_whatsapp_bot(self):
        """Start WhatsApp bot"""
        try:
            log.info("🚀 Starting WhatsApp Bot...")
            
            # Check if Node.js is available
            try:
                subprocess.run(["node", "--version"], check=True, capture_output=True)
                log.info("✅ Node.js is available")
            except subprocess.CalledProcessError:
                log.error("❌ Node.js not found. Please install Node.js first.")
                log.info("💡 Install Node.js from: https://nodejs.org/")
                return None
            
            # Install dependencies if needed
            try:
                subprocess.run(["npm", "list", "whatsapp-web.js"], check=True, capture_output=True)
                log.info("✅ WhatsApp dependencies are available")
            except subprocess.CalledProcessError:
                log.info("📦 Installing WhatsApp dependencies...")
                subprocess.run(["npm", "install"], check=True)
                log.info("✅ WhatsApp dependencies installed")
            
            # Start WhatsApp bot
            process = subprocess.Popen([
                sys.executable, "whatsapp_bot.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.processes.append(process)
            log.info("✅ WhatsApp Bot started")
            return process
            
        except Exception as e:
            log.error(f"❌ Error starting WhatsApp Bot: {e}")
            return None
    
    async def monitor_processes(self):
        """Monitor all bot processes"""
        while self.running:
            for i, process in enumerate(self.processes):
                if process.poll() is not None:
                    log.error(f"❌ Process {i} died with exit code {process.returncode}")
                    self.running = False
                    break
            
            await asyncio.sleep(1)
    
    def stop_all(self):
        """Stop all bot processes"""
        log.info("🛑 Stopping all bots...")
        self.running = False
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                log.error(f"❌ Error stopping process: {e}")
        
        log.info("✅ All bots stopped")
    
    async def start_all(self):
        """Start all bots"""
        log.info("🚀 Starting Multi-Platform Bot System...")
        self.running = True
        
        # Start Telegram bot
        telegram_process = await self.start_telegram_bot()
        
        # Start WhatsApp bot
        whatsapp_process = await self.start_whatsapp_bot()
        
        if not telegram_process and not whatsapp_process:
            log.error("❌ No bots could be started")
            return
        
        log.info("🎉 Multi-Platform Bot System is running!")
        log.info("📱 Telegram Bot: Active")
        if whatsapp_process:
            log.info("📱 WhatsApp Bot: Active")
        else:
            log.info("📱 WhatsApp Bot: Failed to start")
        
        # Monitor processes
        await self.monitor_processes()

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    log.info(f"🛑 Received signal {signum}, shutting down...")
    sys.exit(0)

async def main():
    """Main function"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    bot_system = MultiPlatformBot()
    
    try:
        await bot_system.start_all()
    except KeyboardInterrupt:
        log.info("🛑 Keyboard interrupt received")
    except Exception as e:
        log.error(f"❌ Unexpected error: {e}")
    finally:
        bot_system.stop_all()

if __name__ == "__main__":
    print("""
🤖 Multi-Platform Bot System
============================

This will start both Telegram and WhatsApp bots simultaneously.

Requirements:
- Python 3.8+
- Node.js 16+
- Telegram Bot Token
- YClients API credentials

Starting bots...
""")
    
    asyncio.run(main())
