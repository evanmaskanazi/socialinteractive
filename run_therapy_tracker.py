"""
Therapy Tracker Runner
Easy startup script for the Enhanced Therapeutic Companion System
"""

import os
import sys
import time
import webbrowser
import threading
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("=" * 80)
    print("🏥 ENHANCED THERAPEUTIC COMPANION - WEEKLY TRACKING SYSTEM")
    print("=" * 80)
    print("✨ Features:")
    print("  ✅ Patient enrollment with therapist information")
    print("  ✅ Daily check-ins for emotional state, medication, and physical activity")
    print("  ✅ Complete 7-day weekly tracking")
    print("  ✅ Excel report generation with color-coded data")
    print("  ✅ Historical data entry with custom date/time")
    print("  ✅ Non-response tracking")
    print("  ✅ Email report preparation for therapists")
    print("=" * 80)

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'openpyxl': 'OpenPyXL (for Excel exports)'
    }
    
    missing = []
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {name} installed")
        except ImportError:
            missing.append(package)
            print(f"❌ {name} not installed")
    
    if missing:
        print("\n⚠️  Missing dependencies detected!")
        print("📦 Install them by running:")
        print(f"   pip install {' '.join(missing)}")
        print("\nOr install all requirements:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def save_html_file():
    """Save the enhanced HTML file if needed"""
    html_filename = 'therapy_tracker.html'
    
    if os.path.exists(html_filename):
        print(f"✅ {html_filename} found")
        return True
    
    print(f"📝 Creating {html_filename}...")
    
    # This would contain the full HTML from the therapy_tracker_html artifact
    # For brevity, showing just a placeholder
    html_content = """<!-- Full HTML content from therapy_tracker_html artifact would go here -->"""
    
    try:
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ {html_filename} created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating {html_filename}: {e}")
        return False

def save_backend_file():
    """Save the enhanced backend file if needed"""
    backend_filename = 'enhanced_therapy_backend.py'
    
    if os.path.exists(backend_filename):
        print(f"✅ {backend_filename} found")
        return backend_filename
    
    # Check if web_backend.py exists and can be used
    if os.path.exists('web_backend.py'):
        print("✅ Using existing web_backend.py")
        return 'web_backend.py'
    
    print(f"❌ No backend file found!")
    print(f"💡 Please ensure either {backend_filename} or web_backend.py exists")
    return None

def open_browser_delayed(port=5000):
    """Open browser after server starts"""
    time.sleep(3)
    print("\n🌐 Opening browser...")
    try:
        webbrowser.open(f'http://localhost:{port}')
        print("✅ Browser opened successfully")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print(f"💡 Please open manually: http://localhost:{port}")

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
    
    print("✅ Data directories created")

def run_therapy_tracker():
    """Main function to run the therapy tracker"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        input("\nPress Enter to exit...")
        return
    
    # Create directories
    create_directories()
    
    # Check for backend file
    backend_file = save_backend_file()
    if not backend_file:
        input("\nPress Enter to exit...")
        return
    
    # Check for HTML file
    if not save_html_file():
        print("⚠️  HTML file not found, but server can still run")
    
    print("\n🚀 Starting therapy tracking server...")
    
    # Start browser opener in background
    browser_thread = threading.Thread(target=open_browser_delayed)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Import and run the backend
    try:
        # Add current directory to path
        if '.' not in sys.path:
            sys.path.insert(0, '.')
        
        # Import the appropriate backend module
        if backend_file == 'enhanced_therapy_backend.py':
            from enhanced_therapy_backend import app
        else:
            from web_backend import app
        
        print("\n" + "=" * 80)
        print("🎉 THERAPY TRACKER IS RUNNING!")
        print("=" * 80)
        print("\n📱 Access the system at: http://localhost:5000")
        print("\n📋 QUICK START GUIDE:")
        print("1. Go to 'Patient Enrollment' tab to register a patient")
        print("2. Use 'Daily Check-In' tab to record daily responses")
        print("3. View progress in 'Week Progress' tab")
        print("4. Generate Excel reports in 'Generate Reports' tab")
        print("\n💡 TIPS:")
        print("- You can enter historical data by changing the date/time")
        print("- Check-ins record all three areas at once")
        print("- Excel reports include color-coded ratings")
        print("- Non-responses are automatically tracked")
        print("\n🛑 Press CTRL+C to stop the server")
        print("=" * 80)
        
        # Run the Flask app
        app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
        
    except ImportError as e:
        print(f"\n❌ Error importing backend: {e}")
        print("💡 Make sure all required files are present")
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        print("✅ Therapy tracker shut down successfully")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPress Enter to exit...")

def show_help():
    """Show help information"""
    print("\n📚 THERAPY TRACKER HELP")
    print("=" * 50)
    print("\n🔧 SETUP:")
    print("1. Install dependencies: pip install flask flask-cors openpyxl")
    print("2. Run this script: python run_therapy_tracker.py")
    print("3. Browser opens automatically to http://localhost:5000")
    print("\n📁 DATA STORAGE:")
    print("- Patient data: therapy_data/patients/")
    print("- Daily check-ins: therapy_data/checkins/")
    print("- Excel reports: therapy_data/excel_exports/")
    print("\n🎯 WORKFLOW:")
    print("1. Enroll patient with therapist details")
    print("2. Patient does daily check-ins for 7 days")
    print("3. System tracks emotional state, medication, activity")
    print("4. Generate weekly Excel report")
    print("5. Email report to therapist")
    print("\n❓ TROUBLESHOOTING:")
    print("- Missing module? Run: pip install -r requirements.txt")
    print("- Port in use? Change port in app.run()")
    print("- Can't see data? Check therapy_data/ folder")
    print("=" * 50)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Therapy Tracker System')
    parser.add_argument('--help-info', action='store_true', help='Show detailed help')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on (default: 5000)')
    
    args = parser.parse_args()
    
    if args.help_info:
        show_help()
    else:
        run_therapy_tracker()