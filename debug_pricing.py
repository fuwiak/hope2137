#!/usr/bin/env python3
"""
Debug script to check why services don't show prices
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

def debug_ekaterina_services():
    """Debug Екатерина services to see why prices are missing"""
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
        
        # Get Екатерина
        masters_response = yclients.company_masters(company_id)
        masters = masters_response["data"]
        
        ekaterina = None
        for master in masters:
            if "екатерина" in master["name"].lower():
                ekaterina = master
                break
        
        if not ekaterina:
            print("❌ Екатерина not found")
            return False
            
        print(f"✅ Found Екатерина: {ekaterina['name']} (ID: {ekaterina['id']})")
        
        # Get services for Екатерина
        print(f"\n🔍 DEBUGGING services for Екатерина...")
        services_response = yclients.get_service_details(company_id, staff_id=ekaterina['id'])
        
        if services_response.get("success"):
            services = services_response.get("data", [])
            print(f"✅ Found {len(services)} services:")
            
            for i, service in enumerate(services, 1):
                name = service.get("title", "No name")
                cost = service.get("cost", 0)
                price_min = service.get("price_min", 0)
                price_max = service.get("price_max", 0)
                
                print(f"\n{i}. {name}")
                print(f"   💰 cost: {cost}")
                print(f"   💰 price_min: {price_min}")
                print(f"   💰 price_max: {price_max}")
                
                # Check what fields are available
                print(f"   🔍 Available price fields:")
                for key, value in service.items():
                    if 'price' in key.lower() or 'cost' in key.lower():
                        print(f"      {key}: {value}")
                
                # Show all fields for debugging
                print(f"   📋 All fields: {list(service.keys())}")
        else:
            print(f"❌ Failed to get services: {services_response}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Debugging Екатерина services pricing...")
    success = debug_ekaterina_services()
    
    if success:
        print("\n🎉 Debug completed!")
    else:
        print("\n❌ Debug failed.")
        sys.exit(1)
