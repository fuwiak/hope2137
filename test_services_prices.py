#!/usr/bin/env python3
"""
Test script for YClients services with real prices
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

def test_services_with_prices():
    """Test getting services with real prices"""
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
        if not companies.get("success") or not companies.get("data"):
            print("❌ No companies found")
            return False
            
        company_id = companies["data"][0]["id"]
        print(f"✅ Company ID: {company_id}")
        
        # Test new service details endpoint
        print("\n💰 Testing services with prices...")
        services_response = yclients.get_service_details(company_id)
        
        if services_response.get("success"):
            services = services_response.get("data", [])
            print(f"✅ Found {len(services)} services with prices")
            
            for i, service in enumerate(services[:3], 1):
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
        else:
            print(f"❌ Failed to get services: {services_response}")
            return False
        
        # Test services for specific master
        print("\n👤 Testing services for specific master...")
        masters_response = yclients.company_masters(company_id)
        
        if masters_response.get("success") and masters_response.get("data"):
            masters = masters_response["data"]
            if masters:
                master_id = masters[0]["id"]
                master_name = masters[0]["name"]
                print(f"✅ Testing services for master: {master_name} (ID: {master_id})")
                
                master_services = yclients.get_service_details(company_id, staff_id=master_id)
                if master_services.get("success"):
                    services = master_services.get("data", [])
                    print(f"✅ Found {len(services)} services for {master_name}")
                    
                    for service in services[:2]:
                        name = service.get("title", "No name")
                        cost = service.get("cost", 0)
                        print(f"   • {name}: {cost} ₽" if cost > 0 else f"   • {name}")
                else:
                    print(f"❌ Failed to get services for master: {master_services}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing YClients services with real prices...")
    success = test_services_with_prices()
    
    if success:
        print("\n🎉 All tests passed! Services with prices are working.")
    else:
        print("\n❌ Tests failed. Check your configuration.")
        sys.exit(1)
