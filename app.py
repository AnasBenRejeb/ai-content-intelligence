#!/usr/bin/env python3
"""
Production Flask App for AI Content Intelligence Platform
Deployed on Render.com with auto-scaling and self-healing
"""
from flask import Flask, render_template, jsonify, send_from_directory, request, render_template_string
from pathlib import Path
import logging
import os
from datetime import datetime
import json
from functools import wraps
import hashlib

# Setup logging (NO SENSITIVE DATA IN LOGS)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security: Filter sensitive data from logs
class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        # Remove any potential API keys or tokens from logs
        if hasattr(record, 'msg'):
            msg = str(record.msg)
            # Redact anything that looks like an API key
            import re
            record.msg = re.sub(r'[a-f0-9]{32,}', '[REDACTED]', msg)
        return True

logger.addFilter(SensitiveDataFilter())

app = Flask(__name__, 
            static_folder='website',
            template_folder='website')

# Security Headers
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # Prevent MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # XSS Protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # Content Security Policy
    response.headers['Content-Security-Policy'] = "default-src 'self' https:; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://pagead2.googlesyndication.com; style-src 'self' 'unsafe-inline';"
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # Permissions Policy
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response

# Rate Limiting (simple implementation)
from collections import defaultdict
from time import time

request_counts = defaultdict(list)
RATE_LIMIT = 100  # requests per minute
RATE_WINDOW = 60  # seconds

def rate_limit(f):
    """Rate limiting decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get client IP (respecting proxy headers)
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if client_ip:
            client_ip = client_ip.split(',')[0].strip()
        
        # Hash IP for privacy
        ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:16]
        
        now = time()
        # Clean old requests
        request_counts[ip_hash] = [req_time for req_time in request_counts[ip_hash] 
                                    if now - req_time < RATE_WINDOW]
        
        # Check rate limit
        if len(request_counts[ip_hash]) >= RATE_LIMIT:
            logger.warning(f"Rate limit exceeded for client {ip_hash}")
            return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
        
        # Add current request
        request_counts[ip_hash].append(now)
        
        return f(*args, **kwargs)
    return decorated_function

# Health check endpoint for auto-healing
@app.route('/health')
@rate_limit
def health():
    """Health check for Render.com monitoring - NO SENSITIVE DATA"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'AI Content Intelligence Platform'
    }), 200

@app.route('/')
@rate_limit
def index():
    """Main landing page - NO USER DATA COLLECTED"""
    try:
        return send_from_directory('website', 'index.html')
    except Exception as e:
        logger.error(f"Error serving index: {str(e)[:100]}")  # Limit error message length
        return jsonify({'error': 'Service temporarily unavailable'}), 503

@app.route('/blog')
@app.route('/blog.html')
def blog():
    """Blog page listing all articles"""
    try:
        base_dir = Path(__file__).parent
        articles_dir = base_dir / 'generated_articles'
        
        if not articles_dir.exists():
            return generate_initial_blog()
        
        # Get all articles
        articles = []
        for article_file in articles_dir.glob('*.md'):
            try:
                content = article_file.read_text(encoding='utf-8')
                lines = content.split('\n')
                title = "Untitled"
                preview = ""
                
                for line in lines:
                    if line.startswith('# '):
                        title = line.replace('# ', '').strip()
                    elif line.strip() and not line.startswith('#') and not line.startswith('**'):
                        preview = line.strip()[:200]
                        break
                
                articles.append({
                    'title': title,
                    'preview': preview,
                    'filename': article_file.stem,
                    'created': datetime.fromtimestamp(article_file.stat().st_mtime).isoformat()
                })
            except Exception as e:
                logger.error(f"Error reading article: {e}")
                continue
        
        # Sort by date
        articles.sort(key=lambda x: x['created'], reverse=True)
        
        # Generate blog listing page
        return render_template_string(generate_blog_listing(articles))
    except Exception as e:
        logger.error(f"Error serving blog: {e}")
        return generate_initial_blog()

@app.route('/article/<filename>')
def article(filename):
    """Individual article page"""
    try:
        base_dir = Path(__file__).parent
        articles_dir = base_dir / 'generated_articles'
        article_file = articles_dir / f"{filename}.md"
        
        if not article_file.exists():
            return jsonify({'error': 'Article not found'}), 404
        
        content = article_file.read_text(encoding='utf-8')
        
        # Parse markdown content
        lines = content.split('\n')
        title = "Untitled"
        body_lines = []
        
        for line in lines:
            if line.startswith('# '):
                title = line.replace('# ', '').strip()
            else:
                body_lines.append(line)
        
        body = '\n'.join(body_lines)
        
        # Generate article page
        return render_template_string(generate_article_page(title, body, filename))
    except Exception as e:
        logger.error(f"Error serving article: {e}")
        return jsonify({'error': 'Article not found'}), 404

@app.route('/api/articles')
@rate_limit
def api_articles():
    """API endpoint for articles - NO USER DATA EXPOSED"""
    try:
        # Use absolute path relative to this file
        base_dir = Path(__file__).parent
        articles_dir = base_dir / 'generated_articles'
        
        logger.info(f"Looking for articles in: {articles_dir.absolute()}")
        logger.info(f"Directory exists: {articles_dir.exists()}")
        
        if not articles_dir.exists():
            logger.warning(f"Articles directory not found at {articles_dir.absolute()}")
            return jsonify({'articles': [], 'count': 0, 'debug': str(articles_dir.absolute())})
        
        articles = []
        article_files = list(articles_dir.glob('*.md'))
        logger.info(f"Found {len(article_files)} article files")
        
        for article_file in article_files[:20]:  # Limit to 20
            try:
                content = article_file.read_text(encoding='utf-8')
                lines = content.split('\n')
                title = "Untitled"
                preview = ""
                
                for line in lines:
                    if line.startswith('# '):
                        title = line.replace('# ', '').strip()
                    elif line.strip() and not line.startswith('#'):
                        preview = line.strip()[:200]
                        break
                
                articles.append({
                    'title': title,
                    'preview': preview,
                    'filename': article_file.name,
                    'created': datetime.fromtimestamp(article_file.stat().st_mtime).isoformat()
                })
            except Exception as e:
                logger.error(f"Error reading article: {str(e)[:50]}")
                continue
        
        return jsonify({
            'articles': sorted(articles, key=lambda x: x['created'], reverse=True),
            'count': len(articles)
        })
    except Exception as e:
        logger.error(f"Error in API: {str(e)[:100]}")
        return jsonify({'error': 'API error'}), 500

@app.route('/api/stats')
def api_stats():
    """System statistics API"""
    try:
        base_dir = Path(__file__).parent
        articles_dir = base_dir / 'generated_articles'
        article_count = len(list(articles_dir.glob('*.md'))) if articles_dir.exists() else 0
        
        return jsonify({
            'articles_generated': article_count,
            'status': 'operational',
            'last_updated': datetime.now().isoformat(),
            'uptime': 'continuous'
        })
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': 'Stats unavailable'}), 500

@app.route('/sitemap.xml')
def sitemap():
    """SEO sitemap"""
    try:
        return send_from_directory('website', 'sitemap.xml')
    except:
        return generate_sitemap()

@app.route('/robots.txt')
def robots():
    """Robots.txt for SEO"""
    try:
        return send_from_directory('website', 'robots.txt')
    except:
        return """User-agent: *
Allow: /
Sitemap: https://your-app.onrender.com/sitemap.xml"""

def generate_initial_blog():
    """Generate initial blog page if it doesn't exist"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Generated Articles | AI Content Intelligence</title>
    <meta name="description" content="Latest AI-generated articles. Fresh content updated automatically.">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        h1 { font-size: 42px; margin-bottom: 20px; text-align: center; color: #2563eb; }
        .subtitle { text-align: center; color: #666; margin-bottom: 40px; font-size: 18px; }
        .status { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
        .status h2 { color: #10b981; margin-bottom: 15px; }
        .status p { color: #666; font-size: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI Content Intelligence Platform</h1>
        <p class="subtitle">Autonomous content generation system - Now live!</p>
        <div class="status">
            <h2>✅ System Operational</h2>
            <p>Articles are being generated automatically every 12 hours.</p>
            <p>Check back soon for fresh AI-generated content!</p>
        </div>
    </div>
</body>
</html>"""
    return html

def generate_sitemap():
    """Generate sitemap if it doesn't exist"""
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://your-app.onrender.com/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://your-app.onrender.com/blog</loc>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>"""

@app.errorhandler(404)
def not_found(e):
    """Custom 404 page"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    """Custom 500 page"""
    logger.error(f"Server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500

def generate_blog_listing(articles):
    """Generate blog listing page HTML"""
    articles_html = ""
    for article in articles:
        articles_html += f"""
        <div class="article-card">
            <div class="article-image">📰</div>
            <div class="article-content">
                <div class="article-meta">
                    <span>🕒 {datetime.fromisoformat(article['created']).strftime('%B %d, %Y')}</span>
                    <span>🤖 AI Generated</span>
                </div>
                <h3>{article['title']}</h3>
                <p>{article['preview']}...</p>
                <a href="/article/{article['filename']}" class="read-more">Read Full Article →</a>
            </div>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>All Articles | AI Content Intelligence</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; background: #f8f9fa; }}
        header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header-content {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 24px; font-weight: bold; }}
        nav a {{ color: white; text-decoration: none; margin-left: 30px; }}
        .container {{ max-width: 1200px; margin: 40px auto; padding: 0 20px; }}
        h1 {{ font-size: 36px; margin-bottom: 30px; color: #333; }}
        .articles-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 30px; }}
        .article-card {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.3s; }}
        .article-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.15); }}
        .article-image {{ width: 100%; height: 200px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; font-size: 48px; }}
        .article-content {{ padding: 25px; }}
        .article-meta {{ display: flex; gap: 15px; margin-bottom: 15px; font-size: 13px; color: #999; }}
        .article-card h3 {{ font-size: 20px; margin-bottom: 12px; color: #333; }}
        .article-card p {{ color: #666; margin-bottom: 15px; }}
        .read-more {{ color: #667eea; text-decoration: none; font-weight: 600; }}
        .read-more:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="logo">🤖 AI Content Intelligence</div>
            <nav>
                <a href="/">Home</a>
                <a href="/blog">Articles</a>
            </nav>
        </div>
    </header>
    <div class="container">
        <h1>📰 All Articles</h1>
        <div class="articles-grid">
            {articles_html}
        </div>
    </div>
</body>
</html>"""

def generate_article_page(title, content, filename):
    """Generate individual article page HTML"""
    # Simple markdown to HTML conversion
    html_content = content.replace('\n\n', '</p><p>').replace('\n', '<br>')
    html_content = f'<p>{html_content}</p>'
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | AI Content Intelligence</title>
    <meta name="description" content="{title}">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.8; color: #333; background: #f8f9fa; }}
        header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header-content {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 24px; font-weight: bold; }}
        nav a {{ color: white; text-decoration: none; margin-left: 30px; }}
        .container {{ max-width: 800px; margin: 40px auto; padding: 0 20px; }}
        .article {{ background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1 {{ font-size: 36px; margin-bottom: 20px; color: #333; line-height: 1.3; }}
        .meta {{ color: #999; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #f0f0f0; }}
        .content {{ font-size: 18px; line-height: 1.8; }}
        .content p {{ margin-bottom: 20px; }}
        .back-link {{ display: inline-block; margin-top: 30px; color: #667eea; text-decoration: none; font-weight: 600; }}
        .back-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="logo">🤖 AI Content Intelligence</div>
            <nav>
                <a href="/">Home</a>
                <a href="/blog">Articles</a>
            </nav>
        </div>
    </header>
    <div class="container">
        <article class="article">
            <h1>{title}</h1>
            <div class="meta">
                <span>🤖 AI Generated</span> • 
                <span>📰 Latest News</span>
            </div>
            <div class="content">
                {html_content}
            </div>
            <a href="/blog" class="back-link">← Back to All Articles</a>
        </article>
    </div>
</body>
</html>"""

if __name__ == '__main__':
    # Create required directories
    Path('website').mkdir(exist_ok=True)
    Path('generated_articles').mkdir(exist_ok=True)
    Path('logs').mkdir(exist_ok=True)
    
    # Get port from environment (Render provides this)
    port = int(os.environ.get('PORT', 10000))
    
    logger.info(f"🚀 Starting AI Content Intelligence Platform on port {port}")
    
    # Run with production settings
    app.run(host='0.0.0.0', port=port, debug=False)
