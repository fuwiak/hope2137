#!/usr/bin/env python3
"""
WhatsApp Bot - równoległy do Telegram bota
Używa whatsapp-web.js przez Node.js bridge
"""

import os
import sys
import json
import logging
import asyncio
import subprocess
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# Import funkcji z głównego bota
from app import (
    get_company_id, get_services_with_prices, get_masters, 
    get_master_services_text, parse_booking_message,
    create_booking_from_parsed_data, UserPhone, UserMemory,
    add_memory, get_recent_history, groq_chat, BOOKING_PROMPT,
    CHAT_PROMPT, is_booking
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class WhatsAppBot:
    def __init__(self):
        self.process = None
        self.is_running = False
        
    async def start(self):
        """Start WhatsApp bot"""
        try:
            log.info("🚀 Starting WhatsApp Bot...")
            
            # Sprawdź czy Node.js jest zainstalowany
            try:
                subprocess.run(["node", "--version"], check=True, capture_output=True)
                log.info("✅ Node.js is available")
            except subprocess.CalledProcessError:
                log.error("❌ Node.js not found. Please install Node.js first.")
                return False
            
            # Sprawdź czy whatsapp-web.js jest zainstalowany
            try:
                subprocess.run(["npm", "list", "whatsapp-web.js"], check=True, capture_output=True)
                log.info("✅ whatsapp-web.js is available")
            except subprocess.CalledProcessError:
                log.info("📦 Installing whatsapp-web.js...")
                subprocess.run(["npm", "install", "whatsapp-web.js"], check=True)
                log.info("✅ whatsapp-web.js installed")
            
            # Start Node.js bridge
            self.process = subprocess.Popen([
                "node", "whatsapp_bridge.js"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.is_running = True
            log.info("✅ WhatsApp Bot started successfully!")
            
            # Monitor process
            await self.monitor_process()
            
        except Exception as e:
            log.error(f"❌ Error starting WhatsApp Bot: {e}")
            return False
    
    async def monitor_process(self):
        """Monitor Node.js process"""
        while self.is_running:
            if self.process.poll() is not None:
                log.error("❌ WhatsApp Bot process died")
                self.is_running = False
                break
            
            # Read output
            try:
                line = self.process.stdout.readline()
                if line:
                    await self.handle_message(line.strip())
            except Exception as e:
                log.error(f"❌ Error reading process output: {e}")
            
            await asyncio.sleep(0.1)
    
    async def handle_message(self, message_data: str):
        """Handle incoming WhatsApp message"""
        try:
            if not message_data:
                return
                
            data = json.loads(message_data)
            
            if data.get("type") == "message":
                await self.process_message(data)
            elif data.get("type") == "qr":
                log.info(f"📱 WhatsApp QR Code: {data.get('qr')}")
                log.info("📱 Please scan QR code with WhatsApp to connect")
                
        except json.JSONDecodeError:
            log.debug(f"Non-JSON output: {message_data}")
        except Exception as e:
            log.error(f"❌ Error handling message: {e}")
    
    async def process_message(self, data: Dict[str, Any]):
        """Process incoming WhatsApp message"""
        try:
            message = data.get("message", "")
            sender = data.get("sender", "")
            chat_id = data.get("chatId", "")
            
            log.info(f"📨 WhatsApp message from {sender}: {message}")
            
            # Use same logic as Telegram bot
            response = await self.generate_response(message, sender)
            
            # Send response back
            await self.send_message(chat_id, response)
            
        except Exception as e:
            log.error(f"❌ Error processing message: {e}")
    
    async def generate_response(self, text: str, user_id: str) -> str:
        """Generate response using same logic as Telegram bot"""
        try:
            # Add to memory
            add_memory(user_id, "user", text)
            
            # Check for special commands
            if text.lower() in ["создать тестовую запись", "тест запись", "добавить запись"]:
                from app import create_test_record
                test_record = create_test_record(user_id)
                response = (
                    f"✅ *Создана тестовая запись!*\n\n"
                    f"📅 *Дата:* {test_record['date']}\n"
                    f"⏰ *Время:* {test_record['datetime']}\n"
                    f"👤 *Мастер:* {test_record['staff']['name']}\n"
                    f"🛍 *Услуга:* {test_record['services'][0]['title']}\n\n"
                    f"Используйте команду 'мои записи' для просмотра!"
                )
                add_memory(user_id, "assistant", response)
                return response
            
            # Check if phone number
            if text.startswith("+") and len(text) >= 10:
                UserPhone[user_id] = text
                response = (
                    f"✅ *Номер телефона {text} сохранен!*\n\n"
                    f"Теперь вы можете создавать записи.\n"
                    f"Напишите `хочу записаться` для начала."
                )
                add_memory(user_id, "assistant", response)
                return response
            
            # Check if booking message
            if is_booking(text):
                log.info(f"🎯 BOOKING DETECTED: '{text}'")
                history = get_recent_history(user_id, 50)
                parsed_data = parse_booking_message(text, history)
                
                if parsed_data["has_all_info"]:
                    try:
                        user_phone = UserPhone.get(user_id)
                        if not user_phone:
                            response = (
                                "📱 *Для создания записи нужен ваш номер телефона*\n\n"
                                "Пожалуйста, отправьте номер в формате:\n"
                                "`+7XXXXXXXXXX`"
                            )
                            add_memory(user_id, "assistant", response)
                            return response
                        
                        # Create booking
                        booking_record = create_booking_from_parsed_data(
                            user_id,
                            parsed_data,
                            client_name="WhatsApp User",
                            client_phone=user_phone
                        )
                        
                        response = f"🎉 *Запись успешно создана в системе!* 🎉\n\n"
                        response += f"📅 *Услуга:* {parsed_data['service']}\n"
                        response += f"👤 *Мастер:* {parsed_data['master']}\n"
                        response += f"⏰ *Время:* {parsed_data['datetime']}\n\n"
                        response += "Спасибо за запись! Ждем вас в салоне! ✨"
                        
                    except Exception as e:
                        log.error(f"Error creating booking: {e}")
                        if "недоступно" in str(e) or "conflict" in str(e).lower():
                            response = f"❌ *Время {parsed_data['datetime']} недоступно*\n\n"
                            response += f"💡 *Предлагаем альтернативные варианты:*\n"
                            response += f"• {parsed_data['service']} у {parsed_data['master']}\n"
                            response += f"• Завтра в 14:00\n"
                            response += f"• Завтра в 15:00\n"
                            response += f"• Завтра в 17:00\n\n"
                            response += f"Напишите желаемое время, например: `завтра 14:00`"
                        else:
                            response = f"❌ *Ошибка при создании записи:* {str(e)}"
                else:
                    # Check for master mention
                    masters = get_masters()
                    master_names = [m.get("name", "").lower() for m in masters]
                    
                    mentioned_master = None
                    for master_name in master_names:
                        if master_name in text.lower():
                            mentioned_master = master_name
                            break
                    
                    if mentioned_master:
                        master_display_name = next((m.get("name") for m in masters if m.get("name", "").lower() == mentioned_master), mentioned_master)
                        response = get_master_services_text(master_display_name)
                        log.info(f"🎯 DETERMINISTIC RESPONSE for {master_display_name}")
                    else:
                        # Use AI
                        api_data = self.get_api_data_for_ai()
                        msg = BOOKING_PROMPT.replace("{{api_data}}", api_data).replace("{{message}}", text).replace("{{history}}", history)
                        response = groq_chat([{"role": "user", "content": msg}])
                        log.info(f"🤖 AI RESPONSE: {response}")
            else:
                # Regular chat
                msg = CHAT_PROMPT.replace("{{history}}", get_recent_history(user_id)).replace("{{message}}", text)
                response = groq_chat([{"role": "user", "content": msg}])
            
            add_memory(user_id, "assistant", response)
            return response
            
        except Exception as e:
            log.error(f"❌ Error generating response: {e}")
            return "❌ Произошла ошибка. Попробуйте позже."
    
    def get_api_data_for_ai(self) -> str:
        """Get API data for AI (same as Telegram bot)"""
        try:
            company_id = get_company_id()
            if not company_id:
                return "Данные недоступны"
                
            services = get_services_with_prices(company_id)
            masters = get_masters()
            
            data_text = "Доступные услуги (ТОЧНЫЕ ДАННЫЕ ИЗ API):\n"
            for service in services:
                name = service.get("title", "Без названия")
                cost = service.get("cost", 0)
                price_min = service.get("price_min", 0)
                price_max = service.get("price_max", 0)
                duration = service.get("length", 0)
                
                data_text += f"- {name}"
                
                if cost > 0:
                    data_text += f" ({cost} руб.)"
                elif price_min > 0 and price_max > 0:
                    if price_min == price_max:
                        data_text += f" ({price_min} руб.)"
                    else:
                        data_text += f" ({price_min}-{price_max} руб.)"
                elif price_min > 0:
                    data_text += f" (от {price_min} руб.)"
                    
                if duration > 0:
                    data_text += f" ({duration} мин)"
                data_text += "\n"
            
            data_text += "\nДоступные мастера (ТОЧНЫЕ ДАННЫЕ ИЗ API):\n"
            for master in masters:
                name = master.get("name", "Без имени")
                specialization = master.get("specialization", "")
                staff_id = master.get("id")
                
                data_text += f"- {name}"
                if specialization:
                    data_text += f" ({specialization})"
                
                if staff_id:
                    master_services = self.get_services_for_master(company_id, staff_id)
                    if master_services:
                        data_text += f" - услуги: "
                        service_names = []
                        for service in master_services:
                            service_name = service.get("title", "")
                            cost = service.get("cost", 0)
                            price_min = service.get("price_min", 0)
                            price_max = service.get("price_max", 0)
                            
                            if service_name:
                                if cost > 0:
                                    service_names.append(f"{service_name} ({cost}₽)")
                                elif price_min > 0 and price_max > 0:
                                    if price_min == price_max:
                                        service_names.append(f"{service_name} ({price_min}₽)")
                                    else:
                                        service_names.append(f"{service_name} ({price_min}-{price_max}₽)")
                                elif price_min > 0:
                                    service_names.append(f"{service_name} (от {price_min}₽)")
                                else:
                                    service_names.append(service_name)
                        data_text += ", ".join(service_names)
                
                data_text += "\n"
            
            return data_text
        except Exception as e:
            log.error(f"Error getting API data: {e}")
            return "Данные временно недоступны"
    
    def get_services_for_master(self, company_id: int, staff_id: int) -> List[Dict]:
        """Get services for master (same as Telegram bot)"""
        from app import get_services_for_master
        return get_services_for_master(company_id, staff_id)
    
    async def send_message(self, chat_id: str, message: str):
        """Send message via Node.js bridge"""
        try:
            if self.process and self.process.stdin:
                data = {
                    "type": "send",
                    "chatId": chat_id,
                    "message": message
                }
                self.process.stdin.write(json.dumps(data) + "\n")
                self.process.stdin.flush()
                log.info(f"📤 Sent WhatsApp message to {chat_id}")
        except Exception as e:
            log.error(f"❌ Error sending message: {e}")
    
    def stop(self):
        """Stop WhatsApp bot"""
        if self.process:
            self.process.terminate()
            self.is_running = False
            log.info("🛑 WhatsApp Bot stopped")

async def main():
    """Main function"""
    bot = WhatsAppBot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        log.info("🛑 Stopping WhatsApp Bot...")
        bot.stop()
    except Exception as e:
        log.error(f"❌ Unexpected error: {e}")
        bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
