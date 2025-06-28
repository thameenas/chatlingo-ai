#!/usr/bin/env python3
"""
Test script for the daily nudge functionality
Run this to manually trigger nudges for testing
"""

import requests
import json

def test_manual_nudge():
    """Test the manual nudge endpoint"""
    try:
        # Test the manual nudge endpoint
        response = requests.post('http://localhost:8000/api/nudges/send')
        
        if response.status_code == 200:
            print("✅ Nudge test successful!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Nudge test failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Flask app is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error testing nudges: {str(e)}")

if __name__ == "__main__":
    print("Testing daily nudge functionality...")
    test_manual_nudge() 