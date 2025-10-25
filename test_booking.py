#!/usr/bin/env python3
"""
Test tworzenia rzeczywistej rezerwacji w YClients
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
        logging.FileHandler('booking_test.log')
    ]
)
log = logging.getLogger()

# Załaduj zmienne środowiskowe
load_dotenv()

YCLIENTS_PARTNER_TOKEN = os.getenv("YCLIENTS_PARTNER_TOKEN")
YCLIENTS_USER_TOKEN = os.getenv("YCLIENTS_USER_TOKEN")

def test_create_booking():
    """Test tworzenia rzeczywistej rezerwacji"""
    log.info("🚀 STARTING BOOKING CREATION TEST")
    
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
        
        # Pobieranie usług
        log.info("📋 Getting services...")
        services = client.company_services(company_id)
        # Użyj pierwszej usługi (manicure)
        service = services["data"][0]
        log.info(f"✅ Service: {service['title']} (ID: {service['id']})")
        
        # Pobieranie masterów
        log.info("👥 Getting masters...")
        masters = client.company_masters(company_id)
        # Spróbujmy z trzecim masterem (Полина)
        master = masters["data"][2] if len(masters["data"]) > 2 else masters["data"][0]
        log.info(f"✅ Master: {master['name']} (ID: {master['id']})")
        
        # Tworzenie klienta
        log.info("👤 Creating client...")
        import random
        phone = f"+7999{random.randint(1000000, 9999999)}"
        log.info(f"📱 Using phone: {phone}")
        new_client = client.create_client(
            company_id,
            name="Test Client",
            phone=phone,
            email="test@example.com",
            comment="Test client from booking test"
        )
        client_id = new_client["data"]["id"]
        log.info(f"✅ Created client ID: {client_id}")
        
        # Tworzenie rezerwacji
        log.info("📝 Creating booking...")
        booking = client.create_record(
            company_id,
            service_id=service["id"],
            staff_id=master["id"],
            date_time="2025-11-03 16:00",  # Następny tydzień
            client_id=client_id,
            comment="Test booking from Python script",
            seance_length=7200  # 2 godziny w sekundach (manicure)
        )
        
        log.info(f"🎉 BOOKING CREATED SUCCESSFULLY!")
        log.info(f"📝 Booking ID: {booking['data']['id']}")
        log.info(f"📝 Booking details: {booking}")
        
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
    success = test_create_booking()
    if success:
        print("✅ Booking test completed successfully!")
        print("📝 Check your YClients system for the new booking!")
    else:
        print("❌ Booking test failed!")
