#!/usr/bin/env python3
"""
Start Therapeutic Companion
Easy startup script that handles everything automatically
"""
import os
import sys
import webbrowser
import time
import threading

def open_browser():
    """Open browser after server starts"""
    time.sleep(3)
    webbrowser.open('http://localhost:5000')
    print("\n✅ Browser opened to http://localhost:5000")

def check_dependencies():
    """Check if required packages are installed"""
    missing = []
    
    try:
        import flask
    except ImportError:
        missing.append('flask')
    
    try:
        import flask_cors
    except ImportError:
        missing.append('flask-cors')
    
    try:
        import openpyxl
    except ImportError:
        missing.append('openpyxl')
    
    if missing:
        print("❌ Missing dependencies:", ', '.join(missing))
        print("\n📦 To install, run:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        'therapy_tracker.html',
        'socialworkcountry.py'
    ]
    
    # Check for backend (either one)
    backend_files = ['web_backend.py', 'enhanced_therapy_backend.py']
    backend_found = any(os.path.exists(f) for f in backend_files)
    
    missing = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if not backend_found:
        missing.append('web_backend.py or enhanced_therapy_backend.py')
    
    if missing:
        print("❌ Missing files:", ', '.join(missing))
        return False
    
    return True

def create_directories():
    """Create necessary data directories"""
    directories = [
        'therapy_data',
        'therapy_data/patients',
        'therapy_data/checkins',
        'therapy_data/reports',
        'therapy_data/excel_exports'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Data directories ready")

def main():
    print("=" * 60)
    print("🏥 STARTING THERAPEUTIC COMPANION")
    print("=" * 60)
    
    # Check dependencies
    print("\n📋 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        input("\nPress Enter to exit...")
        return
    print("✅ All dependencies installed")
    
    # Check files
    print("\n📁 Checking files...")
    if not check_files():
        print("\n❌ Please ensure all required files are present")
        input("\nPress Enter to exit...")
        return
    print("✅ All required files found")
    
    # Create directories
    print("\n📂 Setting up data directories...")
    create_directories()
    
    # Start browser in background
    print("\n🌐 Starting web browser...")
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Import and run the backend
    print("\n🚀 Starting Flask server...")
    try:
        # Try to import the appropriate backend
        backend_imported = False
        
        # First try web_backend.py
        if os.path.exists('web_backend.py'):
            try:
                from web_backend import app
                print("✅ Using web_backend.py")
                backend_imported = True
            except Exception as e:
                print(f"⚠️  Could not import web_backend.py: {e}")
        
        # If that fails, try enhanced_therapy_backend.py
        if not backend_imported and os.path.exists('enhanced_therapy_backend.py'):
            try:
                from enhanced_therapy_backend import app
                print("✅ Using enhanced_therapy_backend.py")
                backend_imported = True
            except Exception as e:
                print(f"⚠️  Could not import enhanced_therapy_backend.py: {e}")
        
        if not backend_imported:
            raise ImportError("No working backend found")
        
        print("\n" + "=" * 60)
        print("✅ THERAPEUTIC COMPANION IS RUNNING!")
        print("=" * 60)
        print("\n📱 Access the application at: http://localhost:5000")
        print("\n⚠️  IMPORTANT NOTES:")
        print("   - Use the browser window that opened automatically")
        print("   - Do NOT open therapy_tracker.html directly")
        print("   - Keep this terminal window open")
        print("\n🛑 Press CTRL+C to stop the server")
        print("=" * 60)
        print("\nServer logs will appear below:")
        print("-" * 60)
        
        # Run the Flask app
        app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
        
    except ImportError as e:
        print(f"\n❌ Error importing backend: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure web_backend.py or enhanced_therapy_backend.py exists")
        print("2. Check that the file is not corrupted")
        print("3. Ensure all imports in the backend file are correct")
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        print("✅ Therapeutic Companion shut down successfully")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure no other application is using port 5000")
        print("2. Try running with administrator/sudo privileges if needed")
        print("3. Check the error message above for specific issues")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()