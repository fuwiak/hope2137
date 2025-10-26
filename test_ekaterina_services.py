#!/usr/bin/env python3
"""
Test script to check all massage services for Екатерина
"""
import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yclients_client import YClientsClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

def test_ekaterina_services():
    """Test all services for Екатерина (массажист)"""
    load_dotenv()
    
    partner_token = os.getenv("YCLIENTS_PARTNER_TOKEN")
    user_token = os.getenv("YCLIENTS_USER_TOKEN")
    
    if not partner_token or not user_token:
        print("❌ Missing YClients tokens in .env file")
        return False
    
    yclients = YClientsClient(partner_token, user_token)
    
    try:
        # Get company ID
        companies = yclients.my_companies()
        company_id = companies["data"][0]["id"]
        print(f"✅ Company ID: {company_id}")
        
        # Get all masters
        masters_response = yclients.company_masters(company_id)
        masters = masters_response["data"]
        
        # Find Екатерина
        ekaterina = None
        for master in masters:
            if "екатерина" in master["name"].lower():
                ekaterina = master
                break
        
        if not ekaterina:
            print("❌ Екатерина not found")
            return False
            
        print(f"✅ Found Екатерина: {ekaterina['name']} (ID: {ekaterina['id']})")
        print(f"   Specialization: {ekaterina['specialization']}")
        
        # Get all services for Екатерина
        print(f"\n💰 Getting ALL services for Екатерина...")
        services_response = yclients.get_service_details(company_id, staff_id=ekaterina['id'])
        
        if services_response.get("success"):
            services = services_response.get("data", [])
            print(f"✅ Found {len(services)} services for Екатерина:")
            
            for i, service in enumerate(services, 1):
                name = service.get("title", "No name")
                cost = service.get("cost", 0)
                price_min = service.get("price_min", 0)
                price_max = service.get("price_max", 0)
                duration = service.get("length", 0)
                
                print(f"\n{i}. {name}")
                if cost > 0:
                    print(f"   💰 Cost: {cost} ₽")
                elif price_min > 0 and price_max > 0:
                    if price_min == price_max:
                        print(f"   💰 Price: {price_min} ₽")
                    else:
                        print(f"   💰 Price: {price_min}-{price_max} ₽")
                elif price_min > 0:
                    print(f"   💰 Price: from {price_min} ₽")
                
                if duration > 0:
                    print(f"   ⏱ Duration: {duration} min")
                    
                # Show all fields for debugging
                print(f"   🔍 All fields: {list(service.keys())}")
        else:
            print(f"❌ Failed to get services: {services_response}")
            return False
        
        # Also check all services in company to see massage category
        print(f"\n🔍 Checking ALL company services...")
        all_services = yclients.get_service_details(company_id)
        if all_services.get("success"):
            services = all_services.get("data", [])
            massage_services = [s for s in services if "массаж" in s.get("title", "").lower()]
            print(f"✅ Found {len(massage_services)} massage services in company:")
            
            for service in massage_services:
                print(f"   • {service.get('title', 'No name')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing ALL services for Екатерина...")
    success = test_ekaterina_services()
    
    if success:
        print("\n🎉 Test completed!")
    else:
        print("\n❌ Test failed.")
        sys.exit(1)
