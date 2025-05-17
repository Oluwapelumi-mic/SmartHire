# backend/controllers/recommendation_controller.py
from flask import jsonify
from services.recommendation_service import recommendation_service

def get_recommendations(current_user, args):
    """Get job recommendations for the current user"""
    try:
        limit = int(args.get('limit', 10))
        recommendations = recommendation_service.get_recommendations_for_user(current_user['id'], limit)
        return jsonify({
            'success': True,
            'recommendations': recommendations
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
