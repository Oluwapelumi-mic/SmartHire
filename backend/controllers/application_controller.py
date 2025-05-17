from flask import jsonify
from models.db import db
from models.application import Application
from models.job import Job
from datetime import datetime

def apply_for_job(job_id, data, current_user):
    """Submit a job application"""
    try:
        # Check if job exists and is active
        job = Job.query.get(job_id)
        if not job:
            return jsonify({
                'success': False,
                'message': 'Job not found'
            }), 404
        
        if not job.is_active:
            return jsonify({
                'success': False,
                'message': 'This job is no longer accepting applications'
            }), 400
        
        # Check if user has already applied
        existing_application = Application.query.filter_by(
            job_id=job_id, 
            user_id=current_user['id']
        ).first()
        
        if existing_application:
            return jsonify({
                'success': False,
                'message': 'You have already applied for this job'
            }), 409
        
        # Create new application
        new_application = Application(
            job_id=job_id,
            user_id=current_user['id'],
            cover_letter=data.get('cover_letter'),
            resume_url=data.get('resume_url')
        )
        
        # Save to database
        db.session.add(new_application)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Application submitted successfully',
            'application': new_application.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error submitting application: {str(e)}'
        }), 500

def get_user_applications(current_user):
    """Get all applications submitted by the current user"""
    try:
        applications = Application.query.filter_by(user_id=current_user['id']).all()
        
        # Get job details for each application
        result = []
        for app in applications:
            job = Job.query.get(app.job_id)
            if job:
                app_data = app.to_dict()
                app_data['job'] = job.to_dict()
                result.append(app_data)
        
        return jsonify({
            'success': True,
            'applications': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving applications: {str(e)}'
        }), 500

def get_job_applications(job_id, current_user):
    """Get all applications for a specific job (employer only)"""
    try:
        # Get the job
        job = Job.query.get(job_id)
        
        # Check if job exists
        if not job:
            return jsonify({
                'success': False,
                'message': 'Job not found'
            }), 404
        
        # Check if user is the employer who posted the job
        if job.employer_id != current_user['id']:
            return jsonify({
                'success': False,
                'message': 'You are not authorized to view these applications'
            }), 403
        
        # Get applications
        applications = Application.query.filter_by(job_id=job_id).all()
        
        # Format response
        result = [app.to_dict() for app in applications]
        
        return jsonify({
            'success': True,
            'applications': result,
            'count': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving applications: {str(e)}'
        }), 500

def update_application_status(application_id, data, current_user):
    """Update application status (employer only)"""
    try:
        # Get the application
        application = Application.query.get(application_id)
        
        # Check if application exists
        if not application:
            return jsonify({
                'success': False,
                'message': 'Application not found'
            }), 404
        
        # Get the job
        job = Job.query.get(application.job_id)
        
        # Check if user is the employer
        if job.employer_id != current_user['id']:
            return jsonify({
                'success': False,
                'message': 'You are not authorized to update this application'
            }), 403
        
        # Validate status
        valid_statuses = ['applied', 'reviewed', 'interview', 'offer', 'rejected']
        if 'status' not in data or data['status'] not in valid_statuses:
            return jsonify({
                'success': False,
                'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400
        
        # Update status
        application.status = data['status']
        application.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Application status updated successfully',
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating application: {str(e)}'
        }), 500