#!/usr/bin/env python3
"""
Test script to check Арина's actual services from API
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

def test_arina_services():
    """Test Арина's actual services from API"""
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
        
        # Find Арина
        arina = None
        for master in masters:
            if "арина" in master["name"].lower():
                arina = master
                break
        
        if not arina:
            print("❌ Арина not found")
            return False
            
        print(f"✅ Found Арина: {arina['name']} (ID: {arina['id']})")
        print(f"   Specialization: {arina['specialization']}")
        
        # Get ALL services for Арина
        print(f"\n🔍 Getting ALL services for Арина from API...")
        services_response = yclients.get_service_details(company_id, staff_id=arina['id'])
        
        if services_response.get("success"):
            services = services_response.get("data", [])
            print(f"✅ API returned {len(services)} services for Арина:")
            
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
                else:
                    print(f"   💰 Price: NO PRICE SET")
                
                if duration > 0:
                    print(f"   ⏱ Duration: {duration} min")
                    
                # Show service ID for debugging
                service_id = service.get("id", "No ID")
                print(f"   🆔 Service ID: {service_id}")
        else:
            print(f"❌ Failed to get services: {services_response}")
            return False
        
        # Also check what bot shows vs what API returns
        print(f"\n📊 COMPARISON:")
        print(f"   API services for Арина: {len(services)}")
        
        # Check if any services match the user's list
        user_services = [
            "Маникюр с покрытием гель-лак",
            "Полный педикюр с покрытием гель-лак", 
            "Маникюр в 4 руки",
            "Наращивание гелевых ногтей",
            "Дизайн ногтей (фольга, стемпинг)",
            "Уход за кутикулой (SPA-маникюр)",
            "Парафинотерапия для рук",
            "Парафинотерапия для ног"
        ]
        
        print(f"\n🔍 Checking if user's services exist in API:")
        api_service_names = [s.get("title", "") for s in services]
        
        for user_service in user_services:
            found = any(user_service.lower() in api_name.lower() for api_name in api_service_names)
            status = "✅ FOUND" if found else "❌ NOT FOUND"
            print(f"   {status}: {user_service}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Арина's ACTUAL services from API...")
    success = test_arina_services()
    
    if success:
        print("\n🎉 Test completed!")
    else:
        print("\n❌ Test failed.")
        sys.exit(1)
