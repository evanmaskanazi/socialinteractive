"""
Public Therapeutic Companion Web Backend - Hybrid Database Version
Uses database for persistence but maintains JSON structure
Works on Render's free tier with PostgreSQL
"""

from flask import Flask, request, jsonify, send_file, Response
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
from sqlalchemy import and_
import tempfile

# Import database models
from database_models import db, Patient, CheckIn, Report, ActivityLog

# Optional: Load environment variables from .env file for local development
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Import the social worker components
from socialworkcountry import GlobalSocialWorkerChatbot, PatientProfile

# Create Flask app
app = Flask(__name__)

# Database configuration
if os.environ.get('DATABASE_URL'):
    # Render PostgreSQL
    database_url = os.environ.get('DATABASE_URL')
    # Fix for SQLAlchemy (Render uses postgres:// but SQLAlchemy needs postgresql://)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Local SQLite for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///therapy_data.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully")

# Configure CORS for production
if os.environ.get('PRODUCTION'):
    CORS(app, origins=[os.environ.get('ALLOWED_ORIGINS', '*')])
else:
    CORS(app)  # Allow all origins in development

# Initialize rate limiter for public use
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"]  # Generous limits for public use
)

# Initialize the social worker chatbot
chatbot = GlobalSocialWorkerChatbot()


# ============= HELPER FUNCTIONS =============

def get_system_email_config():
    """Get system email configuration from environment variables"""
    # PRODUCTION: Use environment variables
    if os.environ.get('SYSTEM_EMAIL') and os.environ.get('SYSTEM_EMAIL_PASSWORD'):
        return {
            'sender_email': os.environ.get('SYSTEM_EMAIL'),
            'sender_password': os.environ.get('SYSTEM_EMAIL_PASSWORD'),
            'smtp_server': os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.environ.get('SMTP_PORT', '587'))
        }

    # No configuration found
    return None


def log_email_activity(patient_id, recipient, week, status):
    """Log email sending activity to database"""
    log_data = {
        'patient_id': patient_id,
        'recipient': recipient,
        'week': week,
        'status': status,
        'system_email': os.environ.get('SYSTEM_EMAIL', 'not_configured')
    }

    log_entry = ActivityLog(
        activity_type='email_sent',
        ip_address=request.remote_addr if request else 'system'
    )
    log_entry.set_data(log_data)

    db.session.add(log_entry)
    db.session.commit()


def log_activity(activity_type, data):
    """Log general system activity to database"""
    log_entry = ActivityLog(
        activity_type=activity_type,
        ip_address=request.remote_addr if request else 'system'
    )
    log_entry.set_data(data)

    db.session.add(log_entry)
    db.session.commit()


# ============= PUBLIC ENDPOINTS =============

@app.route('/')
def index():
    """Serve the main HTML file"""
    if os.path.exists('therapy_tracker.html'):
        with open('therapy_tracker.html', 'r', encoding='utf-8') as f:
            return f.read()
    elif os.path.exists('client.html'):
        with open('client.html', 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return f"""
        <html>
        <body>
            <h1>Therapeutic Companion Server Running</h1>
            <p>Database-backed version for Render deployment</p>
            <h2>Features:</h2>
            <ul>
                <li>✅ Public access - no login required</li>
                <li>✅ Patient enrollment by therapists</li>
                <li>✅ Daily check-ins tracking</li>
                <li>✅ Weekly Excel reports</li>
                <li>✅ Automatic email delivery</li>
                <li>✅ System email sends all reports</li>
                <li>✅ Database persistence (PostgreSQL/SQLite)</li>
            </ul>
            <p><strong>Database:</strong> {'PostgreSQL' if os.environ.get('DATABASE_URL') else 'SQLite'}</p>
        </body>
        </html>
        """


# ============= THERAPY TRACKING ENDPOINTS (PUBLIC) =============

@app.route('/api/therapy/save-patient', methods=['POST'])
@limiter.limit("50 per hour")  # Prevent spam enrollment
def save_therapy_patient():
    """Save therapy patient enrollment data"""
    try:
        data = request.json
        patient_id = data.get('patientId')
        patient_data = data.get('patientData')

        # Required access code for security
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

        # Add enrollment metadata
        patient_data['enrollmentTimestamp'] = datetime.now().isoformat()
        patient_data['enrolledFrom'] = request.remote_addr
        patient_data['weeklyReports'] = []

        # Check if patient exists
        patient = Patient.query.get(patient_id)
        if patient:
            # Update existing patient
            patient.set_data(patient_data)
        else:
            # Create new patient
            patient = Patient(id=patient_id)
            patient.set_data(patient_data)
            db.session.add(patient)

        db.session.commit()

        # Log activity
        log_activity('patient_enrolled', {
            'patient_id': patient_id,
            'therapist_email': patient_data.get('therapistEmail')
        })

        return jsonify({
            'success': True,
            'message': 'Patient enrolled successfully',
            'patient_id': patient_id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/therapy/save-checkin', methods=['POST'])
@limiter.limit("200 per hour")  # Allow multiple check-ins
def save_therapy_checkin():
    """Save comprehensive daily check-in data"""
    try:
        data = request.json
        patient_id = data.get('patientId')
        checkin_data = data.get('checkinData')

        if not patient_id or not checkin_data:
            return jsonify({
                'success': False,
                'error': 'Missing patient ID or check-in data'
            }), 400

        # Verify patient exists
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'success': False, 'error': 'Patient not found'}), 404

        # Validate check-in data
        required_fields = ['date', 'time', 'emotional', 'medication', 'activity']
        for field in required_fields:
            if field not in checkin_data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        # Add metadata
        checkin_data['serverTimestamp'] = datetime.now().isoformat()
        checkin_data['submittedFrom'] = request.remote_addr

        # Check if check-in exists for this date
        date = checkin_data.get('date')
        checkin = CheckIn.query.filter_by(patient_id=patient_id, date=date).first()

        if checkin:
            # Update existing check-in
            checkin.set_data(checkin_data)
        else:
            # Create new check-in
            checkin = CheckIn(patient_id=patient_id, date=date)
            checkin.set_data(checkin_data)
            db.session.add(checkin)

        db.session.commit()

        # Log activity
        log_activity('checkin_recorded', {
            'patient_id': patient_id,
            'date': date
        })

        return jsonify({
            'success': True,
            'message': 'Daily check-in saved successfully',
            'date': date
        })

    except Exception as e:
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

            checkin = CheckIn.query.filter_by(patient_id=patient_id, date=date_str).first()
            if checkin:
                week_data[date_str] = checkin.get_data()

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
    """Get list of all enrolled therapy patients"""
    try:
        patients = []

        # Query all patients
        all_patients = Patient.query.all()

        for patient in all_patients:
            patient_data = patient.get_data()
            patient_data['patientId'] = patient.id
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


@app.route('/api/therapy/generate-excel-report/<patient_id>/<week>', methods=['GET'])
@limiter.limit("30 per hour")  # Limit report generation
def generate_excel_report(patient_id, week):
    """Generate comprehensive Excel report for a patient's week"""
    try:
        # Get patient data
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'success': False, 'error': 'Patient not found'}), 404

        patient_data = patient.get_data()
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

        # Styles
        header_font = Font(bold=True, size=14)
        subheader_font = Font(bold=True, size=12)

        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        subheader_fill = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")

        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Add patient information
        summary_sheet['A1'] = "WEEKLY THERAPY TRACKING REPORT"
        summary_sheet['A1'].font = Font(bold=True, size=16)
        summary_sheet.merge_cells('A1:F1')

        summary_sheet['A3'] = "Patient Information"
        summary_sheet['A3'].font = subheader_font
        summary_sheet.merge_cells('A3:B3')

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

        # Add summary statistics
        summary_sheet['D3'] = "Weekly Statistics"
        summary_sheet['D3'].font = subheader_font
        summary_sheet.merge_cells('D3:F3')

        # Calculate statistics
        total_days = 7
        completed_days = len(week_data)

        if completed_days > 0:
            total_emotional = sum(data['emotional']['value'] for data in week_data.values())
            total_medication = sum(data['medication']['value'] for data in week_data.values())
            total_activity = sum(data['activity']['value'] for data in week_data.values())

            avg_emotional = total_emotional / completed_days
            avg_medication = total_medication / completed_days
            avg_activity = total_activity / completed_days
        else:
            avg_emotional = avg_medication = avg_activity = 0

        stats_rows = [
            ("Completion Rate:", f"{completed_days}/{total_days} ({completed_days / 7 * 100:.1f}%)"),
            ("Avg Emotional State:", f"{avg_emotional:.2f}/5" if completed_days > 0 else "N/A"),
            ("Avg Medication Adherence:", f"{avg_medication:.2f}/5" if completed_days > 0 else "N/A"),
            ("Avg Physical Activity:", f"{avg_activity:.2f}/5" if completed_days > 0 else "N/A")
        ]

        row = 4
        for label, value in stats_rows:
            summary_sheet[f'D{row}'] = label
            summary_sheet[f'E{row}'] = value
            summary_sheet[f'D{row}'].font = Font(bold=True)
            row += 1

        # Create Daily Data Sheet
        daily_sheet = wb.create_sheet("Daily Check-ins")

        # Headers for daily data
        headers = ["Date", "Day", "Time", "Emotional State", "Emotional Notes",
                   "Medication Adherence", "Medication Notes", "Physical Activity",
                   "Activity Notes", "Check-in Status"]

        for col, header in enumerate(headers, 1):
            cell = daily_sheet.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
            cell.border = border

        # Parse week to get dates
        year, week_num = week.split('-W')
        year = int(year)
        week_num = int(week_num)

        # Calculate week start date
        jan_4 = datetime(year, 1, 4)
        week_1_monday = jan_4 - timedelta(days=jan_4.weekday())
        week_start = week_1_monday + timedelta(weeks=week_num - 1)

        # Add daily data
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for day_num in range(7):
            current_date = week_start + timedelta(days=day_num)
            date_str = current_date.strftime('%Y-%m-%d')

            row = day_num + 2
            daily_sheet.cell(row=row, column=1, value=date_str).border = border
            daily_sheet.cell(row=row, column=2, value=days_of_week[day_num]).border = border

            if date_str in week_data:
                data = week_data[date_str]
                daily_sheet.cell(row=row, column=3, value=data.get('time', '')).border = border
                daily_sheet.cell(row=row, column=4, value=data['emotional']['value']).border = border
                daily_sheet.cell(row=row, column=5, value=data['emotional'].get('notes', '')).border = border

                # Medication value with text labels
                med_value = data['medication']['value']
                medication_text = {
                    0: "Not Applicable",
                    1: "No Doses",
                    3: "Partial Doses",
                    5: "Yes, All Doses"
                }.get(med_value, str(med_value))
                daily_sheet.cell(row=row, column=6, value=medication_text).border = border
                daily_sheet.cell(row=row, column=7, value=data['medication'].get('notes', '')).border = border
                daily_sheet.cell(row=row, column=8, value=data['activity']['value']).border = border
                daily_sheet.cell(row=row, column=9, value=data['activity'].get('notes', '')).border = border
                daily_sheet.cell(row=row, column=10, value="Completed").border = border

                # Color code emotional state
                emotional_cell = daily_sheet.cell(row=row, column=4)
                emotional_value = emotional_cell.value
                if emotional_value >= 4:
                    emotional_cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                elif emotional_value == 3:
                    emotional_cell.fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
                else:
                    emotional_cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

                # Color code medication adherence
                medication_cell = daily_sheet.cell(row=row, column=6)
                if med_value == 0:  # Not Applicable - no color
                    pass
                elif med_value == 1:  # No Doses - red
                    medication_cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
                elif med_value == 3:  # Partial Doses - yellow
                    medication_cell.fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
                elif med_value == 5:  # Yes, All Doses - green
                    medication_cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")

                # Color code physical activity
                activity_cell = daily_sheet.cell(row=row, column=8)
                activity_value = activity_cell.value
                if activity_value >= 4:
                    activity_cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                elif activity_value == 3:
                    activity_cell.fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
                else:
                    activity_cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
            else:
                daily_sheet.cell(row=row, column=3, value="-").border = border
                for col in range(4, 10):
                    daily_sheet.cell(row=row, column=col, value="-").border = border
                cell = daily_sheet.cell(row=row, column=10, value="No Response")
                cell.border = border
                cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

        # Create Detailed Notes Sheet
        notes_sheet = wb.create_sheet("Detailed Notes")

        # Headers for notes
        notes_headers = ["Date", "Category", "Rating", "Notes"]
        for col, header in enumerate(notes_headers, 1):
            cell = notes_sheet.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
            cell.border = border

        # Add all notes
        row = 2
        for date_str in sorted(week_data.keys()):
            data = week_data[date_str]

            # Emotional notes
            if data['emotional'].get('notes'):
                notes_sheet.cell(row=row, column=1, value=date_str).border = border
                notes_sheet.cell(row=row, column=2, value="Emotional").border = border
                notes_sheet.cell(row=row, column=3, value=data['emotional']['value']).border = border
                notes_sheet.cell(row=row, column=4, value=data['emotional']['notes']).border = border
                row += 1

            # Medication notes
            if data['medication'].get('notes'):
                notes_sheet.cell(row=row, column=1, value=date_str).border = border
                notes_sheet.cell(row=row, column=2, value="Medication").border = border
                med_value = data['medication']['value']
                medication_text = {
                    0: "Not Applicable",
                    1: "No Doses",
                    3: "Partial Doses",
                    5: "Yes, All Doses"
                }.get(med_value, str(med_value))
                notes_sheet.cell(row=row, column=3, value=medication_text).border = border
                notes_sheet.cell(row=row, column=4, value=data['medication']['notes']).border = border
                row += 1

            # Activity notes
            if data['activity'].get('notes'):
                notes_sheet.cell(row=row, column=1, value=date_str).border = border
                notes_sheet.cell(row=row, column=2, value="Physical Activity").border = border
                notes_sheet.cell(row=row, column=3, value=data['activity']['value']).border = border
                notes_sheet.cell(row=row, column=4, value=data['activity']['notes']).border = border
                row += 1

        # Auto-adjust column widths
        for sheet in [summary_sheet, daily_sheet, notes_sheet]:
            for column in sheet.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)

                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass

                adjusted_width = min(max_length + 2, 50)
                sheet.column_dimensions[column_letter].width = adjusted_width

        # Save Excel file to temporary file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"therapy_report_{patient_id}_{week}_{timestamp}.xlsx"

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        wb.save(temp_file.name)
        temp_file.close()

        # Store report metadata in database
        report = Report(
            patient_id=patient_id,
            week=week,
            filename=filename
        )

        # Read file data
        with open(temp_file.name, 'rb') as f:
            report.file_data = f.read()

        db.session.add(report)
        db.session.commit()

        # Log activity
        log_activity('report_generated', {
            'patient_id': patient_id,
            'week': week
        })

        # Send file
        response = send_file(
            temp_file.name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

        # Clean up temp file after sending
        os.unlink(temp_file.name)

        return response

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/therapy/email-report', methods=['POST'])
@limiter.limit("20 per hour")  # Limit email sending
def email_therapy_report():
    """Send therapy report using system email account"""
    try:
        data = request.json
        patient_id = data.get('patientId')
        week = data.get('week')

        # Get patient data
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'success': False, 'error': 'Patient not found'}), 404

        patient_data = patient.get_data()
        patient_data['patientId'] = patient_id

        # Get system email configuration
        email_config = get_system_email_config()

        if not email_config:
            return jsonify({
                'success': True,
                'message': 'Email report prepared',
                'recipient': patient_data['therapistEmail'],
                'subject': f'Weekly Therapy Report - {patient_data["name"]} - Week {week}',
                'note': 'Email not sent - system email not configured. Contact administrator.',
                'error': 'System administrator needs to set SYSTEM_EMAIL environment variables.'
            })

        # Find or generate Excel report
        report = Report.query.filter_by(patient_id=patient_id, week=week).order_by(Report.created_at.desc()).first()

        if not report or not report.file_data:
            # Generate the Excel report
            excel_response = generate_excel_report(patient_id, week)
            # Query again
            report = Report.query.filter_by(patient_id=patient_id, week=week).order_by(Report.created_at.desc()).first()

        if not report or not report.file_data:
            return jsonify({
                'success': False,
                'error': 'Could not generate Excel report'
            }), 500

        excel_filename = report.filename

        # Calculate statistics for email content
        week_response = get_week_data(patient_id, week)
        week_data_json = week_response.get_json()
        week_data = week_data_json.get('weekData', {})

        completed_days = len(week_data)
        if completed_days > 0:
            avg_emotional = sum(d['emotional']['value'] for d in week_data.values()) / completed_days
            med_values = [d['medication']['value'] for d in week_data.values() if d['medication']['value'] > 0]
            avg_medication = sum(med_values) / len(med_values) if med_values else 0
            avg_activity = sum(d['activity']['value'] for d in week_data.values()) / completed_days
        else:
            avg_emotional = avg_medication = avg_activity = 0

        # Create professional email content
        system_name = os.environ.get('SYSTEM_NAME', 'Therapeutic Companion System')

        email_content = f"""
Dear {patient_data['therapistName']},

This is the weekly therapy tracking report for {patient_data['name']} (Patient ID: {patient_id}).

REPORT SUMMARY
--------------
Week: {week}
Completion Rate: {completed_days}/7 days ({completed_days / 7 * 100:.1f}%)

Weekly Averages:
• Emotional State: {avg_emotional:.2f}/5
• Medication Adherence: {avg_medication:.2f}/5 {"(excluding N/A)" if avg_medication > 0 else ""}
• Physical Activity: {avg_activity:.2f}/5

The detailed Excel report is attached to this email. It includes:
- Daily check-in data with timestamps
- Color-coded ratings for easy visualization
- Complete notes and observations
- Weekly summary statistics

If you have any questions about this report, please contact your system administrator.

Best regards,
{system_name}

---
This is an automated report generated by the Therapeutic Companion System.
Please do not reply to this email address as it is not monitored.
Report generated on: {datetime.now().strftime('%Y-%m-%d at %H:%M')}
        """

        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = f"{system_name} <{email_config['sender_email']}>"
            msg['To'] = patient_data['therapistEmail']
            msg['Subject'] = f'Weekly Therapy Report - {patient_data["name"]} - Week {week}'

            # Add reply-to header if configured
            reply_to = os.environ.get('REPLY_TO_EMAIL')
            if reply_to:
                msg['Reply-To'] = reply_to

            # Attach the email body
            msg.attach(MIMEText(email_content, 'plain'))

            # Attach the Excel file from database
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(report.file_data)
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{excel_filename}"'
            )
            msg.attach(part)

            # Send the email
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['sender_email'], email_config['sender_password'])

            # Send to therapist
            server.send_message(msg)

            # Optional: Send a copy to system admin for records
            admin_email = os.environ.get('ADMIN_EMAIL')
            if admin_email:
                msg['Bcc'] = admin_email
                server.send_message(msg)

            server.quit()

            # Log the email sent
            log_email_activity(patient_id, patient_data['therapistEmail'], week, 'sent')

            return jsonify({
                'success': True,
                'message': 'Email sent successfully',
                'recipient': patient_data['therapistEmail'],
                'attachment': excel_filename,
                'note': f'Report sent from {email_config["sender_email"]}'
            })

        except Exception as e:
            # Log the error
            log_email_activity(patient_id, patient_data['therapistEmail'], week, f'failed: {str(e)}')

            return jsonify({
                'success': False,
                'error': f'Failed to send email: {str(e)}',
                'note': 'Please check system email configuration.'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============= SOCIAL WORKER ASSESSMENT ENDPOINTS (PUBLIC) =============

@app.route('/api/assess', methods=['POST'])
@limiter.limit("50 per hour")
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


# ============= HEALTH CHECK ENDPOINTS =============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    email_configured = bool(get_system_email_config())

    return jsonify({
        'status': 'healthy',
        'service': 'Public Therapeutic Companion Backend - Hybrid Database Version',
        'version': '3.0-hybrid-db',
        'features': [
            'Public access - no login required',
            'Patient enrollment and management',
            'Daily check-ins (emotional, medication, physical)',
            '7-day weekly tracking',
            'Excel report generation',
            'System email for all reports',
            'Rate limiting for security',
            'Activity logging',
            'Database persistence (PostgreSQL/SQLite)'
        ],
        'configuration': {
            'email_configured': email_configured,
            'system_email': os.environ.get('SYSTEM_EMAIL', 'not_set'),
            'access_code_required': bool(os.environ.get('ACCESS_CODE')),
            'production_mode': bool(os.environ.get('PRODUCTION')),
            'render_deployment': bool(os.environ.get('RENDER')),
            'database_type': 'PostgreSQL' if os.environ.get('DATABASE_URL') else 'SQLite'
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/stats', methods=['GET'])
def get_system_stats():
    """Get system statistics"""
    try:
        stats = {
            'patients': Patient.query.count(),
            'checkins': CheckIn.query.count(),
            'reports_generated': Report.query.count(),
            'emails_sent_today': 0,
            'database_type': 'PostgreSQL' if os.environ.get('DATABASE_URL') else 'SQLite'
        }

        # Count today's emails
        today = datetime.now().date()
        emails_today = ActivityLog.query.filter(
            ActivityLog.activity_type == 'email_sent',
            db.func.date(ActivityLog.created_at) == today
        ).count()
        stats['emails_sent_today'] = emails_today

        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============= ERROR HANDLERS =============

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
    print("🏥 PUBLIC THERAPEUTIC COMPANION SYSTEM - HYBRID DATABASE VERSION")
    print("=" * 80)
    print("✅ Public access enabled - no login required")
    print("✅ Database persistence for all data")
    print("✅ Works on Render's free tier")
    print("✅ Patient enrollment by therapists")
    print("✅ Daily check-in tracking")
    print("✅ Weekly Excel report generation")
    print("✅ Automatic email delivery")
    print("✅ Rate limiting for security")
    print("=" * 80)

    if os.environ.get('DATABASE_URL'):
        print("📊 Database: PostgreSQL (Render)")
    else:
        print("📊 Database: SQLite (Local development)")

    print("\n🔧 Configuration:")
    email_config = get_system_email_config()
    if email_config:
        print(f"  - System email: {email_config['sender_email']} ✅")
    else:
        print("  - System email: NOT CONFIGURED ❌")
        print("    Set SYSTEM_EMAIL and SYSTEM_EMAIL_PASSWORD environment variables")

    if os.environ.get('ACCESS_CODE'):
        print("  - Access code: ENABLED ✅")
    else:
        print("  - Access code: DISABLED (using default 'therapy2024')")

    print("\n🌐 Server running at: http://localhost:5000")
    print("=" * 80)

    # Run in production mode if environment variable is set
    if os.environ.get('PRODUCTION'):
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    else:
        app.run(host='127.0.0.1', port=5000, debug=True)