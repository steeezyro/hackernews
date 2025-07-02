#!/usr/bin/env python3
"""
Deployment verification script to test if the application is ready for production.
"""

import os
import sys
import json
from pathlib import Path

def test_backend_structure():
    """Test backend file structure and dependencies"""
    print("🔍 Testing Backend Structure...")
    
    backend_path = Path("backend")
    required_files = [
        "main.py",
        "requirements.txt", 
        "src/models/article.py",
        "src/services/scraper.py",
        "src/services/cache.py",
        "src/utils/rate_limiter.py",
        "src/utils/logger.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (backend_path / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing backend files: {missing_files}")
        return False
    
    print("✅ Backend structure is correct")
    return True

def test_frontend_structure():
    """Test frontend file structure and build"""
    print("🔍 Testing Frontend Structure...")
    
    frontend_path = Path("frontend")
    required_files = [
        "package.json",
        "tsconfig.json",
        "src/App.tsx",
        "src/main.tsx",
        "src/types/index.ts",
        "src/hooks/useArticles.ts",
        "src/components/Header.tsx",
        "src/components/ArticleCard.tsx"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (frontend_path / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing frontend files: {missing_files}")
        return False
        
    # Check if build output exists
    if not (frontend_path / "dist").exists():
        print("⚠️  Frontend not built yet - run 'npm run build' in frontend/")
        return False
    
    print("✅ Frontend structure is correct")
    return True

def test_environment_variables():
    """Test required environment variables"""
    print("🔍 Testing Environment Configuration...")
    
    # Check root .env (where GEMINI_API_KEY is stored)
    root_env = Path(".env")
    if not root_env.exists():
        print("⚠️  Root .env file missing - create with GEMINI_API_KEY")
        return False
    else:
        # Check if GEMINI_API_KEY exists in root .env
        content = root_env.read_text()
        if "GEMINI_API_KEY" in content:
            print("✅ GEMINI_API_KEY found in root .env")
        else:
            print("⚠️  GEMINI_API_KEY not found in .env")
            return False
        
    # Check frontend .env
    frontend_env = Path("frontend/.env")
    if not frontend_env.exists():
        print("⚠️  Frontend .env file missing - create with VITE_API_URL")
        return False
    else:
        content = frontend_env.read_text()
        if "VITE_API_URL" in content:
            print("✅ VITE_API_URL found in frontend/.env")
        else:
            print("⚠️  VITE_API_URL not found in frontend/.env")
            return False
    
    print("✅ All environment variables configured")
    return True

def test_deployment_ready():
    """Test if ready for deployment"""
    print("🔍 Testing Deployment Readiness...")
    
    # Check CORS configuration
    main_py = Path("backend/main.py")
    if main_py.exists():
        content = main_py.read_text()
        if "hackernews-1.onrender.com" in content:
            print("✅ CORS configured for production domain")
        else:
            print("⚠️  Update CORS origins for your production domain")
    
    # Check if frontend points to correct API
    package_json = Path("frontend/package.json") 
    if package_json.exists():
        data = json.loads(package_json.read_text())
        print(f"✅ Frontend build script: {data.get('scripts', {}).get('build', 'Not found')}")
    
    return True

def main():
    """Run all tests"""
    print("🚀 HackerNews Deployment Verification\n")
    
    tests = [
        test_backend_structure,
        test_frontend_structure, 
        test_environment_variables,
        test_deployment_ready
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    print("📊 SUMMARY:")
    print(f"✅ {sum(results)} tests passed")
    print(f"❌ {len(results) - sum(results)} tests failed")
    
    if all(results):
        print("\n🎉 Application is ready for deployment!")
        print("\nNext steps:")
        print("1. Set GEMINI_API_KEY in your backend environment")
        print("2. Set VITE_API_URL in your frontend environment")
        print("3. Run 'npm run build' in frontend/ if not done")
        print("4. Deploy backend with uvicorn main:app --host 0.0.0.0 --port 8000")
        print("5. Deploy frontend dist/ folder to static hosting")
    else:
        print("\n⚠️  Fix the issues above before deploying")
        
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)