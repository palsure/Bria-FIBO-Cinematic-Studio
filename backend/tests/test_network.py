#!/usr/bin/env python3
"""
Test network connectivity and DNS resolution
"""

import socket
import requests
import sys

def test_dns(hostname):
    """Test DNS resolution"""
    try:
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS Resolution: {hostname} -> {ip}")
        return True
    except socket.gaierror as e:
        print(f"❌ DNS Resolution Failed: {hostname}")
        print(f"   Error: {e}")
        return False

def test_https(url):
    """Test HTTPS connectivity"""
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ HTTPS Connection: {url} (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError as e:
        print(f"❌ HTTPS Connection Failed: {url}")
        print(f"   Error: {str(e)[:100]}")
        return False
    except Exception as e:
        print(f"⚠️  HTTPS Connection Issue: {url}")
        print(f"   Error: {str(e)[:100]}")
        return False

def main():
    print("=" * 60)
    print("Network Connectivity Test")
    print("=" * 60)
    print()
    
    # Test DNS
    hosts = [
        "engine.bria.ai",
        "api.bria.ai",
        "bria.ai",
        "google.com"  # Control test
    ]
    
    print("DNS Resolution Tests:")
    print("-" * 60)
    dns_results = {}
    for host in hosts:
        dns_results[host] = test_dns(host)
    print()
    
    # Test HTTPS
    urls = [
        "https://google.com",  # Control test
        "https://bria.ai",
        "https://engine.bria.ai",
        "https://api.bria.ai",
    ]
    
    print("HTTPS Connectivity Tests:")
    print("-" * 60)
    https_results = {}
    for url in urls:
        https_results[url] = test_https(url)
    print()
    
    # Summary
    print("=" * 60)
    print("Summary:")
    print("-" * 60)
    
    if dns_results.get("google.com") and not dns_results.get("engine.bria.ai"):
        print("❌ DNS Issue: Can resolve google.com but not BRIA domains")
        print("   This suggests a DNS or network configuration problem")
        print()
        print("Possible solutions:")
        print("  1. Check your internet connection")
        print("  2. Try different DNS servers (8.8.8.8, 1.1.1.1)")
        print("  3. Check firewall/proxy settings")
        print("  4. Contact your network administrator")
    elif not dns_results.get("google.com"):
        print("❌ General DNS Issue: Cannot resolve any domains")
        print("   Check your internet connection")
    elif https_results.get("https://google.com") and not https_results.get("https://engine.bria.ai"):
        print("⚠️  HTTPS Issue: Can connect to google.com but not BRIA")
        print("   BRIA servers might be down or blocked")
    else:
        print("✅ Network connectivity appears normal")
        print("   BRIA API endpoint might be incorrect")
        print("   Check BRIA dashboard for correct endpoint URL")
    
    print()

if __name__ == "__main__":
    main()




