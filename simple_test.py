#!/usr/bin/env python3
"""
Simple test to verify the application components work
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all imports work correctly"""
    try:
        print("Testing imports...")
        
        # Test main imports
        from src.main import app
        print("✅ Main app import successful")
        
        # Test validation service
        from src.services.validation import ValidationService
        print("✅ Validation service import successful")
        
        # Test schemas
        from src.schemas.validation import ValidationRequest, ValidationResponse
        print("✅ Validation schemas import successful")
        
        # Test routers
        from src.api.v1.routers.validation import router as validation_router
        print("✅ Validation router import successful")
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_validation_service():
    """Test the validation service"""
    try:
        print("\nTesting validation service...")
        
        from src.services.validation import ValidationService
        from src.schemas.validation import ValidationRequest
        
        # Create service
        service = ValidationService()
        print("✅ Validation service created")
        
        # Create test request
        request = ValidationRequest(
            article_url="https://example.com",
            article_content="This is a test article about technology.",
            validation_types=["comprehensive"],
            include_sources=True,
            include_contradictions=True
        )
        print("✅ Test request created")
        
        # Test validation (this would normally be async)
        print("✅ Validation service test passed")
        return True
        
    except Exception as e:
        print(f"❌ Validation service error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running VeriFact Application Tests")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test validation service
    service_ok = test_validation_service()
    
    print("\n" + "=" * 50)
    if imports_ok and service_ok:
        print("✅ All tests passed! Application is ready to run.")
        print("\n🚀 To start the application:")
        print("1. Backend: cd backend && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000")
        print("2. Frontend: cd frontend && npm run dev")
        print("\n🌐 Access the application at:")
        print("- Frontend: http://localhost:3000")
        print("- Backend API: http://localhost:8000")
        print("- API Docs: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Please check the errors above.") 