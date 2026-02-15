# 🔒 Security Policy

## Overview

This project implements enterprise-grade security practices to protect sensitive data, API keys, and user information.

## Security Measures Implemented

### 1. Environment Variables
- ✅ All API keys stored in `.env` file (never committed to Git)
- ✅ `.env` file explicitly ignored in `.gitignore`
- ✅ Environment variables loaded via `pydantic-settings`
- ✅ No hardcoded credentials in source code

### 2. Git Security
- ✅ `.gitignore` configured to exclude sensitive files
- ✅ Jupyter notebooks excluded (may contain API keys)
- ✅ Deployment files with credentials excluded
- ✅ No personal information in commit history

### 3. API Key Protection
- ✅ Keys stored as environment variables on Render.com
- ✅ Keys never exposed in public repository
- ✅ Keys rotatable without code changes
- ✅ Separate keys for development and production

### 4. Application Security
- ✅ HTTPS enforced (free SSL via Render)
- ✅ Rate limiting on API endpoints
- ✅ Input validation and sanitization
- ✅ Error messages don't expose sensitive info
- ✅ Health check endpoint for monitoring

### 5. Data Protection
- ✅ No user data collection
- ✅ No personal information stored
- ✅ GDPR compliant by design
- ✅ Privacy-focused architecture

## Configuration

### Required Environment Variables

```bash
# API Keys (REQUIRED)
NEWSAPI_KEY=your_newsapi_key_here
GNEWS_API_KEY=your_gnews_key_here

# Application Settings
LOG_LEVEL=INFO
MAX_WORKERS=5
PYTHON_VERSION=3.10.0
```

### Setting Up Environment Variables

#### Local Development
1. Copy `.env.example` to `.env`
2. Add your actual API keys
3. Never commit `.env` to Git

#### Production (Render.com)
1. Go to Dashboard → Your Service → Environment
2. Add each variable individually
3. Keys are encrypted at rest
4. Keys never appear in logs

## Best Practices

### For Developers

1. **Never commit sensitive data**
   - Check files before committing
   - Use `git status` to review changes
   - Review `.gitignore` regularly

2. **Rotate API keys regularly**
   - Change keys every 90 days
   - Update in Render dashboard
   - No code changes needed

3. **Use separate keys for environments**
   - Development keys
   - Staging keys
   - Production keys

4. **Review dependencies**
   - Keep packages updated
   - Check for security vulnerabilities
   - Use `pip audit` regularly

### For Deployment

1. **Render.com Security**
   - Environment variables encrypted
   - HTTPS enforced automatically
   - DDoS protection included
   - Regular security updates

2. **Monitoring**
   - Check logs for suspicious activity
   - Monitor API usage
   - Set up alerts for errors

3. **Access Control**
   - Limit who can access Render dashboard
   - Use strong passwords
   - Enable 2FA on GitHub and Render

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. **DO NOT** disclose publicly
3. Email: security@your-domain.com (replace with actual)
4. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Checklist

### Before Deployment
- [ ] All API keys in environment variables
- [ ] `.env` file in `.gitignore`
- [ ] No hardcoded credentials in code
- [ ] No personal information in code
- [ ] Dependencies up to date
- [ ] Security scan completed

### After Deployment
- [ ] HTTPS working
- [ ] Environment variables set on Render
- [ ] Health check passing
- [ ] Logs reviewed
- [ ] No errors in production
- [ ] Monitoring configured

## Compliance

### GDPR
- No personal data collected
- No cookies used
- No user tracking
- Privacy by design

### API Terms of Service
- NewsAPI: Free tier, 100 requests/day
- GNews: Free tier, 100 requests/day
- Compliance with rate limits
- Attribution where required

## Updates

This security policy is reviewed and updated regularly. Last update: February 2026.

## Contact

For security concerns: security@your-domain.com (replace with actual)

---

**Remember**: Security is everyone's responsibility. When in doubt, ask!
