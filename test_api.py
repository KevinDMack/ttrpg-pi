#!/usr/bin/env python3
"""
Test script for TTRPG Pi API
Verifies all endpoints and functionality
"""

import json
import requests
import sys
import time

API_BASE = "http://localhost:5000"

def test_endpoint(name, url, method='GET', data=None, expected_status=200):
    """Test a single API endpoint"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == expected_status:
            print(f"✓ {name}: PASS (Status {response.status_code})")
            return True
        else:
            print(f"✗ {name}: FAIL (Expected {expected_status}, got {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ {name}: ERROR ({str(e)})")
        return False

def main():
    """Run all API tests"""
    print("=" * 60)
    print("TTRPG Pi API Test Suite")
    print("=" * 60)
    print(f"Testing API at: {API_BASE}")
    print()
    
    tests = []
    
    # Test root endpoint
    tests.append(test_endpoint("Root endpoint", f"{API_BASE}/"))
    
    # Test health check
    tests.append(test_endpoint("Health check", f"{API_BASE}/health"))
    
    # Test config endpoint
    tests.append(test_endpoint("Config endpoint", f"{API_BASE}/config"))
    
    # Test stop endpoint (should work even when nothing is playing)
    tests.append(test_endpoint("Stop music endpoint", f"{API_BASE}/stop"))
    
    # Test valid play endpoints (1-8)
    for i in range(1, 9):
        tests.append(test_endpoint(f"Play sound {i} (GET)", f"{API_BASE}/play/{i}"))
    
    # Test POST play endpoint
    tests.append(test_endpoint("Play sound (POST)", f"{API_BASE}/play", method='POST', data={'button': 3}))
    
    # Test invalid inputs
    tests.append(test_endpoint("Invalid button 0", f"{API_BASE}/play/0", expected_status=400))
    tests.append(test_endpoint("Invalid button 9", f"{API_BASE}/play/9", expected_status=400))
    tests.append(test_endpoint("Invalid POST data", f"{API_BASE}/play", method='POST', data={'button': 'invalid'}, expected_status=400))
    
    print()
    print("=" * 60)
    print(f"Results: {sum(tests)}/{len(tests)} tests passed")
    print("=" * 60)
    
    if all(tests):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
