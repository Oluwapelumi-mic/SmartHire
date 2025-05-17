import pandas as pd
import numpy as np
import os
import sys
import argparse
import logging
from sklearn.model_selection import train_test_split

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.content_based_recommender import ContentBasedRecommender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def calculate_metrics(recommendations, ground_truth):
    """
    Calculate recommendation metrics
    
    Parameters:
    - recommendations: List of job IDs recommended for each user
    - ground_truth: List of relevant job IDs for each user
    
    Returns:
    - Dictionary of metrics (precision, recall, ndcg)
    """
    precision_at_k = []
    recall_at_k = []
    ndcg_at_k = []
    
    # Calculate metrics for each user
    for user_recs, user_truth in zip(recommendations, ground_truth):
        # Skip users with no relevant items
        if not user_truth:
            continue
        
        # Precision@k
        hits = len(set(user_recs) & set(user_truth))
        precision = hits / len(user_recs) if user_recs else 0
        precision_at_k.append(precision)
        
        # Recall@k
        recall = hits / len(user_truth) if user_truth else 0
        recall_at_k.append(recall)
        
        # NDCG@k (Normalized Discounted Cumulative Gain)
        dcg = 0
        for i, job_id in enumerate(user_recs):
            if job_id in user_truth:
                # Calculate DCG (using binary relevance 0/1)
                dcg += 1 / np.log2(i + 2)  # +2 because i is 0-indexed
        
        # Calculate ideal DCG
        idcg = sum(1 / np.log2(i + 2) for i in range(min(len(user_truth), len(user_recs))))
        ndcg = dcg / idcg if idcg > 0 else 0
        ndcg_at_k.append(ndcg)
    
    # Calculate average metrics
    metrics = {
        'precision': np.mean(precision_at_k) if precision_at_k else 0,
        'recall': np.mean(recall_at_k) if recall_at_k else 0,
        'ndcg': np.mean(ndcg_at_k) if ndcg_at_k else 0
    }
    
    return metrics

def evaluate_model(model, test_data, user_profiles=None, k=10):
    """
    Evaluate recommender model performance
    
    Parameters:
    - model: Trained recommender model
    - test_data: DataFrame of job data for evaluation
    - user_profiles: DataFrame of user profiles (if None, we simulate users)
    - k: Number of recommendations to generate
    
    Returns:
    - Dictionary of evaluation metrics
    """
    # If no user profiles provided, simulate by using job descriptions as user profiles
    if user_profiles is None:
        logger.info("No user profiles provided. Simulating user profiles from job data.")
        
        # Create synthetic user profiles based on job clusters
        np.random.seed(42)
        num_users = min(50, len(test_data))
        
        # Randomly select jobs to create synthetic user profiles
        sample_indices = np.random.choice(len(test_data), num_users, replace=False)
        
        user_profiles = []
        ground_truth = []
        
        for idx in sample_indices:
            job = test_data.iloc[idx]
            # Create user profile from job title and skills
            profile_job_ids = []
            
            # Find similar jobs to this one to use as ground truth
            job_titles = test_data['title'].str.lower()
            similar_job_mask = job_titles.str.contains(job['title'].lower())
            
            # Add the sample job and similar jobs to ground truth
            similar_jobs = test_data[similar_job_mask]
            if len(similar_jobs) > 1:  # Ensure we have more than just the sample job
                profile_job_ids = similar_jobs['id'].tolist()
            else:
                # If no similar jobs by title, just use a few random jobs
                random_ids = test_data.sample(min(5, len(test_data)))['id'].tolist()
                profile_job_ids = [job['id']] + random_ids
            
            # Create user document from the main job
            user_document = f"{job['title']} {job['description']} {' '.join(job['skills']) if isinstance(job['skills'], list) else job['skills']}"
            
            user_profiles.append(user_document)
            ground_truth.append(profile_job_ids)
    
    # Generate recommendations for each user
    all_recommendations = []
    
    for user_doc in user_profiles:
        try:
            # Get top-k recommendations
            recs = model.get_recommendations(user_doc, top_n=k)
            rec_ids = [rec['job_id'] for rec in recs]
            all_recommendations.append(rec_ids)
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            all_recommendations.append([])
    
    # Calculate evaluation metrics
    metrics = calculate_metrics(all_recommendations, ground_truth)
    
    return metrics

def main():
    parser = argparse.ArgumentParser(description="Evaluate SmartHire recommender model")
    parser.add_argument('--data', type=str, required=True, help='Path to job data CSV')
    parser.add_argument('--model', type=str, help='Path to trained model (optional)')
    parser.add_argument('--k', type=int, default=10, help='Number of recommendations to evaluate')
    
    args = parser.parse_args()
    
    try:
        # Load data
        logger.info(f"Loading data from {args.data}")
        job_data = pd.read_csv(args.data)
        
        # Split data into train/test
        train_data, test_data = train_test_split(job_data, test_size=0.2, random_state=42)
        
        # Create and train model if not provided
        if args.model and os.path.exists(args.model):
            logger.info(f"Loading model from {args.model}")
            recommender = ContentBasedRecommender()
            recommender.load_model(args.model)
        else:
            logger.info("Training new model for evaluation")
            recommender = ContentBasedRecommender()
            recommender.fit(train_data)
        
        # Evaluate model
        logger.info(f"Evaluating model with k={args.k}")
        metrics = evaluate_model(recommender, test_data, k=args.k)
        
        # Print results
        logger.info("Evaluation results:")
        logger.info(f"Precision@{args.k}: {metrics['precision']:.4f}")
        logger.info(f"Recall@{args.k}: {metrics['recall']:.4f}")
        logger.info(f"NDCG@{args.k}: {metrics['ndcg']:.4f}")
        
    except Exception as e:
        logger.error(f"Error in evaluation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()