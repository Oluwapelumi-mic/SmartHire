import pandas as pd
import numpy as np
import argparse
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_text(text):
    """Basic text cleaning function"""
    if not isinstance(text, str):
        return ""
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def process_skills(skills):
    """Process skills array or string"""
    if isinstance(skills, list):
        return [s.strip() for s in skills if s.strip()]
    elif isinstance(skills, str):
        # Handle comma-separated skills
        if ',' in skills:
            return [s.strip() for s in skills.split(',') if s.strip()]
        # Handle space-separated skills
        return [s.strip() for s in skills.split() if s.strip()]
    return []

def prepare_job_data(input_file, output_file):
    """
    Process and clean job data
    
    Parameters:
    - input_file: Path to raw data file (CSV or JSON)
    - output_file: Path to save processed data (CSV)
    """
    logger.info(f"Processing file: {input_file}")
    
    # Determine file type from extension
    file_ext = os.path.splitext(input_file)[1].lower()
    
    # Load data based on file type
    if file_ext == '.csv':
        data = pd.read_csv(input_file)
    elif file_ext in ['.json', '.jsonl']:
        data = pd.read_json(input_file, lines=(file_ext == '.jsonl'))
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")
    
    logger.info(f"Loaded {len(data)} records")
    
    # Handle different column naming conventions
    column_mappings = {
        'job_id': 'id',
        'jobId': 'id',
        'job_title': 'title',
        'jobTitle': 'title',
        'position': 'title',
        'job_description': 'description',
        'jobDescription': 'description',
        'desc': 'description',
        'required_skills': 'skills',
        'requiredSkills': 'skills',
        'skillset': 'skills',
        'skill_tags': 'skills'
    }
    
    # Rename columns if needed
    data = data.rename(columns={old: new for old, new in column_mappings.items() 
                              if old in data.columns and new not in data.columns})
    
    # Ensure required columns exist
    required_columns = ['id', 'title', 'description']
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        raise ValueError(f"Input data missing required columns: {missing_columns}")
    
    # Add ID column if missing
    if 'id' not in data.columns:
        data['id'] = [f"job_{i}" for i in range(len(data))]
    
    # Clean text fields
    data['title'] = data['title'].apply(clean_text)
    data['description'] = data['description'].apply(clean_text)
    
    # Process skills
    if 'skills' in data.columns:
        data['skills'] = data['skills'].apply(process_skills)
    else:
        # If no skills column, extract from description (simplified)
        data['skills'] = [[]] * len(data)
        logger.warning("No skills column found. Using empty skills list.")
    
    # Remove rows with missing essential data
    data = data.dropna(subset=['title', 'description'])
    logger.info(f"Cleaned data: {len(data)} records remaining")
    
    # Save processed data
    data.to_csv(output_file, index=False)
    logger.info(f"Processed data saved to {output_file}")
    
    return data

def main():
    parser = argparse.ArgumentParser(description="Prepare job data for SmartHire recommender")
    parser.add_argument('--input', type=str, required=True, help='Path to raw data file (CSV or JSON)')
    parser.add_argument('--output', type=str, help='Path to save processed data (CSV)')
    
    args = parser.parse_args()
    
    # Generate output filename if not provided
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.dirname(args.input) or '.'
        filename = f"processed_jobs_{timestamp}.csv"
        args.output = os.path.join(output_dir, filename)
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    
    try:
        prepare_job_data(args.input, args.output)
    except Exception as e:
        logger.error(f"Error preparing data: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()