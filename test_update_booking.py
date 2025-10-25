#!/usr/bin/env python3
"""
Test aktualizacji rezerwacji w YClients
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
        logging.FileHandler('update_booking_test.log')
    ]
)
log = logging.getLogger()

# Załaduj zmienne środowiskowe
load_dotenv()

YCLIENTS_PARTNER_TOKEN = os.getenv("YCLIENTS_PARTNER_TOKEN")
YCLIENTS_USER_TOKEN = os.getenv("YCLIENTS_USER_TOKEN")

def test_update_booking():
    """Test aktualizacji rezerwacji"""
    log.info("🚀 STARTING UPDATE BOOKING TEST")
    
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
        
        # ID rezerwacji do aktualizacji
        booking_id = 1369928757  # Arina booking (26.10.2025 12:00)
        log.info(f"✏️ Attempting to update booking ID: {booking_id}")
        
        # Najpierw pobierzemy dane rezerwacji
        log.info("📋 Getting booking details...")
        booking_details = client.get(f"/record/{company_id}/{booking_id}")
        log.info(f"📋 Booking details: {booking_details}")
        
        # Aktualizacja rezerwacji - zmiana komentarza i czasu
        log.info("✏️ Updating booking...")
        result = client.update_record(
            company_id, 
            booking_id,
            staff_id=booking_details["data"]["staff_id"],
            services=booking_details["data"]["services"],
            client=booking_details["data"]["client"],
            seance_length=booking_details["data"]["seance_length"],
            comment="Zaktualizowana rezerwacja przez API - zmieniony komentarz",
            datetime="2025-10-26 14:00",  # Zmiana z 12:00 na 14:00
            send_sms=False
        )
        
        log.info(f"🎉 BOOKING UPDATED SUCCESSFULLY!")
        log.info(f"✏️ Updated booking ID: {booking_id}")
        log.info(f"✏️ New time: 2025-10-26 14:00")
        log.info(f"✏️ New comment: Zaktualizowana rezerwacja przez API")
        log.info(f"✏️ Result: {result}")
        
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
    success = test_update_booking()
    if success:
        print("✅ Update booking test completed successfully!")
        print("✏️ Check your YClients system - the booking should be updated!")
    else:
        print("❌ Update booking test failed!")
