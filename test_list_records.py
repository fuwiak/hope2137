#!/usr/bin/env python3
"""
Test listowania rezerwacji w YClients
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
        logging.FileHandler('list_records_test.log')
    ]
)
log = logging.getLogger()

# Załaduj zmienne środowiskowe
load_dotenv()

YCLIENTS_PARTNER_TOKEN = os.getenv("YCLIENTS_PARTNER_TOKEN")
YCLIENTS_USER_TOKEN = os.getenv("YCLIENTS_USER_TOKEN")

def test_list_records():
    """Test listowania rezerwacji"""
    log.info("🚀 STARTING LIST RECORDS TEST")
    
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
        
        # Listowanie rezerwacji
        log.info("📋 Getting records...")
        records = client.company_records(company_id)
        
        log.info(f"📋 Found {len(records.get('data', []))} records")
        
        # Wyświetlanie szczegółów rezerwacji
        for i, record in enumerate(records.get("data", [])[:5]):  # Pokaż pierwsze 5
            log.info(f"📝 Record {i+1}:")
            log.info(f"   ID: {record.get('id')}")
            log.info(f"   Date: {record.get('date')}")
            log.info(f"   Staff: {record.get('staff', {}).get('name', 'Unknown')}")
            log.info(f"   Services: {[s.get('title', 'Unknown') for s in record.get('services', [])]}")
            log.info(f"   Client: {record.get('client', {}).get('name', 'Unknown')}")
            log.info("   ---")
        
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
    success = test_list_records()
    if success:
        print("✅ List records test completed successfully!")
        print("📋 Check the logs for record details!")
    else:
        print("❌ List records test failed!")
