"""
WhatsApp Bot using Green API
"""
import os
import logging
import requests
from collections import defaultdict
from typing import Dict, List
from dotenv import load_dotenv
from whatsapp_chatbot_python import GreenAPIBot, Notification
from yclients_client import YClientsClient, YClientsError

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# Green API configuration
GREEN_API_ID = os.getenv("GREEN_API_ID")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")

if not GREEN_API_ID or not GREEN_API_TOKEN:
    log.error("❌ GREEN_API_ID or GREEN_API_TOKEN not found in .env file")
    exit(1)

# Initialize WhatsApp bot
bot = GreenAPIBot(GREEN_API_ID, GREEN_API_TOKEN)

# Initialize YClients client
YCLIENTS_PARTNER_TOKEN = os.getenv("YCLIENTS_PARTNER_TOKEN")
YCLIENTS_USER_TOKEN = os.getenv("YCLIENTS_USER_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not YCLIENTS_PARTNER_TOKEN or not YCLIENTS_USER_TOKEN or not GROQ_API_KEY:
    log.error("❌ Missing required environment variables for YClients or Groq API")
    exit(1)

yclients = YClientsClient(YCLIENTS_PARTNER_TOKEN, YCLIENTS_USER_TOKEN)

# Configuration
BASE = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-120b"
MEMORY_TURNS = 6

# Global storage for user data
UserMemory: Dict[str, List[tuple]] = defaultdict(list)
UserPhone: Dict[str, str] = {}
UserRecords: Dict[str, List[Dict]] = defaultdict(list)
UserAuth: Dict[str, Dict] = defaultdict(dict)

# Booking keywords for NLP
BOOKING_KEYWORDS = [
    "запись", "записаться", "записать", "забронировать",
    "услуга", "мастер", "время", "дата",
    "когда можно", "свободное время", "расписание",
    "записаться на", "хочу записаться", "нужна запись",
    "маникюр", "педикюр", "массаж",  # nazwy usług
    "арина", "екатерина", "полина", "катя", "катюша",  # imiona masterów
    "октября", "ноября", "декабря", "января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября",  # miesiące
    ":", "часов", "в ", "на "  # czas
]

BOOKING_PROMPT = """
Ты помощник по записи к мастерам. Анализируй ВСЮ историю разговора и определи:
1. Какая услуга нужна
2. Есть ли предпочтения по мастеру  
3. Желаемая дата и время

История разговора:
{{history}}

Доступные данные (ТОЧНЫЕ ДАННЫЕ ИЗ API):
{{api_data}}

Сообщение пользователя: {{message}}

КРИТИЧЕСКИ ВАЖНО: 
- Используй ТОЛЬКО услуги и мастеров из "Доступные данные" выше
- НЕ ВЫДУМЫВАЙ услуги - используй только те что есть в списке
- НЕ ИСПОЛЬЗУЙ форматирование ** - только обычный текст
- НЕ ПРИДУМЫВАЙ цены - используй только те что указаны в API
- Если в истории есть информация об услуге, мастере и времени - СОЗДАЙ ЗАПИСЬ
- Если пользователь повторно пишет "хочу записаться" - проверь историю на наличие всех данных
- Если есть все данные (услуга, мастер, дата и время) - ответь в формате:
ЗАПИСЬ: [услуга] | [мастер] | [дата время]

Например: ЗАПИСЬ: Маникюр с покрытием гель-лак | Арина | 2025-10-26 12:00

Если данных недостаточно, уточни недостающую информацию.
"""

CHAT_PROMPT = """
Ты дружелюбный помощник на русском.
История чата:
{{history}}

Сообщение:
{{message}}
Ответь кратко по делу.
"""

def get_company_id():
    """Get the first available company ID"""
    log.info("🏢 API CALL: Getting companies from YClients...")
    try:
        companies = yclients.my_companies()
        log.info(f"🏢 API RESPONSE: {companies}")
        if companies.get("data") and len(companies["data"]) > 0:
            company_id = companies["data"][0]["id"]
            log.info(f"✅ Company ID found: {company_id}")
            return company_id
        log.warning("⚠️ No companies found in response")
        return None
    except YClientsError as e:
        log.error(f"❌ YClients API Error getting company: {e}")
        return None

def get_services_data():
    """Get services data from YClients API"""
    try:
        company_id = get_company_id()
        if not company_id:
            return "Ошибка получения данных компании"
        
        # Get services using the same method as Telegram bot
        services_response = yclients.company_services(company_id)
        services_data = services_response.get("data", [])
        
        # Get masters using the same method as Telegram bot
        masters_response = yclients.company_staff(company_id)
        masters_data = masters_response.get("data", [])
        
        services_text = "Доступные услуги:\n"
        for service in services_data:
            title = service.get('title', 'Без названия')
            price_min = service.get('price_min', 0)
            price_max = service.get('price_max', 0)
            if price_min == price_max:
                services_text += f"- {title} ({price_min} руб.)\n"
            else:
                services_text += f"- {title} ({price_min}-{price_max} руб.)\n"
        
        masters_text = "\nДоступные мастера:\n"
        for master in masters_data:
            name = master.get('name', 'Без имени')
            masters_text += f"- {name}\n"
        
        return services_text + masters_text
    except Exception as e:
        log.error(f"Error getting services data: {e}")
        return "Ошибка получения данных услуг"

def add_memory(user_id: str, role: str, content: str):
        """Add message to user memory"""
        UserMemory[user_id].append((role, content))
    
    # Keep only last MEMORY_TURNS conversations
        if len(UserMemory[user_id]) > MEMORY_TURNS * 2:
            UserMemory[user_id] = UserMemory[user_id][-MEMORY_TURNS * 2:]

def get_memory_history(user_id: str) -> str:
    """Get conversation history for user"""
    history = UserMemory.get(user_id, [])
    return "\n".join([f"{role}: {content}" for role, content in history])

def call_groq_api(prompt: str, user_id: str) -> str:
    """Call Groq API for AI response"""
    try:
        history = get_memory_history(user_id)
        api_data = get_services_data()
        
        # Replace placeholders in prompt
        formatted_prompt = prompt.replace("{{history}}", history).replace("{{api_data}}", api_data)
        
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "user", "content": formatted_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(BASE, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
        
    except Exception as e:
        log.error(f"Error calling Groq API: {e}")
        return "Извините, произошла ошибка при обработке запроса."

def is_booking_request(text: str) -> bool:
    """Check if message contains booking keywords"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in BOOKING_KEYWORDS)

def parse_booking_data(text: str) -> Dict:
    """Parse booking data from text"""
    # Simple parsing logic - can be enhanced
    parsed = {}
    
    # Look for service names
    services_data = get_services_data()
    for line in services_data.split('\n'):
        if line.startswith('- ') and 'руб' in line:
            service_name = line.split(' (')[0].replace('- ', '')
            if service_name.lower() in text.lower():
                parsed['service'] = service_name
            break
    
    # Look for master names
    masters_data = get_services_data()
    for line in masters_data.split('\n'):
        if line.startswith('- ') and 'руб' not in line:
            master_name = line.replace('- ', '')
            if master_name.lower() in text.lower():
                parsed['master'] = master_name
            break
    
    # Look for date/time patterns
    import re
    date_patterns = [
        r'(\d{1,2}):(\d{2})',  # HH:MM
        r'(\d{1,2})\s+(октября|ноября|декабря|января|февраля|марта|апреля|мая|июня|июля|августа|сентября)',
        r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            parsed['datetime'] = match.group(0)
            break
    
    return parsed

def create_booking(user_id: str, parsed_data: Dict) -> str:
    """Create booking using YClients API"""
    try:
        company_id = get_company_id()
        if not company_id:
            return "Ошибка: не удалось получить ID компании"
        
        # Use user_id as phone (it's already the phone number from WhatsApp)
        user_phone = user_id
        
        # Create booking data
        booking_data = {
            "client": {
                "name": f"WhatsApp User {user_id[:8]}",
                "phone": user_phone
            },
            "services": [],
            "datetime": parsed_data.get('datetime', ''),
            "comment": f"Запись через WhatsApp бота"
        }
        
        # Add service if found
        if 'service' in parsed_data:
            services = yclients.get_services(company_id)
            for service in services:
                if service['title'] == parsed_data['service']:
                    booking_data["services"].append({
                        "id": service['id'],
                        "price": service['price_min']
                    })
                    break
        
        # Create booking
        result = yclients.create_booking(company_id, booking_data)
        
        if result:
            return f"✅ Запись успешно создана!\nУслуга: {parsed_data.get('service', 'Не указана')}\nМастер: {parsed_data.get('master', 'Любой доступный')}\nВремя: {parsed_data.get('datetime', 'Не указано')}"
        else:
            return "❌ Не удалось создать запись. Попробуйте позже."
        
    except Exception as e:
        log.error(f"Error creating booking: {e}")
        return "❌ Произошла ошибка при создании записи."

@bot.router.message()
def message_handler(notification: Notification) -> None:
    """Handle incoming WhatsApp messages"""
    try:
        text = notification.message_text
        
        # Debug: print all available attributes
        log.info(f"🔍 Notification attributes: {dir(notification)}")
        
        # Try different attributes to get sender info
        user_id = getattr(notification, 'sender_id', None) or getattr(notification, 'sender_phone', None) or getattr(notification, 'sender', None) or 'unknown'
        
        log.info(f"📱 WhatsApp message from {user_id}: {text}")
        
        add_memory(user_id, "user", text)
        
        # Check if it's a booking request
        if is_booking_request(text):
            # Use booking prompt
            response = call_groq_api(BOOKING_PROMPT, user_id)
            
            # Check if response contains booking data
            if "ЗАПИСЬ:" in response:
                # Parse booking data
                booking_line = response.split("ЗАПИСЬ:")[1].strip()
                parts = booking_line.split(" | ")
                
                if len(parts) >= 3:
                    parsed_data = {
                        'service': parts[0].strip(),
                        'master': parts[1].strip(),
                        'datetime': parts[2].strip()
                    }
                    
                    # Create booking
                    booking_result = create_booking(user_id, parsed_data)
                    response = booking_result
                else:
                    response = "Не удалось распознать данные для записи. Попробуйте еще раз."
        else:
            # Use chat prompt
            response = call_groq_api(CHAT_PROMPT, user_id)
        
        add_memory(user_id, "assistant", response)
        
        # Send response
        notification.answer(response)
        
    except Exception as e:
        log.error(f"❌ Error handling WhatsApp message: {e}")
        notification.answer("❌ Произошла ошибка. Попробуйте позже.")

def main():
    """Start WhatsApp bot"""
    log.info("🚀 Starting WhatsApp Bot...")
    log.info(f"🔍 Green API ID: {GREEN_API_ID[:10]}...")
    
    try:
        bot.run_forever()
    except KeyboardInterrupt:
        log.info("🛑 WhatsApp Bot stopped by user")
    except Exception as e:
        log.error(f"❌ WhatsApp Bot error: {e}")

if __name__ == "__main__":
    main()
