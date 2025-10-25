#!/usr/bin/env python3
"""
Test tworzenia rezerwacji dla Poliny na 12:00 26.10.2025
"""
import os
import logging
from dotenv import load_dotenv
from yclients_client import YClientsClient, YClientsError

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('polina_booking_test.log')
    ]
)
log = logging.getLogger()

# Załaduj zmienne środowiskowe
load_dotenv()

YCLIENTS_PARTNER_TOKEN = os.getenv("YCLIENTS_PARTNER_TOKEN")
YCLIENTS_USER_TOKEN = os.getenv("YCLIENTS_USER_TOKEN")

def test_polina_booking():
    """Test tworzenia rezerwacji dla Poliny"""
    log.info("🚀 STARTING POLINA BOOKING TEST")
    
    if not YCLIENTS_PARTNER_TOKEN or not YCLIENTS_USER_TOKEN:
        log.error("❌ Missing YClients tokens in .env file")
        return False
    
    try:
        # Tworzenie klienta
        client = YClientsClient(YCLIENTS_PARTNER_TOKEN, YCLIENTS_USER_TOKEN)
        
        # Pobieranie firmy
        log.info("🏢 Getting company...")
        companies = client.my_companies()
        company_id = companies["data"][0]["id"]
        log.info(f"✅ Company ID: {company_id}")
        
        # Pobieranie usług - znajdź manicure
        log.info("📋 Getting services...")
        services = client.company_services(company_id)
        manicure_service = None
        for s in services["data"]:
            if "маникюр" in s["title"].lower():
                manicure_service = s
                break
        service = manicure_service if manicure_service else services["data"][0]
        log.info(f"✅ Service: {service['title']} (ID: {service['id']})")
        
        # Pobieranie masterów - znajdź Polinę
        log.info("👥 Getting masters...")
        masters = client.company_masters(company_id)
        polina = None
        for m in masters["data"]:
            if "полина" in m["name"].lower():
                polina = m
                break
        master = polina if polina else masters["data"][0]
        log.info(f"✅ Master: {master['name']} (ID: {master['id']})")
        
        # Tworzenie klienta
        log.info("👤 Creating client...")
        import random
        phone = f"+7999{random.randint(1000000, 9999999)}"
        log.info(f"📱 Using phone: {phone}")
        new_client = client.create_client(
            company_id,
            name="Test Client Polina",
            phone=phone,
            email="test@example.com",
            comment="Test client for Polina booking"
        )
        client_id = new_client["data"]["id"]
        log.info(f"✅ Created client ID: {client_id}")
        
        # Tworzenie rezerwacji dla Poliny na 12:00 26.10.2025
        log.info("📝 Creating booking for Polina...")
        booking = client.create_record(
            company_id,
            service_id=service["id"],
            staff_id=master["id"],
            date_time="2025-10-26 12:00",  # 26.10.2025 12:00
            client_id=client_id,
            comment="Test booking for Polina - 26.10.2025 12:00",
            seance_length=7200  # 2 godziny w sekundach
        )
        
        log.info(f"🎉 BOOKING CREATED SUCCESSFULLY!")
        log.info(f"📝 Booking ID: {booking['data']['id']}")
        log.info(f"📝 Master: {master['name']}")
        log.info(f"📝 Service: {service['title']}")
        log.info(f"📝 Date: 2025-10-26 12:00")
        log.info(f"📝 Client: {new_client['data']['name']} ({phone})")
        
        return True
        
    except YClientsError as e:
        log.error(f"❌ YClients API Error: {e}")
        log.error(f"❌ Error status: {e.status}")
        log.error(f"❌ Error meta: {e.meta}")
        return False
    except Exception as e:
        log.error(f"❌ General Error: {e}")
        import traceback
        log.error(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_polina_booking()
    if success:
        print("✅ Polina booking test completed successfully!")
        print("📝 Check your YClients system for the new booking!")
    else:
        print("❌ Polina booking test failed!")
