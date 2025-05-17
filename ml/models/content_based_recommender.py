import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

class ContentBasedRecommender:
    def __init__(self, max_features=5000):
        self.max_features = max_features
        self.tfidf_vectorizer = None
        self.job_vectors = None
        self.job_ids = None
        
        # Download nltk resources if needed
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
            
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def _preprocess_text(self, text):
        """Clean and preprocess text data"""
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize, remove stopwords, and lemmatize
        tokens = nltk.word_tokenize(text)
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words]
        
        return ' '.join(tokens)
    
    def fit(self, job_data):
        """
        Train the recommender with job data
        job_data: DataFrame with columns [id, title, description, skills]
        """
        # Preprocess text data
        job_data['processed_title'] = job_data['title'].apply(self._preprocess_text)
        job_data['processed_description'] = job_data['description'].apply(self._preprocess_text)
        
        # Process skills - ensure it's a string
        if isinstance(job_data['skills'].iloc[0], list):
            job_data['processed_skills'] = job_data['skills'].apply(lambda x: ' '.join(self._preprocess_text(skill) for skill in x))
        else:
            job_data['processed_skills'] = job_data['skills'].apply(self._preprocess_text)
        
        # Create document for each job
        job_data['document'] = (
            job_data['processed_title'] + ' ' + 
            job_data['processed_description'] + ' ' + 
            job_data['processed_skills']
        )
        
        # Initialize and fit TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=(1, 2),
            stop_words='english'
        )
        
        # Create vectors for jobs
        self.job_vectors = self.tfidf_vectorizer.fit_transform(job_data['document'])
        self.job_ids = job_data['id'].values
        
        return self
    
    def get_recommendations(self, user_document, top_n=10):
        """
        Get job recommendations based on user profile
        user_document: Text document representing user profile
        top_n: Number of recommendations to return
        """
        if not self.tfidf_vectorizer or not self.job_vectors.any():
            raise ValueError("Recommender model not fitted yet")
        
        # Preprocess user document
        processed_user_document = self._preprocess_text(user_document)
        
        # Transform user document into vector
        user_vector = self.tfidf_vectorizer.transform([processed_user_document])
        
        # Calculate similarity between user and all jobs
        similarities = cosine_similarity(user_vector, self.job_vectors)[0]
        
        # Get indices of top N most similar jobs
        top_indices = similarities.argsort()[-top_n:][::-1]
        
        # Return job IDs and similarity scores
        recommendations = [
            {"job_id": self.job_ids[i], "similarity_score": float(similarities[i])}
            for i in top_indices
        ]
        
        return recommendations
    
    def save_model(self, model_path):
        """Save the trained model to disk"""
        if not os.path.exists(os.path.dirname(model_path)):
            os.makedirs(os.path.dirname(model_path))
            
        model_data = {
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'job_vectors': self.job_vectors,
            'job_ids': self.job_ids
        }
        
        joblib.dump(model_data, model_path)
    
    def load_model(self, model_path):
        """Load a trained model from disk"""
        model_data = joblib.load(model_path)
        
        self.tfidf_vectorizer = model_data['tfidf_vectorizer']
        self.job_vectors = model_data['job_vectors']
        self.job_ids = model_data['job_ids']
        
        return self