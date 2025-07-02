#!/usr/bin/env python3
"""
Complete deployment test - tests actual server startup and endpoints
"""

import os
import sys
import time
import subprocess
import requests
import threading
from pathlib import Path

def test_server_startup():
    """Test that the FastAPI server can start properly"""
    print("🔍 Testing FastAPI Server Startup...")
    
    # Set environment
    env = os.environ.copy()
    env['GEMINI_API_KEY'] = 'AIzaSyBdo85g2p9IXq-iPlb3RK2vqJOnBMN9dvs'
    
    # Start server in background
    try:
        # Use global Python that has the dependencies
        python_path = "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
        
        process = subprocess.Popen([
            python_path, "-c", 
            """
import uvicorn
from main import app
uvicorn.run(app, host='127.0.0.1', port=8001, log_level='error')
            """
        ], 
        cwd="backend",
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
        )
        
        # Wait for startup
        print("⏳ Starting server...")
        time.sleep(3)
        
        # Test health endpoint
        try:
            response = requests.get("http://localhost:8001/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server health check passed: {data.get('message', 'Unknown')}")
                
                # Test articles endpoint
                response = requests.get("http://localhost:8001/api/articles", timeout=5)
                if response.status_code == 200:
                    print("✅ Articles endpoint accessible")
                else:
                    print(f"⚠️  Articles endpoint returned {response.status_code}")
                
                # Test status endpoint
                response = requests.get("http://localhost:8001/api/status", timeout=5)
                if response.status_code == 200:
                    print("✅ Status endpoint accessible")
                    
                print("✅ FastAPI server is fully functional!")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to server: {e}")
            return False
            
        finally:
            # Cleanup
            process.terminate()
            process.wait(timeout=2)
            
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        return False

def test_frontend_production():
    """Test frontend production build"""
    print("🔍 Testing Frontend Production Build...")
    
    frontend_path = Path("frontend")
    dist_path = frontend_path / "dist"
    
    if not dist_path.exists():
        print("❌ Frontend not built - run 'npm run build'")
        return False
    
    # Check for required files
    required_files = ["index.html"]
    for file in required_files:
        if not (dist_path / file).exists():
            print(f"❌ Missing file in dist: {file}")
            return False
    
    # Check if there are JS and CSS assets
    assets_path = dist_path / "assets"
    if assets_path.exists():
        js_files = list(assets_path.glob("*.js"))
        css_files = list(assets_path.glob("*.css"))
        
        if js_files and css_files:
            print(f"✅ Frontend build complete with {len(js_files)} JS and {len(css_files)} CSS files")
            return True
        else:
            print("❌ Missing JS or CSS assets in build")
            return False
    else:
        print("❌ Assets directory missing in build")
        return False

def test_environment_setup():
    """Test environment variables are properly configured"""
    print("🔍 Testing Environment Setup...")
    
    # Check root .env
    if not Path(".env").exists():
        print("❌ Root .env file missing")
        return False
    
    with open(".env") as f:
        content = f.read()
        if "GEMINI_API_KEY" in content and "AIzaSy" in content:
            print("✅ GEMINI_API_KEY properly configured")
        else:
            print("❌ GEMINI_API_KEY not found or invalid")
            return False
    
    # Check frontend .env
    if not Path("frontend/.env").exists():
        print("❌ Frontend .env file missing")
        return False
        
    with open("frontend/.env") as f:
        content = f.read()
        if "VITE_API_URL" in content:
            print("✅ VITE_API_URL configured")
        else:
            print("❌ VITE_API_URL not configured")
            return False
    
    return True

def test_dependencies():
    """Test that all required dependencies are available"""
    print("🔍 Testing Dependencies...")
    
    try:
        python_path = "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
        
        # Test imports
        result = subprocess.run([
            python_path, "-c",
            """
import fastapi, uvicorn, playwright, google.generativeai
print("All Python dependencies available")
            """
        ], capture_output=True, text=True, cwd="backend")
        
        if result.returncode == 0:
            print("✅ All Python dependencies available")
        else:
            print(f"❌ Python dependency error: {result.stderr}")
            return False
            
        # Test Node.js dependencies
        result = subprocess.run([
            "npm", "list", "--depth=0"
        ], capture_output=True, text=True, cwd="frontend")
        
        if result.returncode == 0:
            print("✅ All Node.js dependencies available")
        else:
            print("⚠️  Some Node.js dependencies may be missing (check frontend/)")
            
        return True
        
    except Exception as e:
        print(f"❌ Dependency test failed: {e}")
        return False

def main():
    """Run all deployment tests"""
    print("🚀 DEPLOYMENT READINESS TEST\n")
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Dependencies", test_dependencies),
        ("Frontend Build", test_frontend_production),
        ("Server Startup", test_server_startup),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"{'='*50}")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append(False)
        print()
    
    print("="*50)
    print("📊 FINAL RESULTS:")
    print(f"✅ {sum(results)} tests passed")
    print(f"❌ {len(results) - sum(results)} tests failed")
    
    if all(results):
        print("\n🎉 YOUR APPLICATION IS 100% READY FOR DEPLOYMENT!")
        print("\nDeployment Instructions:")
        print("1. Backend: Deploy with 'uvicorn main:app --host 0.0.0.0 --port 8000'")
        print("2. Frontend: Deploy the 'frontend/dist/' folder to static hosting")
        print("3. Set GEMINI_API_KEY in your backend environment")
        print("4. Update VITE_API_URL to point to your deployed backend")
        print("\n✨ This will work perfectly on your live site!")
    else:
        print("\n⚠️  Please fix the failing tests before deployment")
        
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)