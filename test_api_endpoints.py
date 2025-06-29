#!/usr/bin/env python3
"""
API Endpoint Testing Script
Tests all major API endpoints to ensure they're working correctly.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_endpoint(method, url, data=None, headers=None, expected_status=None):
    """Test a single endpoint and print results."""
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PATCH':
            response = requests.patch(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        print(f"{method} {url}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200 or response.status_code == 201:
            print("✅ SUCCESS")
        else:
            print("❌ FAILED")
            print(f"Response: {response.text}")
        print("-" * 50)
        
        return response
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("-" * 50)
        return None

def main():
    """Test all API endpoints."""
    print("🚀 Starting API Endpoint Tests")
    print("=" * 50)
    
    # Test 1: Registration
    print("1. Testing Registration")
    reg_data = {
        "username": "testapi123",
        "password": "testpass123",
        "repeated_password": "testpass123",
        "email": "testapi@example.com",
        "type": "customer"
    }
    reg_response = test_endpoint('POST', f"{BASE_URL}/registration/", reg_data)
    
    token = None
    if reg_response and reg_response.status_code == 201:
        token = reg_response.json().get('token')
        print(f"Token obtained: {token[:20]}...")
    
    # Test 2: Login
    print("2. Testing Login")
    login_data = {
        "username": "testapi123",
        "password": "testpass123"
    }
    login_response = test_endpoint('POST', f"{BASE_URL}/login/", login_data)
    
    # Test 3: Base Info
    print("3. Testing Base Info")
    test_endpoint('GET', f"{BASE_URL}/base-info/")
    
    # Test 4: Profiles (requires auth)
    print("4. Testing Profiles")
    headers = {"Authorization": f"Token {token}"} if token else None
    test_endpoint('GET', f"{BASE_URL}/profiles/", headers=headers)
    
    # Test 5: Offers
    print("5. Testing Offers")
    test_endpoint('GET', f"{BASE_URL}/offers/", headers=headers)
    
    # Test 6: Orders  
    print("6. Testing Orders")
    test_endpoint('GET', f"{BASE_URL}/orders/", headers=headers)
    
    # Test 7: Reviews
    print("7. Testing Reviews")
    test_endpoint('GET', f"{BASE_URL}/reviews/", headers=headers)
    
    # Test 8: Logout
    print("8. Testing Logout")
    test_endpoint('POST', f"{BASE_URL}/logout/", headers=headers)
    
    print("🏁 Testing Complete!")

if __name__ == "__main__":
    main()
