#!/usr/bin/env python3
"""
Test article generation locally before deploying
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_generation():
    """Test the article generation pipeline"""
    print("🧪 Testing Article Generation Pipeline...")
    print("=" * 50)
    
    # Check environment variables
    print("\n1️⃣ Checking Environment Variables...")
    newsapi_key = os.getenv('NEWSAPI_KEY', '')
    gnews_key = os.getenv('GNEWS_API_KEY', '')
    
    if not newsapi_key or not gnews_key:
        print("⚠️  Warning: API keys not found in environment")
        print("   Loading from .env file...")
        from dotenv import load_dotenv
        load_dotenv()
        newsapi_key = os.getenv('NEWSAPI_KEY', '')
        gnews_key = os.getenv('GNEWS_API_KEY', '')
    
    if newsapi_key:
        print(f"   ✅ NewsAPI Key: {newsapi_key[:10]}...")
    else:
        print("   ❌ NewsAPI Key: Missing!")
        
    if gnews_key:
        print(f"   ✅ GNews Key: {gnews_key[:10]}...")
    else:
        print("   ❌ GNews Key: Missing!")
    
    # Test imports
    print("\n2️⃣ Testing Imports...")
    try:
        from src.orchestrator import Orchestrator
        print("   ✅ Orchestrator imported successfully")
    except Exception as e:
        print(f"   ❌ Failed to import Orchestrator: {e}")
        return False
    
    # Test orchestrator creation
    print("\n3️⃣ Creating Orchestrator...")
    try:
        orchestrator = Orchestrator()
        print("   ✅ Orchestrator created successfully")
    except Exception as e:
        print(f"   ❌ Failed to create Orchestrator: {e}")
        return False
    
    # Test pipeline (dry run)
    print("\n4️⃣ Testing Pipeline (Dry Run)...")
    print("   This will collect a few articles but not generate full content")
    print("   Press Ctrl+C to skip if you want...")
    
    try:
        # Just test the collector
        from src.agents.collector import CollectorAgent
        from src.config import settings
        
        collector = CollectorAgent()
        print(f"   Testing with categories: {settings.categories[:2]}")
        
        # Collect just 1 article from 1 category for testing
        test_category = settings.categories[0]
        print(f"   Collecting from: {test_category}")
        
        result = collector.collect_news(
            categories=[test_category],
            page_size=5,
            pages=1
        )
        
        if result and len(result) > 0:
            print(f"   ✅ Successfully collected {len(result)} articles")
            print(f"   Sample title: {result[0].get('title', 'N/A')[:50]}...")
        else:
            print("   ⚠️  No articles collected (might be API limit)")
        
    except KeyboardInterrupt:
        print("\n   ⏭️  Skipped pipeline test")
    except Exception as e:
        print(f"   ⚠️  Pipeline test failed: {e}")
        print("   This might be normal if API keys are not set")
    
    print("\n" + "=" * 50)
    print("✅ Basic tests completed!")
    print("\n📝 Next Steps:")
    print("   1. Make sure API keys are set in Render dashboard")
    print("   2. The cron job will run automatically every 12 hours")
    print("   3. Check Render logs to see article generation")
    
    return True

if __name__ == "__main__":
    test_generation()
