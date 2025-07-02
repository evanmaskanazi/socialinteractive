"""
Therapeutic Companion Web Backend
Integrates with Social Worker Assessment System
"""

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import json
import os
import csv
import io
from datetime import datetime, timedelta
from pathlib import Path

# Import the social worker components
from socialworkcountry import GlobalSocialWorkerChatbot, PatientProfile

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create data directories
os.makedirs('therapy_data', exist_ok=True)
os.makedirs('therapy_data/patients', exist_ok=True)
os.makedirs('therapy_data/checkins', exist_ok=True)
os.makedirs('therapy_data/reports', exist_ok=True)

# Initialize the social worker chatbot
chatbot = GlobalSocialWorkerChatbot()

@app.route('/')
def index():
    """Serve the main HTML file"""
    # Check if client.html exists
    if os.path.exists('client.html'):
        with open('client.html', 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return """
        <html>
        <body>
            <h1>Therapeutic Companion Server Running</h1>
            <p>Please ensure client.html is in the same directory as this script.</p>
            <p>API Endpoints available:</p>
            <ul>
                <li>/api/assess - Social Worker Assessment</li>
                <li>/api/therapy/save-patient - Save therapy patient</li>
                <li>/api/therapy/save-checkin - Save daily check-in</li>
                <li>/api/therapy/get-week-data - Get weekly data</li>
            </ul>
        </body>
        </html>
        """

# ============= SOCIAL WORKER ASSESSMENT ENDPOINTS =============

@app.route('/api/assess', methods=['POST'])
def assess_patient():
    """Run comprehensive social worker assessment"""
    try:
        data = request.json
        
        # Create PatientProfile from request data
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

@app.route('/api/countries', methods=['GET'])
def get_countries():
    """Get list of available countries"""
    try:
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

@app.route('/api/emergency-resources/<country_code>', methods=['GET'])
def get_emergency_resources(country_code):
    """Get emergency resources for a specific country"""
    try:
        country_data = chatbot.health_db.country_health_data.get(country_code, {})
        
        return jsonify({
            'success': True,
            'country': country_code.replace('_', ' ').title(),
            'crisis_resources': country_data.get('crisis_resources', []),
            'healthcare_system': country_data.get('healthcare_system', 'Unknown')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/save-assessment', methods=['POST'])
def save_assessment():
    """Save assessment results to file"""
    try:
        data = request.json
        patient_name = data.get('patient_name', 'Unknown')
        country = data.get('country', 'Unknown')
        assessment_data = data.get('assessment_data', {})
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"assessment_{patient_name.replace(' ', '_')}_{country}_{timestamp}.json"
        filepath = os.path.join('therapy_data', 'reports', filename)
        
        # Save data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(assessment_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'Assessment saved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============= THERAPY COMPANION ENDPOINTS =============

@app.route('/api/therapy/save-patient', methods=['POST'])
def save_therapy_patient():
    """Save therapy patient data"""
    try:
        data = request.json
        patient_id = data.get('patientId')
        patient_data = data.get('patientData')
        
        if not patient_id or not patient_data:
            return jsonify({
                'success': False,
                'error': 'Missing patient ID or data'
            }), 400
        
        # Save patient data
        filename = f'patient_{patient_id}.json'
        filepath = os.path.join('therapy_data', 'patients', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(patient_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': 'Patient data saved successfully',
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/therapy/save-checkin', methods=['POST'])
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
        
        date = checkin_data.get('date')
        
        # Create patient checkin directory if it doesn't exist
        patient_dir = os.path.join('therapy_data', 'checkins', patient_id)
        os.makedirs(patient_dir, exist_ok=True)
        
        # Save check-in data
        filename = f'checkin_{date}.json'
        filepath = os.path.join(patient_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(checkin_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': 'Check-in saved successfully',
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/therapy/get-week-data/<patient_id>/<week>', methods=['GET'])
def get_week_data(patient_id, week):
    """Get all check-in data for a specific week"""
    try:
        week_data = {}
        checkin_dir = os.path.join('therapy_data', 'checkins', patient_id)
        
        if os.path.exists(checkin_dir):
            # Parse week string (e.g., "2024-W05")
            year, week_num = week.split('-W')
            year = int(year)
            week_num = int(week_num)
            
            # Calculate week dates
            jan1 = datetime(year, 1, 1)
            days_to_monday = (7 - jan1.weekday()) % 7
            if days_to_monday == 0:
                days_to_monday = 7
            first_monday = jan1 + timedelta(days=days_to_monday - 7)
            week_start = first_monday + timedelta(weeks=week_num)
            
            # Get data for each day of the week
            for i in range(7):
                date = week_start + timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                
                checkin_file = os.path.join(checkin_dir, f'checkin_{date_str}.json')
                if os.path.exists(checkin_file):
                    with open(checkin_file, 'r', encoding='utf-8') as f:
                        week_data[date_str] = json.load(f)
        
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
    """Get list of all therapy patients"""
    try:
        patients = []
        patients_dir = os.path.join('therapy_data', 'patients')
        
        if os.path.exists(patients_dir):
            for filename in os.listdir(patients_dir):
                if filename.startswith('patient_') and filename.endswith('.json'):
                    filepath = os.path.join(patients_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        patient_data = json.load(f)
                        patients.append(patient_data)
        
        return jsonify({
            'success': True,
            'patients': patients
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Therapeutic Companion Backend',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == "__main__":
    print("=" * 80)
    print("🏥 THERAPEUTIC COMPANION & SOCIAL WORKER ASSESSMENT SYSTEM")
    print("=" * 80)
    print("Starting integrated backend server...")
    print("✅ Social Worker Assessment endpoints available at /api/")
    print("✅ Therapy Companion endpoints available at /api/therapy/")
    print("=" * 80)
    print("\n📁 Data will be saved in:")
    print("  - therapy_data/patients/ (patient profiles)")
    print("  - therapy_data/checkins/ (daily check-ins)")
    print("  - therapy_data/reports/ (assessment reports)")
    print("\n🌐 Server running at: http://localhost:5000")
    print("=" * 80)
    
    app.run(host='127.0.0.1', port=5000, debug=True)