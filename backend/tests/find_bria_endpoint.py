#!/usr/bin/env python3
"""
Script to help find the correct BRIA API endpoint
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_endpoint(base_url, api_token):
    """Test if an endpoint works"""
    headers = {
        "api_token": api_token,
        "Content-Type": "application/json"
    }
    
    test_url = f"{base_url}/generate"
    payload = {
        "prompt": "test",
        "width": 512,
        "height": 512,
        "sync": False
    }
    
    try:
        response = requests.post(test_url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return True, "✅ Works!"
        elif response.status_code == 401:
            return False, "⚠️  Auth error (endpoint might be correct)"
        elif response.status_code == 404:
            return False, "❌ Not found"
        else:
            return False, f"Status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "❌ Cannot connect"
    except Exception as e:
        return False, f"Error: {str(e)[:50]}"

def main():
    api_token = os.getenv("BRIA_API_TOKEN")
    if not api_token:
        print("❌ BRIA_API_TOKEN not found in .env")
        return
    
    print("=" * 60)
    print("BRIA API Endpoint Finder")
    print("=" * 60)
    print()
    print("Testing common BRIA API endpoints...")
    print()
    
    # Common endpoint patterns to try
    endpoints = [
        "https://api.bria.ai/v2",
        "https://api.bria.ai/api/v2",
        "https://platform.bria.ai/api/v2",
        "https://platform.bria.ai/v2",
        "https://bria.ai/api/v2",
        "https://bria.ai/v2",
        "https://engine.bria.ai/v2",
        "https://engine.bria.ai/api/v2",
    ]
    
    working_endpoints = []
    
    for endpoint in endpoints:
        print(f"Testing: {endpoint}")
        works, message = test_endpoint(endpoint, api_token)
        print(f"  {message}")
        
        if works or "Auth error" in message:
            working_endpoints.append((endpoint, message))
        print()
    
    print("=" * 60)
    if working_endpoints:
        print("✅ Found potential working endpoints:")
        for endpoint, message in working_endpoints:
            print(f"   {endpoint} - {message}")
        print()
        print("Update your .env file:")
        print(f"   BRIA_API_BASE_URL={working_endpoints[0][0]}")
    else:
        print("❌ No working endpoints found")
        print()
        print("Next steps:")
        print("1. Check your BRIA dashboard: https://platform.bria.ai")
        print("2. Look for API Documentation or Settings")
        print("3. Find the 'Base URL' or 'API Endpoint'")
        print("4. Update backend/.env with:")
        print("   BRIA_API_BASE_URL=https://your-correct-endpoint/v2")
    print()

if __name__ == "__main__":
    main()




