# bot.py
import os
import re
import time
import logging
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from typing import Dict, Deque, List, Tuple

import requests
from dotenv import load_dotenv
from telegram import Update, Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from yclients_client import YClientsClient, YClientsError

# ===================== LOAD .ENV ======================
load_dotenv()  # <-- loads variables from .env file

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
YCLIENTS_PARTNER_TOKEN = os.getenv("YCLIENTS_PARTNER_TOKEN")
YCLIENTS_USER_TOKEN = os.getenv("YCLIENTS_USER_TOKEN")

# ===================== VALIDATION =====================
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Error: Missing TELEGRAM_BOT_TOKEN in .env")
if not GROQ_API_KEY:
    raise ValueError("Error: Missing GROQ_API_KEY in .env")
if not YCLIENTS_PARTNER_TOKEN:
    raise ValueError("Error: Missing YCLIENTS_PARTNER_TOKEN in .env")
if not YCLIENTS_USER_TOKEN:
    raise ValueError("Error: Missing YCLIENTS_USER_TOKEN in .env")

# ===================== CONFIG =========================
BASE = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-120b"
MEMORY_TURNS = 6

# Initialize YClients client
yclients = YClientsClient(YCLIENTS_PARTNER_TOKEN, YCLIENTS_USER_TOKEN)

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

Доступные данные:
{{api_data}}

Сообщение пользователя: {{message}}

КРИТИЧЕСКИ ВАЖНО: 
- Если в истории есть информация об услуге, мастере и времени - СОЗДАЙ ЗАПИСЬ
- Если пользователь повторно пишет "хочу записаться" - проверь историю на наличие всех данных
- Если есть все данные (услуга, мастер, дата и время) - ответь в формате:
ЗАПИСЬ: [услуга] | [мастер] | [дата время]

Например: ЗАПИСЬ: маникюр | Арина | 2025-10-26 12:00

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

# ===================== LOGGING ========================
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger()

# ===================== MEMORY =========================
UserMemory: Dict[int, Deque] = defaultdict(lambda: deque(maxlen=MEMORY_TURNS * 2))
UserRecords: Dict[int, List[Dict]] = defaultdict(list)  # Хранилище записей пользователей
UserAuth: Dict[int, Dict] = defaultdict(dict)  # Данные авторизации пользователей
UserPhone: Dict[int, str] = {}  # Номера телефонов пользователей

def add_memory(user_id, role, text):
    UserMemory[user_id].append((role, text))

def get_history(user_id):
    return "\n".join([f"{r}: {t}" for r, t in UserMemory[user_id]])

# ===================== NLP ============================
def is_booking(text):
    text_lower = text.lower()
    matches = [k for k in BOOKING_KEYWORDS if k in text_lower]
    log.info(f"🔍 BOOKING CHECK: '{text}' -> matches: {matches}")
    return len(matches) > 0

def groq_chat(messages):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 500,
        "temperature": 0.4
    }
    r = requests.post(BASE, json=data, headers=headers)
    return r.json()["choices"][0]["message"]["content"]

# ===================== YCLIENTS INTEGRATION ===========
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
    except Exception as e:
        log.error(f"❌ General Error getting company: {e}")
        return None

def get_services():
    """Get available services"""
    log.info("📋 API CALL: Getting services from YClients...")
    try:
        company_id = get_company_id()
        if not company_id:
            log.warning("⚠️ No company ID, cannot get services")
            return []
        log.info(f"📋 Getting services for company ID: {company_id}")
        services = yclients.company_services(company_id)
        log.info(f"📋 API RESPONSE: {services}")
        services_data = services.get("data", [])
        log.info(f"✅ Found {len(services_data)} services")
        return services_data
    except YClientsError as e:
        log.error(f"❌ YClients API Error getting services: {e}")
        return []
    except Exception as e:
        log.error(f"❌ General Error getting services: {e}")
        return []

def get_masters():
    """Get available masters"""
    log.info("👥 API CALL: Getting masters from YClients...")
    try:
        company_id = get_company_id()
        if not company_id:
            log.warning("⚠️ No company ID, cannot get masters")
            return []
        log.info(f"👥 Getting masters for company ID: {company_id}")
        masters = yclients.company_masters(company_id)
        log.info(f"👥 API RESPONSE: {masters}")
        masters_data = masters.get("data", [])
        log.info(f"✅ Found {len(masters_data)} masters")
        return masters_data
    except YClientsError as e:
        log.error(f"❌ YClients API Error getting masters: {e}")
        return []
    except Exception as e:
        log.error(f"❌ General Error getting masters: {e}")
        return []

def get_api_data_for_ai():
    """Get formatted API data for AI responses"""
    try:
        services = get_services()
        masters = get_masters()
        
        data_text = "Доступные услуги:\n"
        for service in services[:5]:  # Показываем первые 5 услуг
            name = service.get("title", "Без названия")
            price = service.get("price_min", 0)
            duration = service.get("length", 0)
            data_text += f"- {name}"
            if price > 0:
                data_text += f" (от {price} руб.)"
            if duration > 0:
                data_text += f" ({duration} мин)"
            data_text += "\n"
        
        data_text += "\nДоступные мастера:\n"
        for master in masters[:5]:  # Показываем первых 5 мастеров
            name = master.get("name", "Без имени")
            specialization = master.get("specialization", "")
            data_text += f"- {name}"
            if specialization:
                data_text += f" ({specialization})"
            data_text += "\n"
        
        return data_text
    except Exception as e:
        log.error(f"Error getting API data: {e}")
        return "Данные временно недоступны"

# ===================== NLP PARSING ==================
def init_fuzzy_matcher():
    """Инициализация нечеткого поиска"""
    try:
        from fuzzywuzzy import fuzz, process
        return True
    except ImportError:
        log.warning("fuzzywuzzy not available, using basic parsing")
        return False

# Глобальный флаг доступности fuzzywuzzy
fuzzy_available = init_fuzzy_matcher()

def find_best_match(word: str, choices: list, threshold: int = 80) -> str:
    """Находит лучшее совпадение с помощью нечеткого поиска"""
    if not fuzzy_available:
        return None
    
    try:
        from fuzzywuzzy import process
        result = process.extractOne(word, choices, scorer=fuzz.ratio)
        if result and result[1] >= threshold:
            return result[0]
    except Exception as e:
        log.debug(f"Error in fuzzy matching '{word}': {e}")
    
    return None

def find_service_advanced(message: str) -> str:
    """Продвинутый поиск услуги с regex и нечетким поиском"""
    message_lower = message.lower()
    
    # Расширенные варианты услуг с regex паттернами
    service_patterns = {
        "маникюр": [
            r'\bманикюр\w*\b',  # маникюр, маникюра, маникюру, маникюром, маникюре
            r'\bманикюрн\w*\b',  # маникюрный, маникюрная, маникюрное
            r'\bманик\w*\b',     # маник, маника (сокращения)
        ],
        "педикюр": [
            r'\bпедикюр\w*\b',  # педикюр, педикюра, педикюру, педикюром, педикюре
            r'\bпедикюрн\w*\b',  # педикюрный, педикюрная, педикюрное
            r'\bпедик\w*\b',     # педик, педика (сокращения)
        ],
        "массаж": [
            r'\bмассаж\w*\b',   # массаж, массажа, массажу, массажем, массаже
            r'\bмассажн\w*\b',   # массажный, массажная, массажное
            r'\bмасаж\w*\b',     # масаж, масажа (опечатки)
            r'\bмас\w*ж\w*\b',   # мас*ж (опечатки)
        ]
    }
    
    # Ищем по regex паттернам
    for service, patterns in service_patterns.items():
        for pattern in patterns:
            if re.search(pattern, message_lower):
                return service
    
    # Fallback к нечеткому поиску
    service_variants = {
        "маникюр": ["маникюр", "маникюра", "маникюру", "маникюром", "маникюре", "маникюрный", "маникюрная", "маник", "маника"],
        "педикюр": ["педикюр", "педикюра", "педикюру", "педикюром", "педикюре", "педикюрный", "педикюрная", "педик", "педика"],
        "массаж": ["массаж", "массажа", "массажу", "массажем", "массаже", "масаж", "масажа", "массажный", "массажная"]
    }
    
    # Нечеткий поиск по словам
    words = message_lower.split()
    for word in words:
        all_variants = []
        for variants in service_variants.values():
            all_variants.extend(variants)
        
        best_match = find_best_match(word, all_variants, threshold=70)
        if best_match:
            for service, variants in service_variants.items():
                if best_match in variants:
                    return service
    
    return None

def find_master_advanced(message: str) -> str:
    """Продвинутый поиск мастера с regex и нечетким поиском"""
    message_lower = message.lower()
    
    # Regex паттерны для имен мастеров
    master_patterns = {
        "арина": [
            r'\bарин\w*\b',      # арина, арины, арине, арину, ариной
            r'\bаринк\w*\b',     # аринка, ариночка
        ],
        "екатерина": [
            r'\bекатерин\w*\b',  # екатерина, екатерины, екатерине, екатерину, екатериной
            r'\bкат\w*\b',       # катя, кати, кате, катю, катей, катенька
            r'\bкатюш\w*\b',     # катюша, катюши, катюше, катюшу, катюшей, катюшка
        ],
        "полина": [
            r'\bполин\w*\b',     # полина, полины, полине, полину, полиной
            r'\bполинк\w*\b',    # полинка, полиночка
        ]
    }
    
    # Ищем по regex паттернам
    for master, patterns in master_patterns.items():
        for pattern in patterns:
            if re.search(pattern, message_lower):
                return master.title()
    
    # Fallback к нечеткому поиску
    master_variants = {
        "арина": ["арина", "арины", "арине", "арину", "ариной", "аринка", "ариночка"],
        "екатерина": ["екатерина", "екатерины", "екатерине", "екатерину", "екатериной", "катя", "кати", "кате", "катю", "катей", "катюша", "катюши", "катюше", "катюшу", "катюшей", "катенька", "катюшка"],
        "полина": ["полина", "полины", "полине", "полину", "полиной", "полинка", "полиночка"]
    }
    
    # Нечеткий поиск по словам
    words = message_lower.split()
    for word in words:
        all_variants = []
        for variants in master_variants.values():
            all_variants.extend(variants)
        
        best_match = find_best_match(word, all_variants, threshold=75)
        if best_match:
            for master, variants in master_variants.items():
                if best_match in variants:
                    return master.title()
    
    return None

def parse_booking_message(message: str, history: str) -> Dict:
    """Парсит сообщение пользователя и извлекает информацию о записи"""
    import re
    from datetime import datetime, timedelta
    
    result = {
        "service": None,
        "master": None,
        "datetime": None,
        "has_all_info": False
    }
    
    # Список услуг для поиска
    services = [
        "маникюр с покрытием гель-лак", "маникюр", "педикюр с покрытием гель-лак", 
        "педикюр", "массаж оздоровительный", "массаж", "маникюр в 4 руки", 
        "педикюр в 4 руки"
    ]
    
    # Список мастеров
    masters = ["арина", "екатерина", "полина", "катя", "катюша"]
    
    message_lower = message.lower()
    
    # Используем продвинутый поиск услуг
    result["service"] = find_service_advanced(message)
    
    # Используем продвинутый поиск мастеров
    result["master"] = find_master_advanced(message)
    
    # Fallback к старому методу если не найдено
    if not result["service"]:
        for service in services:
            if service.lower() in message_lower:
                result["service"] = service
                break
    
    if not result["master"]:
        for master in masters:
            if master in message_lower:
                # Преобразуем обратно в правильное имя
                if master in ["арина"]:
                    result["master"] = "Арина"
                elif master in ["екатерина", "катя", "катюша"]:
                    result["master"] = "Екатерина"
                elif master in ["полина"]:
                    result["master"] = "Полина"
                break
    
    # Ищем дату и время
    # Паттерны для поиска времени
    time_patterns = [
        r'(\d{1,2}):(\d{2})',  # 12:00, 9:30
        r'(\d{1,2})\s*часов',  # 12 часов
        r'в\s*(\d{1,2}):(\d{2})',  # в 12:00
        r'на\s*(\d{1,2}):(\d{2})',  # на 12:00
    ]
    
    # Расширенные паттерны для поиска даты
    date_patterns = [
        # Точные даты с месяцами
        r'(\d{1,2})\s*октября',  # 26 октября
        r'(\d{1,2})\s*ноября',   # 26 ноября
        r'(\d{1,2})\s*декабря',  # 26 декабря
        r'(\d{1,2})\s*января',   # 26 января
        r'(\d{1,2})\s*февраля',  # 26 февраля
        r'(\d{1,2})\s*марта',    # 26 марта
        r'(\d{1,2})\s*апреля',   # 26 апреля
        r'(\d{1,2})\s*мая',      # 26 мая
        r'(\d{1,2})\s*июня',     # 26 июня
        r'(\d{1,2})\s*июля',     # 26 июля
        r'(\d{1,2})\s*августа',  # 26 августа
        r'(\d{1,2})\s*сентября', # 26 сентября
        
        # Относительные даты
        r'\bзавтра\b',           # завтра
        r'\bпослезавтра\b',      # послезавтра
        r'\bсегодня\b',          # сегодня
        
        # Даты в формате DD.MM или DD/MM
        r'(\d{1,2})[./](\d{1,2})',  # 26.10 или 26/10
        
        # Даты с годами
        r'(\d{1,2})[./](\d{1,2})[./](\d{4})',  # 26.10.2025
    ]
    
    # Ищем время
    time_match = None
    for pattern in time_patterns:
        match = re.search(pattern, message_lower)
        if match:
            if len(match.groups()) == 2:
                hour, minute = match.groups()
                time_match = f"{hour.zfill(2)}:{minute.zfill(2)}"
            else:
                hour = match.group(1)
                time_match = f"{hour.zfill(2)}:00"
            break
    
    # Ищем дату
    date_match = None
    month_map = {
        'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
        'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
        'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
    }
    
    for pattern in date_patterns:
        match = re.search(pattern, message_lower)
        if match:
            if pattern == r'\bзавтра\b':
                # Завтра
                tomorrow = datetime.now() + timedelta(days=1)
                date_match = tomorrow.strftime("%Y-%m-%d")
            elif pattern == r'\bпослезавтра\b':
                # Послезавтра
                day_after_tomorrow = datetime.now() + timedelta(days=2)
                date_match = day_after_tomorrow.strftime("%Y-%m-%d")
            elif pattern == r'\bсегодня\b':
                # Сегодня
                today = datetime.now()
                date_match = today.strftime("%Y-%m-%d")
            elif pattern == r'(\d{1,2})[./](\d{1,2})[./](\d{4})':
                # DD.MM.YYYY или DD/MM/YYYY
                day, month, year = match.groups()
                date_match = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            elif pattern == r'(\d{1,2})[./](\d{1,2})':
                # DD.MM или DD/MM (текущий год)
                day, month = match.groups()
                current_year = datetime.now().year
                date_match = f"{current_year}-{month.zfill(2)}-{day.zfill(2)}"
            else:
                # Месяцы по названию
                day = match.group(1)
                month_name = pattern.split(r'\s*')[1].replace(')', '')
                month = month_map.get(month_name, '10')  # По умолчанию октябрь
                current_year = datetime.now().year
                date_match = f"{current_year}-{month}-{day.zfill(2)}"
            break
    
    # Если нашли и время и дату, формируем datetime
    if time_match and date_match:
        result["datetime"] = f"{date_match} {time_match}"
    
    # Проверяем, есть ли все данные
    result["has_all_info"] = all([result["service"], result["master"], result["datetime"]])
    
    return result

def get_recent_history(user_id: int, limit: int = 50) -> str:
    """Получает последние N сообщений из истории"""
    if user_id not in UserMemory:
        return ""
    
    messages = UserMemory[user_id]
    recent_messages = messages[-limit:] if len(messages) > limit else messages
    
    history_text = ""
    for msg in recent_messages:
        # msg is a tuple (role, text)
        if isinstance(msg, tuple) and len(msg) == 2:
            role, content = msg
            history_text += f"{role}: {content}\n"
        else:
            # Fallback for dictionary format
            role = msg.get("role", "user") if isinstance(msg, dict) else "user"
            content = msg.get("content", "") if isinstance(msg, dict) else str(msg)
            history_text += f"{role}: {content}\n"
    
    return history_text

def create_booking_from_parsed_data(user_id: int, parsed_data: Dict, client_name: str = "", client_phone: str = "") -> Dict:
    """Создает запись на основе распарсенных данных"""
    try:
        log.info(f"🔍 PARSED DATA: {parsed_data}")
        
        if not parsed_data["has_all_info"]:
            raise Exception("Недостаточно данных для создания записи")
        
        # Создаем реальную запись
        booking_record = create_real_booking(
            user_id,
            parsed_data["service"],
            parsed_data["master"],
            parsed_data["datetime"],
            client_name=client_name,
            client_phone=client_phone
        )
        
        return booking_record
        
    except Exception as e:
        log.error(f"Error creating booking from parsed data: {e}")
        raise e

# ===================== USER RECORDS ==================
def format_user_record(record: Dict) -> str:
    """Форматирует запись пользователя для отображения"""
    try:
        services = record.get("services", [])
        staff = record.get("staff", {})
        company = record.get("company", {})
        
        text = f"📅 *{record.get('date', 'Неизвестно')}*\n"
        text += f"⏰ {record.get('datetime', 'Неизвестно')}\n"
        text += f"👤 Мастер: *{staff.get('name', 'Неизвестно')}*\n"
        text += f"🏢 {company.get('title', 'Салон')}\n"
        
        if services:
            text += "🛍 *Услуги:*\n"
            for service in services:
                name = service.get("title", "Услуга")
                cost = service.get("cost", 0)
                if cost > 0:
                    text += f"  • {name} - {cost} ₽\n"
                else:
                    text += f"  • {name}\n"
        
        if record.get("comment"):
            text += f"💬 Комментарий: {record.get('comment')}\n"
        
        status_map = {
            2: "✅ Подтверждена",
            1: "✅ Выполнена", 
            0: "⏳ Ожидание",
            -1: "❌ Не пришел"
        }
        status = record.get("visit_attendance", 0)
        text += f"📊 Статус: {status_map.get(status, 'Неизвестно')}\n"
        
        return text
    except Exception as e:
        log.error(f"Error formatting record: {e}")
        return "❌ Ошибка отображения записи"

def get_user_records(user_id: int) -> List[Dict]:
    """Получить записи пользователя"""
    return UserRecords.get(user_id, [])

def add_user_record(user_id: int, record: Dict):
    """Добавить запись пользователя"""
    UserRecords[user_id].append(record)

def remove_user_record(user_id: int, record_id: int):
    """Удалить запись пользователя"""
    UserRecords[user_id] = [r for r in UserRecords[user_id] if r.get("id") != record_id]

def create_real_booking(user_id: int, service_name: str, master_name: str, date_time: str, client_name: str = "", client_phone: str = "") -> Dict:
    """Создать реальную запись через YClients API"""
    log.info(f"🚀 STARTING REAL BOOKING: user_id={user_id}, service='{service_name}', master='{master_name}', datetime='{date_time}'")
    
    try:
        log.info("📞 Getting company ID...")
        company_id = get_company_id()
        if not company_id:
            raise Exception("Не удалось получить ID компании")
        log.info(f"✅ Company ID: {company_id}")
        
        # Находим услугу по названию
        log.info("🔍 Searching for service...")
        services = get_services()
        log.info(f"📋 Available services: {[s.get('title', 'Unknown') for s in services[:3]]}")
        
        service = None
        for s in services:
            if service_name.lower() in s.get("title", "").lower():
                service = s
                break
        
        if not service:
            log.error(f"❌ Service '{service_name}' not found")
            raise Exception(f"Услуга '{service_name}' не найдена")
        log.info(f"✅ Found service: {service.get('title')} (ID: {service.get('id')})")
        
        # Находим мастера по имени
        log.info("👥 Searching for master...")
        masters = get_masters()
        log.info(f"👥 Available masters: {[m.get('name', 'Unknown') for m in masters[:3]]}")
        
        master = None
        for m in masters:
            if master_name.lower() in m.get("name", "").lower():
                master = m
                break
        
        if not master:
            log.error(f"❌ Master '{master_name}' not found")
            raise Exception(f"Мастер '{master_name}' не найден")
        log.info(f"✅ Found master: {master.get('name')} (ID: {master.get('id')})")
        
        # Создаем клиента если нужно
        client_id = None
        if client_phone:
            log.info(f"📱 Processing client with phone: {client_phone}")
            try:
                # Ищем существующего клиента
                log.info("🔍 Searching for existing client...")
                existing_clients = yclients.find_client_by_phone(company_id, client_phone)
                log.info(f"📞 Client search result: {existing_clients}")
                
                if existing_clients.get("data"):
                    client_id = existing_clients["data"][0]["id"]
                    log.info(f"✅ Found existing client ID: {client_id}")
            except Exception as e:
                log.error(f"❌ Error searching for client: {e}")
            
            # Если клиент не найден, создаем нового
            if not client_id:
                try:
                    log.info("👤 Creating new client...")
                    new_client = yclients.create_client(
                        company_id,
                        name=client_name or "Клиент",
                        phone=client_phone,
                        email="",
                        comment="Создан через Telegram бот"
                    )
                    client_id = new_client["data"]["id"]
                    log.info(f"✅ Created new client ID: {client_id}")
                except Exception as e:
                    log.error(f"❌ Error creating client: {e}")
        
        # Создаем запись
        log.info("📝 Creating record in YClients...")
        log.info(f"📝 Record details: company_id={company_id}, service_id={service['id']}, staff_id={master['id']}, datetime={date_time}, client_id={client_id}")
        
        record = yclients.create_record(
            company_id,
            service_id=service["id"],
            staff_id=master["id"],
            date_time=date_time,
            client_id=client_id,
            comment=f"Запись через Telegram бот (пользователь {user_id})",
            seance_length=service.get("length", 3600)  # Длительность в секундах
        )
        
        log.info(f"✅ Record created successfully: {record}")
        
        # Добавляем в локальное хранилище
        booking_record = {
            "id": record["data"]["id"],
            "date": date_time.split()[0],
            "datetime": date_time,
            "services": [{
                "id": service["id"],
                "title": service["title"],
                "cost": service.get("price_min", 0)
            }],
            "staff": {
                "id": master["id"],
                "name": master["name"],
                "specialization": master.get("specialization", "")
            },
            "company": {
                "id": company_id,
                "title": "Салон"
            },
            "comment": f"Запись через Telegram бот",
            "visit_attendance": 0,
            "length": service.get("length", 60),
            "online": True
        }
        
        add_user_record(user_id, booking_record)
        log.info(f"🎉 BOOKING COMPLETED SUCCESSFULLY! Record ID: {booking_record['id']}")
        return booking_record
        
    except Exception as e:
        log.error(f"❌ CRITICAL ERROR in create_real_booking: {e}")
        log.error(f"❌ Error type: {type(e)}")
        import traceback
        log.error(f"❌ Traceback: {traceback.format_exc()}")
        raise e

# ===================== MENU HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Записаться", callback_data="book_appointment")],
        [InlineKeyboardButton("📋 Услуги", callback_data="services")],
        [InlineKeyboardButton("👥 Мастера", callback_data="masters")],
        [InlineKeyboardButton("📅 Мои записи", callback_data="my_records")],
        [InlineKeyboardButton("💬 Чат с AI", callback_data="chat")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "✨ *Добро пожаловать в салон красоты!* ✨\n\n"
        "🎯 *Что я умею:*\n"
        "• 📝 Записать вас к мастеру\n"
        "• 📋 Показать доступные услуги\n"
        "• 👥 Познакомить с мастерами\n"
        "• 📅 Управлять вашими записями\n"
        "• 💬 Ответить на вопросы\n\n"
        "Выберите действие:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Записаться", callback_data="book_appointment")],
        [InlineKeyboardButton("📋 Услуги", callback_data="services")],
        [InlineKeyboardButton("👥 Мастера", callback_data="masters")],
        [InlineKeyboardButton("📅 Мои записи", callback_data="my_records")],
        [InlineKeyboardButton("💬 Чат с AI", callback_data="chat")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🏠 *Главное меню*\n\n"
        "📝 *Записаться* - создать новую запись\n"
        "📋 *Услуги* - посмотреть доступные услуги\n"
        "👥 *Мастера* - посмотреть мастеров и их расписание\n"
        "📅 *Мои записи* - просмотр и управление записями\n"
        "💬 *Чат с AI* - общение с AI помощником",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "services":
        await show_services(query)
    elif query.data == "masters":
        await show_masters(query)
    elif query.data == "my_records":
        await show_user_records(query)
    elif query.data == "book_appointment":
        await start_booking_process(query)
    elif query.data == "chat":
        await query.edit_message_text("Теперь вы можете писать сообщения для общения с AI помощником 💬")
    elif query.data == "back_to_menu":
        await show_main_menu(query)
    elif query.data.startswith("delete_record_"):
        record_id = int(query.data.replace("delete_record_", ""))
        await delete_user_record(query, record_id)

async def show_services(query: CallbackQuery):
    services = get_services()
    if not services:
        await query.edit_message_text("❌ Не удалось загрузить услуги. Попробуйте позже.")
        return
    
    text = "✨ *Наши услуги* ✨\n\n"
    for i, service in enumerate(services[:8], 1):  # Показываем первые 8 услуг
        name = service.get("title", "Без названия")
        price = service.get("price_min", 0)
        duration = service.get("length", 0)
        
        # Красивое форматирование с эмодзи
        if "маникюр" in name.lower():
            emoji = "💅"
        elif "педикюр" in name.lower():
            emoji = "🦶"
        elif "массаж" in name.lower():
            emoji = "💆"
        else:
            emoji = "✨"
            
        text += f"{emoji} *{name}*\n"
        if price > 0:
            text += f"   💰 от {price} ₽\n"
        if duration > 0:
            text += f"   ⏱ {duration} мин\n"
        text += "\n"
    
    keyboard = [
        [InlineKeyboardButton("📝 Записаться", callback_data="book_appointment")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_masters(query: CallbackQuery):
    masters = get_masters()
    if not masters:
        await query.edit_message_text("❌ Не удалось загрузить мастеров. Попробуйте позже.")
        return
    
    text = "👥 *Наши мастера* 👥\n\n"
    for master in masters:
        name = master.get("name", "Без имени")
        specialization = master.get("specialization", "")
        
        # Красивое форматирование с эмодзи
        if "массаж" in specialization.lower():
            emoji = "💆‍♀️"
        elif "мастер" in specialization.lower():
            emoji = "💅"
        else:
            emoji = "✨"
            
        text += f"{emoji} *{name}*\n"
        if specialization:
            text += f"   🎯 {specialization}\n"
        text += "\n"
    
    keyboard = [
        [InlineKeyboardButton("📝 Записаться", callback_data="book_appointment")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_user_records(query: CallbackQuery):
    """Показать записи пользователя"""
    user_id = query.from_user.id
    records = get_user_records(user_id)
    
    if not records:
        keyboard = [
            [InlineKeyboardButton("📝 Записаться", callback_data="book_appointment")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📅 *Мои записи*\n\n"
            "У вас пока нет записей.\n\n"
            "💡 *Создайте первую запись:*\n"
            "• Используйте кнопку \"📝 Записаться\"\n"
            "• Или напишите в чат \"хочу записаться\"",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return
    
    text = "📅 *Мои записи* 📅\n\n"
    keyboard = []
    
    for i, record in enumerate(records[:5]):  # Показываем первые 5 записей
        record_text = format_user_record(record)
        text += f"📋 *Запись {i+1}:*\n{record_text}\n"
        
        # Добавляем кнопку удаления для каждой записи
        keyboard.append([
            InlineKeyboardButton(
                f"🗑 Удалить запись {i+1}", 
                callback_data=f"delete_record_{record.get('id', i)}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text, 
        parse_mode='Markdown', 
        reply_markup=reply_markup
    )

async def delete_user_record(query: CallbackQuery, record_id: int):
    """Удалить запись пользователя"""
    user_id = query.from_user.id
    
    try:
        # Удаляем из локального хранилища
        remove_user_record(user_id, record_id)
        
        # TODO: Здесь можно добавить вызов API для удаления записи
        # yclients.delete_user_record(record_id, record_hash)
        
        await query.edit_message_text(
            f"✅ Запись #{record_id} успешно удалена!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 К записям", callback_data="my_records")
            ]])
        )
    except Exception as e:
        log.error(f"Error deleting record: {e}")
        await query.edit_message_text(
            "❌ Ошибка при удалении записи. Попробуйте позже.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 К записям", callback_data="my_records")
            ]])
        )

async def start_booking_process(query: CallbackQuery):
    """Начать процесс записи"""
    user_id = query.from_user.id
    
    # Проверяем, есть ли номер телефона
    if user_id not in UserPhone:
        await query.edit_message_text(
            "📱 *Для записи нужен ваш номер телефона*\n\n"
            "Пожалуйста, отправьте номер в формате:\n"
            "`+7XXXXXXXXXX`\n\n"
            "Например: `+79991234567`",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")
            ]])
        )
        return
    
    # Показываем доступные услуги и мастеров
    services = get_services()
    masters = get_masters()
    
    text = "📝 *Создание записи* 📝\n\n"
    text += "✨ *Доступные услуги:*\n"
    for service in services[:5]:
        name = service.get('title', 'Услуга')
        price = service.get('price_min', 0)
        if price > 0:
            text += f"• {name} (от {price} ₽)\n"
        else:
            text += f"• {name}\n"
    
    text += "\n👥 *Доступные мастера:*\n"
    for master in masters[:5]:
        name = master.get('name', 'Мастер')
        spec = master.get('specialization', '')
        if spec:
            text += f"• {name} ({spec})\n"
        else:
            text += f"• {name}\n"
    
    text += "\n💬 *Напишите сообщение с вашими пожеланиями:*\n"
    text += "Например: `Хочу записаться на маникюр к Арине на завтра в 14:00`"
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")
        ]])
    )

async def show_main_menu(query: CallbackQuery):
    keyboard = [
        [InlineKeyboardButton("📝 Записаться", callback_data="book_appointment")],
        [InlineKeyboardButton("📋 Услуги", callback_data="services")],
        [InlineKeyboardButton("👥 Мастера", callback_data="masters")],
        [InlineKeyboardButton("📅 Мои записи", callback_data="my_records")],
        [InlineKeyboardButton("💬 Чат с AI", callback_data="chat")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "🏠 *Главное меню*\n\n"
        "📝 *Записаться* - создать новую запись\n"
        "📋 *Услуги* - посмотреть доступные услуги\n"
        "👥 *Мастера* - посмотреть мастеров и их расписание\n"
        "📅 *Мои записи* - просмотр и управление записями\n"
        "💬 *Чат с AI* - общение с AI помощником",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

def create_test_record(user_id: int):
    """Создать тестовую запись для демонстрации"""
    test_record = {
        "id": user_id + 1000,  # Простой ID для теста
        "date": "2024-01-15",
        "datetime": "2024-01-15 14:30",
        "services": [
            {
                "id": 1,
                "title": "Стрижка",
                "cost": 1500,
                "price_min": 1200,
                "price_max": 2000
            }
        ],
        "staff": {
            "id": 1,
            "name": "Анна Иванова",
            "specialization": "Парикмахер"
        },
        "company": {
            "id": 1,
            "title": "Салон красоты 'Элегант'",
            "address": "ул. Примерная, 123"
        },
        "comment": "Тестовая запись",
        "visit_attendance": 0,  # Ожидание
        "length": 60,
        "online": True
    }
    add_user_record(user_id, test_record)
    return test_record

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id
    add_memory(user_id, "user", text)

    # Проверяем специальные команды
    if text.lower() in ["создать тестовую запись", "тест запись", "добавить запись"]:
        test_record = create_test_record(user_id)
        await update.message.reply_text(
            f"✅ *Создана тестовая запись!*\n\n"
            f"📅 *Дата:* {test_record['date']}\n"
            f"⏰ *Время:* {test_record['datetime']}\n"
            f"👤 *Мастер:* {test_record['staff']['name']}\n"
            f"🛍 *Услуга:* {test_record['services'][0]['title']}\n\n"
            f"Используйте меню *'Мои записи'* для просмотра!",
            parse_mode='Markdown'
        )
        return
    
    # Проверяем, является ли сообщение номером телефона
    if text.startswith("+") and len(text) >= 10:
        UserPhone[user_id] = text
        await update.message.reply_text(
            f"✅ *Номер телефона {text} сохранен!*\n\n"
            f"Теперь вы можете создавать записи.\n"
            f"Напишите `хочу записаться` для начала.",
            parse_mode='Markdown'
        )
        return

    if is_booking(text):
        log.info(f"🎯 BOOKING DETECTED: '{text}'")
        # Сначала пробуем парсить сообщение напрямую
        history = get_recent_history(user_id, 50)
        log.info(f"📚 HISTORY: {history[:200]}...")
        parsed_data = parse_booking_message(text, history)
        
        log.info(f"🔍 PARSED MESSAGE: {parsed_data}")
        
        # Если удалось распарсить все данные, создаем запись напрямую
        if parsed_data["has_all_info"]:
            try:
                user_phone = UserPhone.get(user_id)
                if not user_phone:
                    await update.message.reply_text(
                        "📱 *Для создания записи нужен ваш номер телефона*\n\n"
                        "Пожалуйста, отправьте номер в формате:\n"
                        "`+7XXXXXXXXXX`",
                        parse_mode='Markdown'
                    )
                    return
                
                # Создаем запись напрямую
                booking_record = create_booking_from_parsed_data(
                    user_id,
                    parsed_data,
                    client_name=update.message.from_user.first_name or "Клиент",
                    client_phone=user_phone
                )
                
                answer = f"🎉 *Запись успешно создана в системе!* 🎉\n\n"
                answer += f"📅 *Услуга:* {parsed_data['service']}\n"
                answer += f"👤 *Мастер:* {parsed_data['master']}\n"
                answer += f"⏰ *Время:* {parsed_data['datetime']}\n\n"
                answer += "Спасибо за запись! Ждем вас в салоне! ✨"
                
            except Exception as e:
                log.error(f"Error creating booking from parsed data: {e}")
                
                # Sprawdzamy czy to konflikt czasowy
                if "недоступно" in str(e) or "conflict" in str(e).lower():
                    answer = f"❌ *Время {parsed_data['datetime']} недоступно*\n\n"
                    answer += f"💡 *Предлагаем альтернативные варианты:*\n"
                    answer += f"• {parsed_data['service']} у {parsed_data['master']}\n"
                    answer += f"• Завтра в 14:00\n"
                    answer += f"• Завтра в 15:00\n"
                    answer += f"• Завтра в 17:00\n\n"
                    answer += f"Напишите желаемое время, например: `завтра 14:00`"
                else:
                    answer = f"❌ *Ошибка при создании записи:* {str(e)}"
        else:
            # Если не удалось распарсить, используем AI
            api_data = get_api_data_for_ai()
            msg = BOOKING_PROMPT.replace("{{api_data}}", api_data).replace("{{message}}", text).replace("{{history}}", history)
            log.info(f"🤖 AI PROMPT: {msg}")
        answer = groq_chat([{"role": "user", "content": msg}])
            log.info(f"🤖 AI RESPONSE: {answer}")
            
            # Проверяем, содержит ли ответ команду для создания записи
            if "ЗАПИСЬ:" in answer:
                try:
                    # Парсим данные из ответа AI
                    booking_line = [line for line in answer.split('\n') if 'ЗАПИСЬ:' in line][0]
                    parts = booking_line.split('|')
                    if len(parts) >= 3:
                        service_name = parts[0].replace('ЗАПИСЬ:', '').strip()
                        master_name = parts[1].strip()
                        date_time = parts[2].strip()
                        
                        # Проверяем, есть ли номер телефона
                        user_phone = UserPhone.get(user_id)
                        if not user_phone:
                            await update.message.reply_text(
                                "📱 *Для создания записи нужен ваш номер телефона*\n\n"
                                "Пожалуйста, отправьте номер в формате:\n"
                                "`+7XXXXXXXXXX`",
                                parse_mode='Markdown'
                            )
                            return
                        
                        # Создаем реальную запись
                        booking_record = create_real_booking(
                            user_id, 
                            service_name, 
                            master_name, 
                            date_time,
                            client_name=update.message.from_user.first_name or "Клиент",
                            client_phone=user_phone
                        )
                        
                        # Обновляем ответ
                        answer = f"🎉 *Запись успешно создана в системе!* 🎉\n\n" + answer.replace("ЗАПИСЬ:", "📅 *Создана запись:*")
                        
                except Exception as e:
                    log.error(f"Error creating booking: {e}")
                    
                    # Sprawdzamy czy to konflikt czasowy
                    if "недоступно" in str(e) or "conflict" in str(e).lower():
                        answer += f"\n\n❌ *Время {date_time} недоступно*\n\n"
                        answer += f"💡 *Предлагаем альтернативные варианты:*\n"
                        answer += f"• {service_name} у {master_name}\n"
                        answer += f"• Завтра в 14:00\n"
                        answer += f"• Завтра в 15:00\n"
                        answer += f"• Завтра в 17:00\n\n"
                        answer += f"Напишите желаемое время, например: `завтра 14:00`"
                    else:
                        answer += f"\n\n❌ *Ошибка при создании записи:* {str(e)}"
    else:
        msg = CHAT_PROMPT.replace("{{history}}", get_history(user_id)).replace("{{message}}", text)
        answer = groq_chat([{"role": "user", "content": msg}])

    add_memory(user_id, "assistant", answer)
    await update.message.reply_text(answer)

# ===================== RUN BOT ========================
def main():
    # Start Telegram bot
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    
    # Callback query handler for inline buttons
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Message handler for AI chat
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    
    # Start bot
    log.info("🚀 Starting Telegram Bot...")
    app.run_polling()

if __name__ == "__main__":
    main()
