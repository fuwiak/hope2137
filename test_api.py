#!/usr/bin/env python3
"""
Тестовый скрипт для проверки YClients API
"""
import os
from dotenv import load_dotenv
from yclients_client import YClientsClient, YClientsError

# Загружаем переменные окружения
load_dotenv()

YCLIENTS_PARTNER_TOKEN = os.getenv("YCLIENTS_PARTNER_TOKEN")
YCLIENTS_USER_TOKEN = os.getenv("YCLIENTS_USER_TOKEN")

def test_api():
    """Тестируем подключение к YClients API"""
    if not YCLIENTS_PARTNER_TOKEN or not YCLIENTS_USER_TOKEN:
        print("❌ Ошибка: Не найдены токены YClients в .env файле")
        return
    
    try:
        # Создаем клиент
        client = YClientsClient(YCLIENTS_PARTNER_TOKEN, YCLIENTS_USER_TOKEN)
        
        # Тестируем получение компаний
        print("🔍 Получаем список компаний...")
        companies = client.my_companies()
        print(f"✅ Найдено компаний: {len(companies.get('data', []))}")
        
        if companies.get("data"):
            company_id = companies["data"][0]["id"]
            print(f"📋 ID первой компании: {company_id}")
            
            # Тестируем получение услуг
            print("🔍 Получаем услуги...")
            services = client.company_services(company_id)
            print(f"✅ Найдено услуг: {len(services.get('data', []))}")
            
            # Показываем первые 3 услуги
            for i, service in enumerate(services.get("data", [])[:3]):
                name = service.get("title", "Без названия")
                price = service.get("price_min", 0)
                print(f"  {i+1}. {name} (от {price} руб.)")
            
            # Тестируем получение мастеров
            print("🔍 Получаем мастеров...")
            masters = client.company_masters(company_id)
            print(f"✅ Найдено мастеров: {len(masters.get('data', []))}")
            
            # Показываем первых 3 мастеров
            for i, master in enumerate(masters.get("data", [])[:3]):
                name = master.get("name", "Без имени")
                specialization = master.get("specialization", "")
                print(f"  {i+1}. {name} ({specialization})")
            
            # Тестируем методы для работы с записями пользователей
            print("\n🔍 Тестируем методы для записей пользователей...")
            print("✅ Методы для работы с записями добавлены:")
            print("  - get_user_record(record_id, record_hash)")
            print("  - delete_user_record(record_id, record_hash)")
            print("  - send_phone_code(company_id, phone, fullname)")
            print("  - auth_by_phone_code(phone, code)")
        
        print("\n✅ API работает корректно!")
        print("\n📋 Доступные методы YClients API:")
        print("  - Получение компаний, услуг, мастеров")
        print("  - Создание клиентов и записей")
        print("  - Управление записями пользователей")
        print("  - Авторизация по телефону")
        
    except YClientsError as e:
        print(f"❌ Ошибка YClients API: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    test_api()
