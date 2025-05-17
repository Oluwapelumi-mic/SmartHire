import pandas as pd
import os
import sys
import argparse
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.content_based_recommender import ContentBasedRecommender
from models.hybrid_recommender import HybridRecommender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_data(data_path):
    """Load job data from CSV file"""
    logger.info(f"Loading data from {data_path}")
    job_data = pd.read_csv(data_path)
    
    # Ensure required columns exist
    required_columns = ['id', 'title', 'description', 'skills']
    missing_columns = [col for col in required_columns if col not in job_data.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Parse skills column if it's in string format
    if job_data['skills'].dtype == 'object':
        try:
            job_data['skills'] = job_data['skills'].apply(
                lambda x: x.split(',') if isinstance(x, str) else []
            )
        except Exception as e:
            logger.warning(f"Error parsing skills column: {e}")
    
    logger.info(f"Loaded {len(job_data)} job records")
    return job_data

def train_and_save_model(job_data, model_path, model_type='content'):
    """Train recommender model and save it to disk"""
    logger.info(f"Training {model_type} model...")
    
    if model_type == 'content':
        recommender = ContentBasedRecommender()
        recommender.fit(job_data)
    elif model_type == 'hybrid':
        recommender = HybridRecommender()
        recommender.fit(job_data)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    logger.info(f"Saving model to {model_path}")
    recommender.save_model(model_path)
    logger.info("Model training and saving complete")
    
    return recommender

def main():
    parser = argparse.ArgumentParser(description="Train SmartHire recommender model")
    parser.add_argument('--data', type=str, required=True, help='Path to job data CSV')
    parser.add_argument('--output', type=str, required=True, help='Path to save model')
    parser.add_argument('--model-type', type=str, default='content', 
                        choices=['content', 'hybrid'], help='Type of recommender model')
    
    args = parser.parse_args()
    
    try:
        # Load data
        job_data = load_data(args.data)
        
        # Train and save model
        model = train_and_save_model(job_data, args.output, args.model_type)
        
        # Quick validation
        if len(job_data) > 0:
            sample_job = job_data.iloc[0]
            test_document = f"{sample_job['title']} {' '.join(sample_job['skills'])}"
            recommendations = model.get_recommendations(test_document, top_n=5)
            logger.info(f"Sample recommendations: {recommendations}")
        
    except Exception as e:
        logger.error(f"Error in training pipeline: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()