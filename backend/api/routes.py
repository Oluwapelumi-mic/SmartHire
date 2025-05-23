from flask import Blueprint, request, jsonify
from controllers.auth_controller import register, login, get_current_user
from controllers.job_controller import get_jobs, get_job, create_job
from controllers.recommendation_controller import get_recommendations
from controllers.profile_controller import get_profile, update_profile
from utils.auth import token_required

api_bp = Blueprint('api', __name__)

# Auth routes
@api_bp.route('/auth/register', methods=['POST'])
def register_route():
    return register(request.json)

@api_bp.route('/auth/login', methods=['POST'])
def login_route():
    return login(request.json)


@api_bp.route('/auth/me', methods=['GET'])
@token_required
def me_route(current_user):
    return get_current_user(current_user)

# Job routes
@api_bp.route('/jobs', methods=['GET'])
def jobs_route():
    return get_jobs(request.args)

@api_bp.route('/jobs/<job_id>', methods=['GET'])
def job_route(job_id):
    return get_job(job_id)

@api_bp.route('/jobs', methods=['POST'])
@token_required
def create_job_route(current_user):
    return create_job(request.json, current_user)

# Recommendation routes
@api_bp.route('/recommendations', methods=['GET'])
@token_required
def recommendations_route(current_user):
    return get_recommendations(current_user, request.args)

# Profile routes
@api_bp.route('/profile', methods=['GET'])
@token_required
def profile_route(current_user):
    return get_profile(current_user)

@api_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile_route(current_user):
    return update_profile(current_user, request.json)
