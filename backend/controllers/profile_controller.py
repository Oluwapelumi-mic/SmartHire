from flask import jsonify
from models.db import db
from models.profile import Profile
from models.skill import Skill
from models.experience import Experience
from datetime import datetime

def get_profile(current_user):
    """Get user profile"""
    try:
        profile = Profile.query.filter_by(user_id=current_user['id']).first()
        
        if not profile:
            return jsonify({
                'success': False,
                'message': 'Profile not found'
            }), 404
        
        return jsonify({
            'success': True,
            'profile': profile.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving profile: {str(e)}'
        }), 500

def update_profile(current_user, data):
    """Update user profile"""
    try:
        profile = Profile.query.filter_by(user_id=current_user['id']).first()
        
        if not profile:
            # Create profile if it doesn't exist
            profile = Profile(user_id=current_user['id'])
            db.session.add(profile)
        
        # Update basic profile fields
        updatable_fields = [
            'headline', 'summary', 'experience_years', 'education',
            'job_title', 'location', 'desired_salary', 'desired_job_type',
            'remote_preference'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(profile, field, data[field])
        
        # Handle skills update
        if 'skills' in data and isinstance(data['skills'], list):
            # Clear existing skills
            profile.skills = []
            
            # Add updated skills
            for skill_name in data['skills']:
                # Find or create skill
                skill = Skill.query.filter_by(name=skill_name).first()
                if not skill:
                    skill = Skill(name=skill_name)
                    db.session.add(skill)
                
                profile.skills.append(skill)
        
        # Handle experiences update
        if 'experiences' in data and isinstance(data['experiences'], list):
            # Get existing experiences
            existing_experiences = {exp.id: exp for exp in profile.experiences}
            updated_exp_ids = set()
            
            for exp_data in data['experiences']:
                if 'id' in exp_data and exp_data['id'] in existing_experiences:
                    # Update existing experience
                    exp = existing_experiences[exp_data['id']]
                    updated_exp_ids.add(exp_data['id'])
                else:
                    # Create new experience
                    exp = Experience(profile_id=profile.id)
                    db.session.add(exp)
                
                # Update fields
                exp.title = exp_data.get('title', exp.title)
                exp.company = exp_data.get('company', exp.company)
                exp.location = exp_data.get('location', exp.location)
                
                # Handle dates
                if 'start_date' in exp_data:
                    exp.start_date = datetime.fromisoformat(exp_data['start_date'].rstrip('Z'))
                
                if 'end_date' in exp_data:
                    if exp_data['end_date']:
                        exp.end_date = datetime.fromisoformat(exp_data['end_date'].rstrip('Z'))
                    else:
                        exp.end_date = None
                
                exp.is_current = exp_data.get('is_current', exp.is_current)
                exp.description = exp_data.get('description', exp.description)
            
            # Remove experiences not in the update
            for exp_id, exp in existing_experiences.items():
                if exp_id not in updated_exp_ids:
                    db.session.delete(exp)
        
        # Save changes
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': profile.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating profile: {str(e)}'
        }), 500
