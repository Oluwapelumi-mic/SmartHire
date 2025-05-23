from models.db import db
from datetime import datetime
import uuid

class Skill(db.Model):
    __tablename__ = 'skills'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(100), nullable=True)  # e.g., programming, soft skill, language
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
        }