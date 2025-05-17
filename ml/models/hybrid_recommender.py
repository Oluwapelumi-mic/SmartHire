import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .content_based_recommender import ContentBasedRecommender

class HybridRecommender:
    def __init__(self, cb_weight=0.7, cf_weight=0.3):
        """
        Initialize hybrid recommender with content-based and collaborative filtering
        cb_weight: Weight for content-based recommendations
        cf_weight: Weight for collaborative filtering recommendations
        """
        self.content_based = ContentBasedRecommender()
        self.cb_weight = cb_weight
        self.cf_weight = cf_weight
        
    def fit(self, job_data, user_job_interactions=None):
        """
        Train the hybrid recommender
        job_data: DataFrame with job information
        user_job_interactions: DataFrame with user-job interactions (for collaborative filtering)
        """
        # Train content-based recommender
        self.content_based.fit(job_data)
        
        # Here we could train a collaborative filtering model if we had user interaction data
        # For now, we'll focus on content-based recommendations
        
        return self
        
    def get_recommendations(self, user_document, user_id=None, top_n=10):
        """
        Get job recommendations for a user
        user_document: Text document representing user profile
        user_id: User ID for collaborative filtering (can be None)
        top_n: Number of recommendations to return
        """
        # Get content-based recommendations
        cb_recommendations = self.content_based.get_recommendations(user_document, top_n=top_n*2)
        
        # Here we would get collaborative filtering recommendations if we had that component
        
        # For now, just return content-based recommendations
        # In a full implementation, we would combine the two recommendation types
        return cb_recommendations[:top_n]