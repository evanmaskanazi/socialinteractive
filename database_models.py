"""
Simple database models for storing JSON data
This creates a hybrid solution that stores JSON in database tables
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Patient(db.Model):
    """Store patient data as JSON"""
    __tablename__ = 'patients'
    
    id = db.Column(db.String(50), primary_key=True)  # patient_id
    data = db.Column(db.Text, nullable=False)  # JSON data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_data(self):
        """Get patient data as dictionary"""
        return json.loads(self.data)
    
    def set_data(self, data_dict):
        """Set patient data from dictionary"""
        self.data = json.dumps(data_dict, ensure_ascii=False)


class CheckIn(db.Model):
    """Store check-in data as JSON"""
    __tablename__ = 'checkins'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    data = db.Column(db.Text, nullable=False)  # JSON data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Create unique constraint on patient_id + date
    __table_args__ = (
        db.UniqueConstraint('patient_id', 'date', name='_patient_date_uc'),
    )
    
    def get_data(self):
        """Get check-in data as dictionary"""
        return json.loads(self.data)
    
    def set_data(self, data_dict):
        """Set check-in data from dictionary"""
        self.data = json.dumps(data_dict, ensure_ascii=False)


class Report(db.Model):
    """Store generated reports metadata"""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), nullable=False)
    week = db.Column(db.String(10), nullable=False)  # YYYY-W##
    filename = db.Column(db.String(200), nullable=False)
    file_data = db.Column(db.LargeBinary, nullable=True)  # Store Excel file
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ActivityLog(db.Model):
    """Store activity logs"""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Text)  # JSON data
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_data(self):
        """Get log data as dictionary"""
        return json.loads(self.data) if self.data else {}
    
    def set_data(self, data_dict):
        """Set log data from dictionary"""
        self.data = json.dumps(data_dict, ensure_ascii=False)