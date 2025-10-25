#!/usr/bin/env python3
"""
Test anulowania rezerwacji w YClients
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
        logging.FileHandler('cancel_booking_test.log')
    ]
)
log = logging.getLogger()

# Załaduj zmienne środowiskowe
load_dotenv()

YCLIENTS_PARTNER_TOKEN = os.getenv("YCLIENTS_PARTNER_TOKEN")
YCLIENTS_USER_TOKEN = os.getenv("YCLIENTS_USER_TOKEN")

def test_cancel_booking():
    """Test anulowania rezerwacji"""
    log.info("🚀 STARTING CANCEL BOOKING TEST")
    
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
        
        # ID rezerwacji do anulowania
        booking_id = 1369928574  # Polina booking (26.10.2025 12:00)
        log.info(f"🚫 Attempting to cancel booking ID: {booking_id}")
        
        # Próba anulowania rezerwacji przez zmianę statusu
        log.info("🚫 Canceling booking...")
        
        # Spróbujmy użyć metody PUT do aktualizacji rezerwacji
        try:
            result = client.put(f"/records/{company_id}/{booking_id}", {
                "deleted": True,
                "comment": "Anulowane przez API test"
            })
            log.info(f"🎉 BOOKING CANCELED SUCCESSFULLY!")
            log.info(f"🚫 Canceled booking ID: {booking_id}")
            log.info(f"🚫 Result: {result}")
            return True
        except Exception as e:
            log.error(f"❌ Error canceling booking: {e}")
            return False
        
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
    success = test_cancel_booking()
    if success:
        print("✅ Cancel booking test completed successfully!")
        print("🚫 Check your YClients system - the booking should be canceled!")
    else:
        print("❌ Cancel booking test failed!")
