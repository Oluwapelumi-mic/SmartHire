# backend/models/job.py
from models.db import db
from datetime import datetime
import uuid

job_skills = db.Table('job_skills',
    db.Column('job_id', db.String(36), db.ForeignKey('jobs.id'), primary_key=True),
    db.Column('skill_id', db.String(36), db.ForeignKey('skills.id'), primary_key=True)
)

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    salary_min = db.Column(db.Integer, nullable=True)
    salary_max = db.Column(db.Integer, nullable=True)
    job_type = db.Column(db.String(50), nullable=False)  # full-time, part-time, contract, etc.
    experience_level = db.Column(db.String(50), nullable=False)  # entry, mid, senior, etc.
    employer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    skills = db.relationship('Skill', secondary=job_skills, lazy='subquery', backref=db.backref('jobs', lazy=True))
    applications = db.relationship('Application', backref='job', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'job_type': self.job_type,
            'experience_level': self.experience_level,
            'skills': [skill.name for skill in self.skills],
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }