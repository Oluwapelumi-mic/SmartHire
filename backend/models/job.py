# backend/models/job.py
from models.db import db
from datetime import datetime
import uuid

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    salary_range = db.Column(db.String(100))
    job_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    employer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    employer = db.relationship('User', backref='posted_jobs')
    # Applications relationship is handled by backref in Application model
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'description': self.description,
            'requirements': self.requirements,
            'location': self.location,
            'salary_range': self.salary_range,
            'job_type': self.job_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'employer_id': self.employer_id
        }