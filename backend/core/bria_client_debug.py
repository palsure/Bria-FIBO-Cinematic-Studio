"""
Debug script to test BRIA API connection and find correct endpoint
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_bria_endpoints():
    """Test different possible BRIA API endpoints"""
    
    api_token = os.getenv("BRIA_API_TOKEN")
    if not api_token:
        print("❌ BRIA_API_TOKEN not found")
        return
    
    headers = {
        "api_token": api_token,
        "Content-Type": "application/json"
    }
    
    # Possible endpoints to try
    endpoints = [
        "https://engine.bria.ai/v2/generate",
        "https://engine.bria.ai/api/v2/generate",
        "https://api.bria.ai/v2/generate",
        "https://api.bria.ai/api/v2/generate",
    ]
    
    test_payload = {
        "prompt": "A cinematic city street at night",
        "width": 1024,
        "height": 1024,
        "sync": False
    }
    
    print("Testing BRIA API endpoints...\n")
    
    for endpoint in endpoints:
        print(f"Testing: {endpoint}")
        try:
            response = requests.post(
                endpoint,
                json=test_payload,
                headers=headers,
                timeout=10
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ SUCCESS! Use this endpoint: {endpoint}")
                print(f"  Response: {result}")
                return endpoint
            else:
                print(f"  Response: {response.text[:200]}")
        except requests.exceptions.ConnectionError as e:
            print(f"  ❌ Connection error: {str(e)[:100]}")
        except Exception as e:
            print(f"  ⚠️  Error: {str(e)[:100]}")
        print()
    
    print("❌ No working endpoint found. Check BRIA API documentation.")
    print("   Visit: https://docs.bria.ai")

if __name__ == "__main__":
    test_bria_endpoints()




