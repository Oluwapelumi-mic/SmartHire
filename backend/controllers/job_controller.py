from flask import jsonify
from models.db import db
from models.job import Job
from models.skill import Skill
from datetime import datetime
import re

def get_jobs(args):
    """Get all jobs with optional filtering"""
    try:
        # Start with base query
        query = Job.query
        
        # Apply filters
        if 'title' in args:
            query = query.filter(Job.title.ilike(f"%{args['title']}%"))
        
        if 'location' in args:
            query = query.filter(Job.location.ilike(f"%{args['location']}%"))
        
        if 'job_type' in args:
            query = query.filter(Job.job_type == args['job_type'])
        
        if 'experience_level' in args:
            query = query.filter(Job.experience_level == args['experience_level'])
        
        if 'salary_min' in args:
            try:
                min_salary = int(args['salary_min'])
                query = query.filter(Job.salary_min >= min_salary)
            except ValueError:
                pass
        
        if 'salary_max' in args:
            try:
                max_salary = int(args['salary_max'])
                query = query.filter(Job.salary_max <= max_salary)
            except ValueError:
                pass
        
        # Only show active jobs by default
        if 'show_inactive' not in args or args['show_inactive'].lower() != 'true':
            query = query.filter(Job.is_active == True)
        
        # Handle pagination
        page = int(args.get('page', 1))
        limit = min(int(args.get('limit', 10)), 50)  # Limit to 50 items max
        
        # Execute query with pagination
        paginated_jobs = query.order_by(Job.created_at.desc()).paginate(page=page, per_page=limit)
        
        # Format response
        jobs = [job.to_dict() for job in paginated_jobs.items]
        
        return jsonify({
            'success': True,
            'jobs': jobs,
            'total': paginated_jobs.total,
            'pages': paginated_jobs.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving jobs: {str(e)}'
        }), 500

def get_job(job_id):
    """Get a specific job by ID"""
    try:
        job = Job.query.get(job_id)
        
        if not job:
            return jsonify({
                'success': False,
                'message': 'Job not found'
            }), 404
        
        return jsonify({
            'success': True,
            'job': job.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving job: {str(e)}'
        }), 500

def create_job(data, current_user):
    """Create a new job listing"""
    # Check if user is an employer
    if current_user['role'] != 'employer':
        return jsonify({
            'success': False,
            'message': 'Only employers can create job listings'
        }), 403
    
    # Validate required fields
    required_fields = ['title', 'company', 'location', 'description', 'job_type', 'experience_level']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({
                'success': False,
                'message': f'Missing required field: {field}'
            }), 400
    
    try:
        # Create new job
        new_job = Job(
            title=data['title'],
            company=data['company'],
            location=data['location'],
            description=data['description'],
            job_type=data['job_type'],
            experience_level=data['experience_level'],
            employer_id=current_user['id'],
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max'),
            is_active=data.get('is_active', True)
        )
        
        # Handle skills
        if 'skills' in data and isinstance(data['skills'], list):
            for skill_name in data['skills']:
                # Find or create skill
                skill = Skill.query.filter_by(name=skill_name).first()
                if not skill:
                    skill = Skill(name=skill_name)
                    db.session.add(skill)
                
                new_job.skills.append(skill)
        
        # Save to database
        db.session.add(new_job)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Job created successfully',
            'job': new_job.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating job: {str(e)}'
        }), 500
