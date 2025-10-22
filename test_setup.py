#!/usr/bin/env python3
"""
Test script to verify RiskIQ setup for HF Spaces
"""

import sys
import os
from pathlib import Path


def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")

    try:
        import fastapi

        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False

    try:
        import uvicorn

        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False

    try:
        import pandas

        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False

    try:
        import numpy

        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False

    try:
        import yfinance

        print("✅ yfinance imported successfully")
    except ImportError as e:
        print(f"❌ yfinance import failed: {e}")
        return False

    return True


def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing file structure...")

    required_files = [
        "app.py",
        "requirements.txt",
        "README.md",
        "Dockerfile",
        "backend/api/app.py",
        "backend/api/risk_models.py",
        "backend/api/risk_summary.py",
        "backend/api/fetch_data.py",
        "frontend/index.html",
        "frontend/styles.css",
        "frontend/script.js",
    ]

    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False

    return all_exist


def test_backend_imports():
    """Test that backend modules can be imported"""
    print("\n🔧 Testing backend imports...")

    try:
        # Add backend to path
        sys.path.insert(0, str(Path("backend")))

        from backend.api.risk_models import get_risk_metrics

        print("✅ risk_models imported successfully")

        from backend.api.risk_summary import generate_ai_summary, get_risk_level

        print("✅ risk_summary imported successfully")

        from backend.api.fetch_data import prepare_data

        print("✅ fetch_data imported successfully")

        return True
    except ImportError as e:
        print(f"❌ Backend import failed: {e}")
        return False


def test_app_creation():
    """Test that the main app can be created"""
    print("\n🚀 Testing app creation...")

    try:
        from app import app

        print("✅ Main app created successfully")

        # Test that routes exist
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/docs"]

        for route in expected_routes:
            if route in routes:
                print(f"✅ Route {route} exists")
            else:
                print(f"❌ Route {route} missing")
                return False

        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 RiskIQ Setup Test for HF Spaces")
    print("=" * 60)

    tests = [test_file_structure, test_imports, test_backend_imports, test_app_creation]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Ready for HF Spaces deployment.")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
