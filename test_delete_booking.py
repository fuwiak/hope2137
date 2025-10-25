#!/usr/bin/env python3
"""
Test usuwania rezerwacji z YClients
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
        logging.FileHandler('delete_booking_test.log')
    ]
)
log = logging.getLogger()

# Załaduj zmienne środowiskowe
load_dotenv()

YCLIENTS_PARTNER_TOKEN = os.getenv("YCLIENTS_PARTNER_TOKEN")
YCLIENTS_USER_TOKEN = os.getenv("YCLIENTS_USER_TOKEN")

def test_delete_booking():
    """Test usuwania rezerwacji"""
    log.info("🚀 STARTING DELETE BOOKING TEST")
    
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
        
        # ID rezerwacji do usunięcia (używamy ID z poprzednich testów)
        # Polina booking: 1369928574
        # Arina booking: 1369928757
        booking_id = 1369928574  # Polina booking (26.10.2025 12:00)
        log.info(f"🗑️ Attempting to delete booking ID: {booking_id}")
        
        # Usuwanie rezerwacji
        log.info("🗑️ Deleting booking...")
        result = client.delete_record(company_id, booking_id)
        
        log.info(f"🎉 BOOKING DELETED SUCCESSFULLY!")
        log.info(f"🗑️ Deleted booking ID: {booking_id}")
        log.info(f"🗑️ Result: {result}")
        
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
    success = test_delete_booking()
    if success:
        print("✅ Delete booking test completed successfully!")
        print("🗑️ Check your YClients system - the booking should be deleted!")
    else:
        print("❌ Delete booking test failed!")
