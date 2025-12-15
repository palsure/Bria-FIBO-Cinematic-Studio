#!/usr/bin/env python3
"""
Test BRIA API endpoint to find correct format
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BRIA_API_TOKEN")
BASE_URL = os.getenv("BRIA_API_BASE_URL", "https://engine.prod.bria-api.com/v2")

if not API_TOKEN:
    print("❌ BRIA_API_TOKEN not set in .env")
    exit(1)

headers = {
    "api_token": API_TOKEN,
    "Content-Type": "application/json"
}

print(f"🔍 Testing BRIA API Endpoints")
print(f"Base URL: {BASE_URL}")
print(f"API Token: {API_TOKEN[:10]}...{API_TOKEN[-4:]}")
print()

# Test different endpoint formats
test_endpoints = [
    "/text-to-image/tailored/default",
    "/text-to-image/tailored/1",
    "/text-to-image",
    "/generate",
    "/v2/text-to-image/tailored/default",
]

test_payload = {
    "prompt": "test image",
    "width": 512,
    "height": 512,
    "sync": False
}

for endpoint in test_endpoints:
    url = f"{BASE_URL}{endpoint}" if not endpoint.startswith("http") else endpoint
    print(f"Testing: {url}")
    
    try:
        response = requests.post(url, json=test_payload, headers=headers, timeout=10)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✅ SUCCESS! Use this endpoint: {endpoint}")
            print(f"  Response: {response.json()}")
            break
        elif response.status_code == 401:
            print(f"  ⚠️  Unauthorized - check API token")
        elif response.status_code == 404:
            print(f"  ❌ Not Found")
        else:
            print(f"  ⚠️  Status {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()

print("\n💡 If all endpoints return 404, check:")
print("   1. Your BRIA dashboard for the correct API endpoint")
print("   2. Your account's available model IDs")
print("   3. API documentation for your specific BRIA plan")




