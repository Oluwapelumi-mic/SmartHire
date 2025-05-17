import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os
from flask import current_app
from models.db import db
from models.job import Job
from models.user import User
from models.profile import Profile

class RecommendationService:
    def __init__(self):
        self.tfidf_vectorizer = None
        self.load_model()
        
    def load_model(self):
        """Load the trained TF-IDF vectorizer"""
        model_path = os.path.join(current_app.config['ML_MODEL_PATH'], 'tfidf_vectorizer.pkl')
        try:
            self.tfidf_vectorizer = joblib.load(model_path)
        except (FileNotFoundError, IOError):
            # If model doesn't exist, create a new one
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2)
            )
    
    def get_recommendations_for_user(self, user_id, limit=10):
        """Get job recommendations for a user based on their profile and skills"""
        # Get user profile
        user_profile = Profile.query.filter_by(user_id=user_id).first()
        if not user_profile:
            return []
        
        # Combine profile information into a single document
        user_document = f"{user_profile.headline} {user_profile.summary} {' '.join([skill.name for skill in user_profile.skills])}"
        
        # Get all active jobs
        jobs = Job.query.filter_by(is_active=True).all()
        job_ids = [job.id for job in jobs]
        job_documents = [f"{job.title} {job.description} {' '.join([skill.name for skill in job.skills])}" for job in jobs]
        
        if not job_documents:
            return []
        
        # Transform job documents using TF-IDF
        if not self.tfidf_vectorizer.vocabulary_:
            self.tfidf_vectorizer.fit(job_documents + [user_document])
        
        job_vectors = self.tfidf_vectorizer.transform(job_documents)
        user_vector = self.tfidf_vectorizer.transform([user_document])
        
        # Calculate cosine similarity between user and jobs
        similarities = cosine_similarity(user_vector, job_vectors)[0]
        
        # Sort jobs by similarity and return top matches
        job_similarity = list(zip(job_ids, similarities))
        job_similarity.sort(key=lambda x: x[1], reverse=True)
        
        recommended_job_ids = [job_id for job_id, _ in job_similarity[:limit]]
        
        # Fetch recommended jobs
        recommended_jobs = []
        for job_id in recommended_job_ids:
            job = Job.query.get(job_id)
            if job:
                recommended_jobs.append(job.to_dict())
        
        return recommended_jobs

# Instantiate the recommendation service
recommendation_service = RecommendationService()


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
