from flask import jsonify
from models.db import db
from models.user import User
from models.profile import Profile
import jwt
import os
from datetime import datetime, timedelta
import re

def generate_token(user_id):
    """Generate JWT token for authentication"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1)  # Token expires in 1 day
    }
    token = jwt.encode(payload, os.environ.get('JWT_SECRET_KEY', 'dev'), algorithm='HS256')
    return token

def register(data):
    """Register a new user"""
    # Validate input
    required_fields = ['email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({
                'success': False,
                'message': f'Missing required field: {field}'
            }), 400
    
    # Check if email already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({
            'success': False,
            'message': 'Email already in use'
        }), 409
    
    # Validate email format
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_pattern, data['email']):
        return jsonify({
            'success': False,
            'message': 'Invalid email format'
        }), 400
    
    # Validate password strength
    if len(data['password']) < 8:
        return jsonify({
            'success': False,
            'message': 'Password must be at least 8 characters long'
        }), 400
    
    try:
        # Create new user
        new_user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data.get('role', 'job_seeker')
        )
        new_user.set_password(data['password'])
        
        # Create empty profile
        new_profile = Profile(user_id=new_user.id)
        
        # Save to database
        db.session.add(new_user)
        db.session.add(new_profile)
        db.session.commit()
        
        # Generate token
        token = generate_token(new_user.id)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'token': token,
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error registering user: {str(e)}'
        }), 500

def login(data):
    """Authenticate user and generate token"""
    # Validate input
    if 'email' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'message': 'Email and password are required'
        }), 400
    
    try:
        # Find user by email
        user = User.query.filter_by(email=data['email']).first()
        
        # Check if user exists and password is correct
        if not user or not user.check_password(data['password']):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
        
        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error during login: {str(e)}'
        }), 500

def get_current_user(current_user):
    """Get current authenticated user"""
    try:
        user = User.query.get(current_user['id'])
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving user: {str(e)}'
        }), 500
