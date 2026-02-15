#!/usr/bin/env python3
"""
Production Scheduler - Runs every 12 hours
Generates articles and publishes to website
"""
import schedule
import time
import logging
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestrator import Orchestrator
from src.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/production.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ProductionScheduler:
    """Production scheduler for automated content generation"""
    
    def __init__(self):
        self.orchestrator = Orchestrator()
        self.run_count = 0
        
    def run_pipeline(self):
        """Run the content generation pipeline"""
        try:
            logger.info("=" * 60)
            logger.info(f"PRODUCTION RUN #{self.run_count + 1} STARTED")
            logger.info(f"Time: {datetime.now().isoformat()}")
            logger.info("=" * 60)
            
            # Run pipeline
            result = self.orchestrator.run_pipeline()
            
            if result.get("success"):
                logger.info("✅ Pipeline completed successfully")
                logger.info(f"Collected: {result.get('collected_count', 0)} titles")
                logger.info(f"Analyzed: {result.get('analyzed_count', 0)} titles")
                logger.info(f"Retrieved: {result.get('retrieved_count', 0)} articles")
                logger.info(f"Generated: {result.get('generated_count', 0)} articles")
                logger.info(f"Execution time: {result.get('execution_time', 0):.2f}s")
                
                # Publish to website
                self.publish_to_website(result)
                
                self.run_count += 1
            else:
                logger.error(f"❌ Pipeline failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"❌ Critical error in pipeline: {e}", exc_info=True)
        
        finally:
            logger.info("=" * 60)
            logger.info(f"PRODUCTION RUN #{self.run_count + 1} COMPLETED")
            logger.info("=" * 60)
            logger.info("")
    
    def publish_to_website(self, result):
        """Publish generated articles to website"""
        try:
            logger.info("📤 Publishing articles to website...")
            
            # Get generated articles
            generated_dir = settings.generated_articles_dir
            articles = list(generated_dir.glob("*.md"))
            
            # Create blog page
            self.create_blog_page(articles[-10:])  # Latest 10 articles
            
            logger.info(f"✅ Published {len(articles[-10:])} articles to website")
            
        except Exception as e:
            logger.error(f"❌ Failed to publish to website: {e}")
    
    def create_blog_page(self, articles):
        """Create blog page with latest articles"""
        blog_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Latest AI-Generated Articles | AI Content Intelligence</title>
    <meta name="description" content="Read our latest AI-generated articles. Fresh content updated every 12 hours.">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        h1 { font-size: 42px; margin-bottom: 40px; text-align: center; }
        .articles-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 30px; }
        .article-card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .article-card:hover { transform: translateY(-5px); }
        .article-card h2 { font-size: 24px; margin-bottom: 15px; color: #2563eb; }
        .article-card p { color: #666; margin-bottom: 15px; }
        .read-more { color: #2563eb; text-decoration: none; font-weight: 600; }
        .timestamp { color: #999; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Latest AI-Generated Articles</h1>
        <p style="text-align: center; margin-bottom: 40px; color: #666;">
            Fresh content generated every 12 hours by our AI Content Intelligence Platform
        </p>
        <div class="articles-grid">
"""
        
        for article_path in articles:
            try:
                # Read article
                content = article_path.read_text(encoding='utf-8')
                
                # Extract title (first line starting with #)
                lines = content.split('\n')
                title = "Untitled"
                preview = ""
                
                for line in lines:
                    if line.startswith('# '):
                        title = line.replace('# ', '').strip()
                    elif line.strip() and not line.startswith('#'):
                        preview = line.strip()[:200] + "..."
                        break
                
                # Get timestamp
                timestamp = datetime.fromtimestamp(article_path.stat().st_mtime)
                
                blog_html += f"""
            <div class="article-card">
                <h2>{title}</h2>
                <p class="timestamp">Generated: {timestamp.strftime('%Y-%m-%d %H:%M')}</p>
                <p>{preview}</p>
                <a href="/articles/{article_path.name}" class="read-more">Read More →</a>
            </div>
"""
            except Exception as e:
                logger.error(f"Error processing article {article_path}: {e}")
        
        blog_html += """
        </div>
    </div>
</body>
</html>
"""
        
        # Save blog page
        blog_path = Path("website/blog.html")
        blog_path.write_text(blog_html, encoding='utf-8')
        logger.info(f"✅ Blog page created: {blog_path}")
    
    def start(self):
        """Start the scheduler"""
        logger.info("🚀 Production Scheduler Starting...")
        logger.info(f"Schedule: Every 12 hours")
        logger.info(f"First run: Immediately")
        logger.info("")
        
        # Run immediately on start
        self.run_pipeline()
        
        # Schedule every 12 hours
        schedule.every(12).hours.do(self.run_pipeline)
        
        logger.info("⏰ Scheduler active. Waiting for next run...")
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


def main():
    """Main entry point"""
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Create website directory
    Path("website").mkdir(exist_ok=True)
    
    # Start scheduler
    scheduler = ProductionScheduler()
    scheduler.start()


if __name__ == "__main__":
    main()
