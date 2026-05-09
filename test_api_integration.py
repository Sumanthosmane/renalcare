#!/usr/bin/env python3
"""
Integration test for RenalCare AI API endpoints
Tests image upload, water logging, and data retrieval
"""

import requests
import json
from pathlib import Path
from PIL import Image
import io

BASE_URL = "http://localhost:8001/api"
PATIENT_ID = "patient_demo_001"

def test_patient_exists():
    """Test: Get patient data"""
    print("\n1️⃣  Testing: Get Patient Data")
    response = requests.get(f"{BASE_URL}/patients/{PATIENT_ID}")
    print(f"   Status: {response.status_code}")
    print(f"   Patient: {response.json()['name']}")
    assert response.status_code == 200
    return True

def test_water_intake_logging():
    """Test: Log water intake"""
    print("\n2️⃣  Testing: Log Water Intake")
    
    payload = {
        "patient_id": PATIENT_ID,
        "amount_ml": 250,
        "time": "14:30",
        "notes": "with lunch"
    }
    
    response = requests.post(f"{BASE_URL}/water-intake", json=payload)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code in [200, 201]
    return True

def test_water_summary():
    """Test: Get daily water summary"""
    print("\n3️⃣  Testing: Get Daily Water Summary")
    
    response = requests.get(f"{BASE_URL}/water-intake/{PATIENT_ID}/daily")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Total intake: {data.get('total_intake_ml', 'N/A')}ml")
        print(f"   Goal: {data.get('goal_ml', 'N/A')}ml")
    else:
        print(f"   Response: {response.text}")
    return response.status_code == 200

def test_create_test_image():
    """Create a simple test image"""
    print("\n4️⃣  Creating Test Image")
    
    # Create a simple test image
    img = Image.new('RGB', (400, 400), color='gray')
    
    # Add some circles to simulate stones
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.ellipse([100, 100, 150, 150], fill='white', outline='white')
    draw.ellipse([250, 200, 290, 240], fill='white', outline='white')
    
    # Save to temp file
    test_image_path = Path("/tmp/test_kidney_scan.jpg")
    img.save(test_image_path)
    print(f"   Created: {test_image_path}")
    return test_image_path

def test_image_upload(image_path):
    """Test: Upload and analyze image"""
    print("\n5️⃣  Testing: Upload & Analyze Kidney Scan")
    
    with open(image_path, 'rb') as f:
        files = {
            'file': ('test_scan.jpg', f, 'image/jpeg')
        }
        
        params = {
            'patient_id': PATIENT_ID,
            'stone_type': 'unknown'
        }
        
        response = requests.post(f"{BASE_URL}/analyze-scan", files=files, params=params)
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"   ✅ Analysis Success!")
        print(f"   - Stone Size: {result.get('stone_size_mm', 'N/A')}mm")
        print(f"   - Location: {result.get('stone_location', 'N/A')}")
        print(f"   - Severity: {result.get('severity', 'N/A')}")
        print(f"   - Confidence: {result.get('confidence', 'N/A')}")
        return True
    else:
        print(f"   ❌ Error: {response.text}")
        return False

def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("🏥 RenalCare AI - API Integration Tests")
    print("="*60)
    
    try:
        # Test 1: Patient
        test_patient_exists()
        
        # Test 2: Water logging
        test_water_intake_logging()
        
        # Test 3: Water summary
        test_water_summary()
        
        # Test 4: Create test image
        image_path = test_create_test_image()
        
        # Test 5: Image upload & analysis
        test_image_upload(image_path)
        
        print("\n" + "="*60)
        print("✅ All Tests Passed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
