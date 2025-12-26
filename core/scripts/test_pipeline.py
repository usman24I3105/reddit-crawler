#!/usr/bin/env python
"""
Test the full crawler pipeline.
"""
import os
import sys
from pathlib import Path

# Setup Django before importing anything else
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from src.pipeline.crawler_pipeline import CrawlerPipeline

def test_pipeline():
    """Test the full crawler pipeline"""
    print("=" * 60)
    print("TESTING CRAWLER PIPELINE")
    print("=" * 60)
    
    try:
        pipeline = CrawlerPipeline()
        print("\nPipeline initialized, running...")
        result = pipeline.run()
        
        print("\n" + "=" * 60)
        print("PIPELINE RESULT")
        print("=" * 60)
        print(f"Total Fetched: {result.get('total_fetched', 0)}")
        print(f"Total Saved: {result.get('total_saved', 0)}")
        print(f"Duplicates Skipped: {result.get('duplicates_skipped', 0)}")
        print("=" * 60)
        
        return result
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    test_pipeline()



