"""
Main runner script for the Therapeutic Social Companion Website
Run this file to start the complete application
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
    print("🏥 THERAPEUTIC SOCIAL COMPANION")
    print("=" * 80)
    print("🚀 Starting complete full-stack application...")
    print("📁 Project directory:", os.getcwd())
    print("🐍 Python version:", sys.version.split()[0])
    print("=" * 80)


def check_files():
    """Check if all required files exist"""
    required_files = [
        'socialworkcountry.py',
        'input_validation.py',
        'enhanced_therapy_backend.py',
        'client.html',
        'requirements.txt'
    ]

    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)

    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n💡 Please ensure all files are in the project directory")
        return False

    print("✅ All required files found")
    return True


def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import flask_cors
        print(f"✅ Flask {flask.__version__} installed")
        print("✅ Flask-CORS installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run in terminal: pip install -r requirements.txt")
        print("💡 Or use: python -m pip install -r requirements.txt")
        return False


def open_browser_delayed():
    """Open browser after a short delay"""
    time.sleep(3)  # Wait for server to start
    print("🌐 Opening browser automatically...")
    try:
        webbrowser.open('http://localhost:5000')
        print("✅ Browser opened successfully")
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print("💡 Manually open: http://localhost:5000")


def start_application():
    """Start the complete application"""
    print_banner()

    # Check prerequisites
    if not check_files():
        input("\nPress Enter to exit...")
        return

    if not check_dependencies():
        input("\nPress Enter to exit...")
        return

    print("\n🔄 Starting Flask backend server...")

    # Schedule browser opening
    browser_thread = threading.Thread(target=open_browser_delayed)
    browser_thread.daemon = True
    browser_thread.start()

    # Import and run the web backend
    try:
        # Add current directory to Python path
        if '.' not in sys.path:
            sys.path.insert(0, '.')

        from enhanced_therapy_backend import app
        print("✅ Web backend imported successfully")
        print("✅ Therapy companion logic loaded")
        print("✅ Social worker assessment logic loaded")
        print("✅ Input validation system loaded")

        print("\n" + "=" * 80)
        print("🌐 WEBSITE IS NOW RUNNING!")
        print("=" * 80)
        print("📱 Main interface: http://localhost:5000")
        print("📊 Features available:")
        print("   - Patient Enrollment")
        print("   - Daily Check-ins (Emotional, Medication, Physical)")
        print("   - Weekly Progress Reports")
        print("   - Excel Export with Tab Separation")
        print("   - Email Report Generation")
        print("   - Social Worker Assessment")
        print("=" * 80)
        print("\n🎯 HOW TO USE:")
        print("1. Enroll patients with therapist information")
        print("2. Collect daily check-ins for 7 days")
        print("3. Generate weekly reports")
        print("4. Export to Excel or email to therapist")
        print("\n🛑 Press CTRL+C to stop the server")
        print("📊 Server logs will appear below:")
        print("-" * 80)

        # Run Flask app
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            use_reloader=False  # Disable reloader to avoid conflicts
        )

    except ImportError as e:
        print(f"❌ Error importing enhanced_therapy_backend: {e}")
        print("💡 Make sure all Python files are in the same directory")
        print("💡 Check that enhanced_therapy_backend.py imports are correct")
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        print("✅ Application shut down successfully")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Check the error details above")
        input("\nPress Enter to exit...")


def show_project_info():
    """Show information about the project structure"""
    print("\n📁 PROJECT STRUCTURE:")
    print("-" * 50)

    files_info = {
        'client.html': 'Web interface with therapy tracking',
        'socialworkcountry.py': 'Social worker assessment logic',
        'input_validation.py': 'Input validation system',
        'enhanced_therapy_backend.py': 'Flask server and API endpoints',
        'requirements.txt': 'Python package dependencies',
        'main.py': 'This runner script'
    }

    for filename, description in files_info.items():
        status = "✅" if Path(filename).exists() else "❌"
        print(f"{status} {filename:<25} - {description}")

    print("\n🔧 SETUP INSTRUCTIONS:")
    print("-" * 50)
    print("1. Install packages: pip install -r requirements.txt")
    print("2. Run this file: python main.py")
    print("3. Website opens automatically in browser")
    print("4. Data is saved locally in therapy_data/ folder")


if __name__ == "__main__":
    try:
        start_application()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        show_project_info()
        input("\nPress Enter to exit...")