from flask import request, jsonify
from functools import wraps
import jwt
import os
from models.user import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is missing'
            }), 401
        
        try:
            # Verify token
            data = jwt.decode(token, os.environ.get('JWT_SECRET_KEY'), algorithms=['HS256'])
            user = User.query.filter_by(id=data['user_id']).first()
            
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Invalid token'
                }), 401
            
            # Return user info for controller use
            current_user = user.to_dict()
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token has expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated