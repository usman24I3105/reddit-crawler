#!/usr/bin/env python3
"""
Master script to generate keywords from templates and load them into the database.

This script:
1. Generates keywords using generate_keywords.py
2. Loads them into the database using load_generated_keywords.py

Usage:
    python scripts/setup_keywords.py
    python scripts/setup_keywords.py --min-score 10  # Only high-scoring keywords
"""
import sys
import argparse
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logging import get_logger

logger = get_logger(__name__)

# Paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
KEYWORDS_DIR = PROJECT_ROOT / 'keywords'
SCRIPTS_DIR = PROJECT_ROOT / 'core' / 'scripts'


def generate_keywords(min_score: int = 0, limit: int = None, output_file: str = None):
    """Generate keywords from templates"""
    if output_file is None:
        output_file = str(KEYWORDS_DIR / 'generated_keywords.csv')
    
    templates_file = str(KEYWORDS_DIR / 'master_templates_v3_complete.txt')
    places_file = str(KEYWORDS_DIR / 'places_california_complete_v2.txt')
    weights_file = str(KEYWORDS_DIR / 'intent_weights_v2.json')
    
    # Check if files exist
    if not Path(templates_file).exists():
        raise FileNotFoundError(f"Templates file not found: {templates_file}")
    if not Path(places_file).exists():
        raise FileNotFoundError(f"Places file not found: {places_file}")
    if not Path(weights_file).exists():
        logger.warning(f"Weights file not found: {weights_file}, continuing without weights")
        weights_file = None
    
    # Build command
    cmd = [
        sys.executable,
        str(KEYWORDS_DIR / 'generate_keywords.py'),
        '--templates', templates_file,
        '--places', places_file,
        '--out', output_file,
        '--min-score', str(min_score),
    ]
    
    if weights_file:
        cmd.extend(['--weights', weights_file])
    
    if limit:
        cmd.extend(['--limit', str(limit)])
    
    logger.info(f"Generating keywords...")
    logger.info(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=str(KEYWORDS_DIR), check=True, capture_output=True, text=True)
        logger.info(f"Keyword generation output:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"Keyword generation warnings:\n{result.stderr}")
        return output_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Keyword generation failed: {e.stderr}")
        raise


def load_keywords(keywords_file: str):
    """Load keywords into database"""
    format_type = 'jsonl' if keywords_file.endswith('.jsonl') else 'csv'
    
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / 'load_generated_keywords.py'),
        '--keywords', keywords_file,
        '--format', format_type,
    ]
    
    logger.info(f"Loading keywords into database...")
    logger.info(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=str(SCRIPTS_DIR.parent), check=True, capture_output=True, text=True)
        logger.info(f"Keyword loading output:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"Keyword loading warnings:\n{result.stderr}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Keyword loading failed: {e.stderr}")
        raise


def main():
    parser = argparse.ArgumentParser(description="Generate and load keywords into database")
    parser.add_argument('--min-score', type=int, default=0, help="Minimum intent score (default: 0)")
    parser.add_argument('--limit', type=int, default=None, help="Limit number of keywords (default: no limit)")
    parser.add_argument('--output', default=None, help="Output file path (default: keywords/generated_keywords.csv)")
    parser.add_argument('--skip-generation', action='store_true', help="Skip keyword generation, only load existing file")
    parser.add_argument('--keywords-file', default=None, help="Path to existing keywords file to load")
    args = parser.parse_args()
    
    try:
        if args.skip_generation:
            if args.keywords_file:
                keywords_file = args.keywords_file
            else:
                keywords_file = str(KEYWORDS_DIR / 'generated_keywords.csv')
            
            if not Path(keywords_file).exists():
                raise FileNotFoundError(f"Keywords file not found: {keywords_file}")
            
            logger.info(f"Loading existing keywords from: {keywords_file}")
        else:
            # Generate keywords
            keywords_file = generate_keywords(
                min_score=args.min_score,
                limit=args.limit,
                output_file=args.output
            )
        
        # Load keywords into database
        load_keywords(keywords_file)
        
        logger.info("=" * 60)
        logger.info("Keyword setup complete!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

