#!/usr/bin/env python3
"""
Verify Therapy System Setup
This script checks that everything is configured correctly
"""

import os
import sys
import subprocess
import time

def check_files():
    """Check if all required files exist"""
    print("=" * 60)
    print("CHECKING FILES...")
    print("=" * 60)
    
    required_files = {
        'app.py': False,
        'web_backend.py': False,
        'therapy_tracker.html': False,
        'socialworkcountry.py': False
    }
    
    for filename in required_files:
        if os.path.exists(filename):
            required_files[filename] = True
            print(f"✅ {filename} found")
        else:
            print(f"❌ {filename} NOT FOUND")
    
    return all(required_files.values())

def test_backend():
    """Test if the backend can be imported"""
    print("\n" + "=" * 60)
    print("TESTING BACKEND...")
    print("=" * 60)
    
    try:
        # Try to import the backend
        if os.path.exists('web_backend.py'):
            from web_backend import app
            print("✅ web_backend.py imported successfully")
            
            # Check if therapy endpoints exist
            with app.test_client() as client:
                # Test health endpoint
                response = client.get('/api/health')
                if response.status_code == 200:
                    print("✅ Backend health check passed")
                else:
                    print("❌ Backend health check failed")
                    
            return True
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def create_startup_script():
    """Create a simple startup script"""
    print("\n" + "=" * 60)
    print("CREATING STARTUP SCRIPT...")
    print("=" * 60)
    
    startup_content = '''#!/usr/bin/env python3
"""
Start Therapeutic Companion
"""
import os
import sys
import webbrowser
import time
import threading

def open_browser():
    time.sleep(3)
    webbrowser.open('http://localhost:5000')
    print("\\n✅ Browser opened to http://localhost:5000")

print("=" * 60)
print("🏥 STARTING THERAPEUTIC COMPANION")
print("=" * 60)

# Start browser in background
browser_thread = threading.Thread(target=open_browser)
browser_thread.daemon = True
browser_thread.start()

# Import and run the backend
try:
    from web_backend import app
    print("\\n✅ Backend loaded successfully")
    print("🌐 Server starting at http://localhost:5000")
    print("\\n⚠️  IMPORTANT: Use the browser that opens automatically")
    print("   Do NOT open therapy_tracker.html directly!")
    print("=" * 60)
    
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
except Exception as e:
    print(f"\\n❌ Error: {e}")
    print("\\nTroubleshooting:")
    print("1. Make sure all files are in the same directory")
    print("2. Install dependencies: pip install flask flask-cors openpyxl")
    input("\\nPress Enter to exit...")
'''
    
    with open('start_therapy.py', 'w') as f:
        f.write(startup_content)
    
    print("✅ Created start_therapy.py")
    return True

def main():
    print("\n🔍 THERAPEUTIC COMPANION - SETUP VERIFICATION\n")
    
    # Check files
    files_ok = check_files()
    
    # Test backend
    backend_ok = test_backend()
    
    # Create startup script
    script_created = create_startup_script()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if files_ok and backend_ok:
        print("\n✅ SYSTEM READY!")
        print("\nTo start the application:")
        print("1. Run: python start_therapy.py")
        print("2. Wait for browser to open automatically")
        print("3. Use the application at http://localhost:5000")
        print("\n⚠️  IMPORTANT: Do NOT open therapy_tracker.html directly!")
        print("   Always access through http://localhost:5000")
    else:
        print("\n❌ ISSUES FOUND")
        print("\nPlease ensure:")
        print("1. All files are in the same directory")
        print("2. Dependencies are installed: pip install flask flask-cors openpyxl")
        print("3. No other application is using port 5000")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()