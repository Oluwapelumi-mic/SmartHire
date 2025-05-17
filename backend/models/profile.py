from models.db import db
from datetime import datetime
import uuid

profile_skills = db.Table('profile_skills',
    db.Column('profile_id', db.String(36), db.ForeignKey('profiles.id'), primary_key=True),
    db.Column('skill_id', db.String(36), db.ForeignKey('skills.id'), primary_key=True)
)

class Profile(db.Model):
    __tablename__ = 'profiles'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    headline = db.Column(db.String(255), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    experience_years = db.Column(db.Integer, nullable=True)
    education = db.Column(db.Text, nullable=True)
    job_title = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    desired_salary = db.Column(db.Integer, nullable=True)
    desired_job_type = db.Column(db.String(50), nullable=True)  # full-time, part-time, contract, etc.
    remote_preference = db.Column(db.String(50), nullable=True)  # remote, hybrid, on-site
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    skills = db.relationship('Skill', secondary=profile_skills, lazy='subquery', backref=db.backref('profiles', lazy=True))
    experiences = db.relationship('Experience', backref='profile', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'headline': self.headline,
            'summary': self.summary,
            'experience_years': self.experience_years,
            'education': self.education,
            'job_title': self.job_title,
            'location': self.location,
            'desired_salary': self.desired_salary,
            'desired_job_type': self.desired_job_type,
            'remote_preference': self.remote_preference,
            'skills': [skill.name for skill in self.skills],
            'experiences': [exp.to_dict() for exp in self.experiences],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }