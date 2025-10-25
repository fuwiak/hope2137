#!/usr/bin/env python3
"""
Test rzeczywistych wywołań API YClients z pełnym logowaniem
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
        logging.FileHandler('yclients_api_test.log')
    ]
)
log = logging.getLogger()

# Załaduj zmienne środowiskowe
load_dotenv()

YCLIENTS_PARTNER_TOKEN = os.getenv("YCLIENTS_PARTNER_TOKEN")
YCLIENTS_USER_TOKEN = os.getenv("YCLIENTS_USER_TOKEN")

def test_yclients_api():
    """Test rzeczywistych wywołań API YClients"""
    log.info("🚀 STARTING YCLIENTS API TEST")
    
    if not YCLIENTS_PARTNER_TOKEN or not YCLIENTS_USER_TOKEN:
        log.error("❌ Missing YClients tokens in .env file")
        return False
    
    log.info(f"🔑 Partner Token: {YCLIENTS_PARTNER_TOKEN[:10]}...")
    log.info(f"🔑 User Token: {YCLIENTS_USER_TOKEN[:10]}...")
    
    try:
        # Tworzenie klienta
        log.info("🔧 Creating YClients client...")
        client = YClientsClient(YCLIENTS_PARTNER_TOKEN, YCLIENTS_USER_TOKEN)
        log.info("✅ YClients client created successfully")
        
        # Test 1: Pobieranie firm
        log.info("📞 TEST 1: Getting companies...")
        companies = client.my_companies()
        log.info(f"📞 Companies response: {companies}")
        
        if not companies.get("data"):
            log.error("❌ No companies found")
            return False
        
        company_id = companies["data"][0]["id"]
        log.info(f"✅ Company ID: {company_id}")
        
        # Test 2: Pobieranie usług
        log.info("📋 TEST 2: Getting services...")
        services = client.company_services(company_id)
        log.info(f"📋 Services response: {services}")
        
        # Test 3: Pobieranie masterów
        log.info("👥 TEST 3: Getting masters...")
        masters = client.company_masters(company_id)
        log.info(f"👥 Masters response: {masters}")
        
        # Test 4: Wyszukiwanie klienta
        log.info("👤 TEST 4: Searching for client...")
        try:
            client_search = client.find_client_by_phone(company_id, "+79999999999")
            log.info(f"👤 Client search response: {client_search}")
        except Exception as e:
            log.warning(f"⚠️ Client search failed (expected): {e}")
        
        log.info("🎉 ALL API TESTS COMPLETED SUCCESSFULLY!")
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
    success = test_yclients_api()
    if success:
        print("✅ API test completed successfully!")
    else:
        print("❌ API test failed!")
