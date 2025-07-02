"""
Public Therapeutic Companion Web Backend - Fixed Version
Properly handles HTML serving and API endpoints
"""

from flask import Flask, request, jsonify, send_file, Response, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import os
import io
from datetime import datetime, timedelta
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import tempfile

# Import database models - with fallback for testing
try:
    from database_models import db, Patient, CheckIn, Report, ActivityLog
except ImportError:
    print("Warning: database_models not found, using in-memory storage")
    # Fallback to simple in-memory storage for testing
    db = None

# Import social worker components
try:
    from socialworkcountry import GlobalSocialWorkerChatbot, PatientProfile
except ImportError:
    print("Warning: socialworkcountry not found")
    GlobalSocialWorkerChatbot = None
    PatientProfile = None

# Create Flask app
app = Flask(__name__)
print("Flask app created successfully!")

# Database configuration
if db:
    if os.environ.get('DATABASE_URL'):
        database_url = os.environ.get('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///therapy_data.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        print("Database tables created successfully")

# Configure CORS
CORS(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"]
)

# Initialize chatbot if available
chatbot = GlobalSocialWorkerChatbot() if GlobalSocialWorkerChatbot else None

# In-memory storage fallback
if not db:
    patients_data = {}
    checkins_data = {}
    reports_data = {}


# ============= HELPER FUNCTIONS =============

def get_system_email_config():
    """Get system email configuration"""
    if os.environ.get('SYSTEM_EMAIL') and os.environ.get('SYSTEM_EMAIL_PASSWORD'):
        return {
            'sender_email': os.environ.get('SYSTEM_EMAIL'),
            'sender_password': os.environ.get('SYSTEM_EMAIL_PASSWORD'),
            'smtp_server': os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.environ.get('SMTP_PORT', '587'))
        }
    return None


# ============= MAIN ROUTE - SERVE HTML =============

@app.route('/')
def index():
    """Serve the main HTML file"""
    # Try to find and serve the HTML file
    for filename in ['client.html', 'index.html', 'therapy_tracker.html']:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Only serve if it's actually HTML
                    if content.strip().startswith('<!DOCTYPE') or content.strip().startswith('<html'):
                        return content
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    # If no HTML file found, return a simple page
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Therapeutic Companion</title>
    </head>
    <body>
        <h1>Therapeutic Companion Server Running</h1>
        <p>API Endpoints Available:</p>
        <ul>
            <li>POST /api/therapy/save-patient</li>
            <li>POST /api/therapy/save-checkin</li>
            <li>GET /api/therapy/get-all-patients</li>
            <li>GET /api/therapy/get-week-data/{patient_id}/{week}</li>
            <li>GET /api/therapy/generate-excel-report/{patient_id}/{week}</li>
            <li>POST /api/therapy/email-report</li>
            <li>GET /api/countries</li>
            <li>POST /api/assess</li>
        </ul>
        <p>Please ensure client.html is in the root directory.</p>
    </body>
    </html>
    """


# ============= THERAPY TRACKING ENDPOINTS =============

@app.route('/api/therapy/save-patient', methods=['POST'])
@limiter.limit("50 per hour")
def save_therapy_patient():
    """Save therapy patient enrollment data"""
    try:
        data = request.json
        patient_id = data.get('patientId')
        patient_data = data.get('patientData')

        # Access code validation
        access_code = data.get('accessCode')
        required_code = os.environ.get('ACCESS_CODE', 'therapy2024')

        if access_code != required_code:
            return jsonify({
                'success': False,
                'error': 'Invalid access code'
            }), 403

        if not patient_id or not patient_data:
            return jsonify({
                'success': False,
                'error': 'Missing patient ID or data'
            }), 400

        # Add metadata
        patient_data['enrollmentTimestamp'] = datetime.now().isoformat()
        patient_data['weeklyReports'] = []

        if db:
            # Database storage
            patient = Patient.query.get(patient_id)
            if patient:
                patient.set_data(patient_data)
            else:
                patient = Patient(id=patient_id)
                patient.set_data(patient_data)
                db.session.add(patient)
            db.session.commit()
        else:
            # In-memory storage
            patients_data[patient_id] = patient_data

        return jsonify({
            'success': True,
            'message': 'Patient enrolled successfully',
            'patient_id': patient_id
        })

    except Exception as e:
        if db:
            db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/therapy/save-checkin', methods=['POST'])
@limiter.limit("200 per hour")
def save_therapy_checkin():
    """Save daily check-in data"""
    try:
        data = request.json
        patient_id = data.get('patientId')
        checkin_data = data.get('checkinData')

        if not patient_id or not checkin_data:
            return jsonify({
                'success': False,
                'error': 'Missing patient ID or check-in data'
            }), 400

        # Validate required fields
        required_fields = ['date', 'time', 'emotional', 'medication', 'activity']
        for field in required_fields:
            if field not in checkin_data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        # Add metadata
        checkin_data['serverTimestamp'] = datetime.now().isoformat()

        date = checkin_data.get('date')

        if db:
            # Database storage
            patient = Patient.query.get(patient_id)
            if not patient:
                return jsonify({'success': False, 'error': 'Patient not found'}), 404

            checkin = CheckIn.query.filter_by(patient_id=patient_id, date=date).first()
            if checkin:
                checkin.set_data(checkin_data)
            else:
                checkin = CheckIn(patient_id=patient_id, date=date)
                checkin.set_data(checkin_data)
                db.session.add(checkin)
            db.session.commit()
        else:
            # In-memory storage
            if patient_id not in patients_data:
                return jsonify({'success': False, 'error': 'Patient not found'}), 404

            if patient_id not in checkins_data:
                checkins_data[patient_id] = {}
            checkins_data[patient_id][date] = checkin_data

        return jsonify({
            'success': True,
            'message': 'Daily check-in saved successfully',
            'date': date
        })

    except Exception as e:
        if db:
            db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/therapy/get-week-data/<patient_id>/<week>', methods=['GET'])
def get_week_data(patient_id, week):
    """Get all check-in data for a specific week"""
    try:
        week_data = {}

        # Parse week string
        year, week_num = week.split('-W')
        year = int(year)
        week_num = int(week_num)

        # Calculate week dates
        jan_4 = datetime(year, 1, 4)
        week_1_monday = jan_4 - timedelta(days=jan_4.weekday())
        week_start = week_1_monday + timedelta(weeks=week_num - 1)

        # Get data for each day
        for i in range(7):
            date = week_start + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')

            if db:
                checkin = CheckIn.query.filter_by(patient_id=patient_id, date=date_str).first()
                if checkin:
                    week_data[date_str] = checkin.get_data()
            else:
                if patient_id in checkins_data and date_str in checkins_data[patient_id]:
                    week_data[date_str] = checkins_data[patient_id][date_str]

        return jsonify({
            'success': True,
            'weekData': week_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/therapy/get-all-patients', methods=['GET'])
def get_all_therapy_patients():
    """Get list of all enrolled patients"""
    try:
        patients = []

        if db:
            all_patients = Patient.query.all()
            for patient in all_patients:
                patient_data = patient.get_data()
                patient_data['patientId'] = patient.id
                patients.append(patient_data)
        else:
            for patient_id, patient_data in patients_data.items():
                data = patient_data.copy()
                data['patientId'] = patient_id
                patients.append(data)

        return jsonify({
            'success': True,
            'patients': patients
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/therapy/generate-excel-report/<patient_id>/<week>', methods=['GET'])
@limiter.limit("30 per hour")
def generate_excel_report(patient_id, week):
    """Generate Excel report for a patient's week"""
    try:
        # Get patient data
        if db:
            patient = Patient.query.get(patient_id)
            if not patient:
                return jsonify({'success': False, 'error': 'Patient not found'}), 404
            patient_data = patient.get_data()
        else:
            if patient_id not in patients_data:
                return jsonify({'success': False, 'error': 'Patient not found'}), 404
            patient_data = patients_data[patient_id]

        patient_data['patientId'] = patient_id

        # Get week data
        week_response = get_week_data(patient_id, week)
        week_data_json = week_response.get_json()
        week_data = week_data_json.get('weekData', {})

        # Create Excel workbook
        wb = openpyxl.Workbook()

        # Create Summary Sheet
        summary_sheet = wb.active
        summary_sheet.title = "Weekly Summary"

        # Add patient information
        summary_sheet['A1'] = "WEEKLY THERAPY TRACKING REPORT"
        summary_sheet['A1'].font = Font(bold=True, size=16)
        summary_sheet.merge_cells('A1:F1')

        summary_sheet['A3'] = "Patient Information"
        summary_sheet['A3'].font = Font(bold=True, size=12)

        patient_info_rows = [
            ("Patient ID:", patient_data['patientId']),
            ("Patient Name:", patient_data['name']),
            ("Therapist:", patient_data['therapistName']),
            ("Therapist Email:", patient_data['therapistEmail']),
            ("Week:", week),
            ("Report Generated:", datetime.now().strftime("%Y-%m-%d %H:%M"))
        ]

        row = 4
        for label, value in patient_info_rows:
            summary_sheet[f'A{row}'] = label
            summary_sheet[f'B{row}'] = value
            summary_sheet[f'A{row}'].font = Font(bold=True)
            row += 1

        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        wb.save(temp_file.name)
        temp_file.close()

        # Send file
        response = send_file(
            temp_file.name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"therapy_report_{patient_id}_{week}.xlsx"
        )

        # Clean up
        os.unlink(temp_file.name)

        return response

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/therapy/email-report', methods=['POST'])
@limiter.limit("20 per hour")
def email_therapy_report():
    """Send therapy report via email"""
    try:
        data = request.json
        patient_id = data.get('patientId')
        week = data.get('week')

        # For now, just return a success message
        # Email functionality would go here

        return jsonify({
            'success': True,
            'message': 'Email functionality not configured',
            'note': 'Please configure SYSTEM_EMAIL environment variables'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============= SOCIAL WORKER ASSESSMENT ENDPOINTS =============

@app.route('/api/countries', methods=['GET'])
def get_countries():
    """Get list of available countries"""
    try:
        if not chatbot:
            # Return default countries if chatbot not available
            countries = [
                {'code': 'united_states', 'name': 'United States', 'key': '1'},
                {'code': 'canada', 'name': 'Canada', 'key': '2'},
                {'code': 'united_kingdom', 'name': 'United Kingdom', 'key': '3'},
                {'code': 'australia', 'name': 'Australia', 'key': '4'},
                {'code': 'germany', 'name': 'Germany', 'key': '5'},
                {'code': 'japan', 'name': 'Japan', 'key': '6'},
                {'code': 'india', 'name': 'India', 'key': '7'},
                {'code': 'brazil', 'name': 'Brazil', 'key': '8'},
                {'code': 'south_africa', 'name': 'South Africa', 'key': '9'},
                {'code': 'sweden', 'name': 'Sweden', 'key': '10'},
                {'code': 'israel', 'name': 'Israel', 'key': '11'},
                {'code': 'france', 'name': 'France', 'key': '12'}
            ]
        else:
            countries = []
            for key, (code, name) in chatbot.get_country_list().items():
                countries.append({
                    'code': code,
                    'name': name,
                    'key': key
                })

        return jsonify({
            'success': True,
            'countries': countries
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/assess', methods=['POST'])
@limiter.limit("50 per hour")
def assess_patient():
    """Run social worker assessment"""
    try:
        if not chatbot or not PatientProfile:
            return jsonify({
                'success': False,
                'error': 'Assessment module not available'
            }), 503

        data = request.json

        # Create PatientProfile
        patient = PatientProfile(
            name=data['name'],
            age=int(data['age']),
            country=data['country'],
            city=data['city'],
            gender=data['gender'],
            employment_status=data['employment'],
            exercise_level=data['exercise'],
            mental_state=data['mental'],
            financial_status=data['financial'],
            additional_notes=data.get('notes', '')
        )

        # Run assessments
        chatbot.current_patient = patient
        country_health_needs = chatbot.assess_country_specific_health_needs(patient)
        country_safety_needs = chatbot.assess_country_specific_safety_needs(patient)
        country_evidence_recs = chatbot.generate_country_evidence_recommendations(patient)
        general_recommendations = chatbot.generate_comprehensive_recommendations(patient)

        # Get country context
        country_data = chatbot.health_db.country_health_data.get(patient.country, {})

        # Prepare response
        result = {
            'success': True,
            'patient_profile': {
                'name': patient.name,
                'age': patient.age,
                'country': patient.country,
                'city': patient.city,
                'gender': patient.gender,
                'employment_status': patient.employment_status,
                'financial_status': patient.financial_status,
                'exercise_level': patient.exercise_level,
                'mental_state': patient.mental_state
            },
            'country_context': {
                'name': patient.country.replace('_', ' ').title(),
                'mental_health_prevalence': country_data.get('mental_health_prevalence', 0.20) * 100,
                'healthcare_system': country_data.get('healthcare_system', 'Unknown').replace('_', ' ').title(),
                'common_health_issues': country_data.get('common_health_issues', []),
                'crisis_resources': country_data.get('crisis_resources', [])
            },
            'risk_indicators': {
                'level': 'critical' if patient.mental_state == 'Critical' else
                'high' if patient.mental_state == 'Poor' else
                'moderate' if patient.mental_state == 'Fair' else 'low',
                'requires_immediate_attention': patient.mental_state in ['Critical', 'Poor']
            },
            'assessments': {
                'country_health_needs': country_health_needs,
                'country_safety_needs': country_safety_needs,
                'country_evidence_recommendations': country_evidence_recs,
                'general_recommendations': general_recommendations
            },
            'age_category': chatbot.determine_age_category(patient.age),
            'city_category': chatbot.determine_city_category(patient.city, patient.country),
            'timestamp': datetime.now().isoformat()
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============= HEALTH CHECK ENDPOINT =============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Therapeutic Companion Backend',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if db else 'in-memory',
        'features': {
            'therapy_tracking': True,
            'social_assessment': bool(chatbot),
            'email_reports': bool(get_system_email_config())
        }
    })


# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(e):
    # For API routes, return JSON
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Endpoint not found',
            'path': request.path
        }), 404
    # For other routes, return HTML
    return index()


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.'
    }), 429


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == "__main__":
    print("=" * 80)
    print("🏥 THERAPEUTIC COMPANION SYSTEM")
    print("=" * 80)
    print("✅ Server initialized")
    print("✅ API endpoints ready")
    print("✅ Database:", "PostgreSQL/SQLite" if db else "In-memory storage")
    print("✅ Social assessment:", "Available" if chatbot else "Not available")
    print("\n🌐 Server running at: http://localhost:5000")
    print("=" * 80)

    # Run server
    if os.environ.get('PRODUCTION'):
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    else:
        app.run(host='127.0.0.1', port=5000, debug=True)