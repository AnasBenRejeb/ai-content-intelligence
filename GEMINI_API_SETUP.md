# 🤖 Google Gemini API Setup Guide

## Why Gemini API?

We use Google's Gemini API to **rewrite articles in our own words** - this is CRITICAL to avoid copyright infringement!

**Benefits:**
- ✅ 100% FREE tier (15 requests/min, 1,500/day)
- ✅ High-quality AI rewriting
- ✅ Fast and reliable
- ✅ No local model needed (saves resources)
- ✅ Professional-grade content generation

---

## Step 1: Get Your FREE API Key (2 minutes)

1. Go to: https://makersuite.google.com/app/apikey
2. Click "Get API Key"
3. Click "Create API key in new project"
4. Copy the API key (starts with `AIza...`)

**That's it!** No credit card required, completely free.

---

## Step 2: Add to GitHub Secrets (for GitHub Actions)

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `GEMINI_API_KEY`
5. Value: Paste your API key
6. Click **Add secret**

---

## Step 3: Add to Render (for deployment)

1. Go to Render dashboard: https://dashboard.render.com
2. Click on your web service
3. Go to **Environment** tab
4. Click **Add Environment Variable**
5. Key: `GEMINI_API_KEY`
6. Value: Paste your API key
7. Click **Save Changes**

---

## Step 4: Test Locally (optional)

If testing locally:

1. Copy `.env.example` to `.env`
2. Add your key:
   ```
   GEMINI_API_KEY=AIza...your_key_here
   ```
3. Run: `python -c "from src.orchestrator import Orchestrator; o = Orchestrator(); o.run_pipeline()"`

---

## How It Works - Agentic Design Pattern

Our Writer Agent uses **metacognitive thinking** (like professional newsrooms):

### 🧠 STEP 1: ANALYZE
- Understands the core story
- Identifies the best angle
- Creates a better, more engaging title
- Decides on structure and tone

### 📋 STEP 2: PLAN
- Creates detailed outline
- Plans hook/lead
- Identifies key points
- Plans conclusion

### ✍️ STEP 3: WRITE
- Writes in its own words (NOT copying!)
- Professional journalistic style
- 400-500 words
- Engaging and readable

### 🔍 STEP 4: REVIEW
- Self-critiques the article
- Identifies improvements
- Ensures quality

### 📰 STEP 5: FORMAT
- Adds proper attribution
- Includes source links
- Professional markdown formatting

**Result:** Original, high-quality articles that respect copyright!

---

## Free Tier Limits

**Gemini 1.5 Flash (FREE):**
- 15 requests per minute
- 1,500 requests per day
- 1 million tokens per minute

**Our Usage:**
- 20 articles per run = 100 API calls (5 calls per article)
- 2 runs per day = 200 calls/day
- Well within free limits! ✅

---

## What If I Don't Add the Key?

Without the Gemini API key:
- ❌ Articles will use basic templates (boring)
- ❌ May have copyright issues
- ❌ Lower quality content

With the Gemini API key:
- ✅ Professional AI-rewritten articles
- ✅ No copyright issues
- ✅ Engaging, unique content
- ✅ Better SEO and reader engagement

---

## Troubleshooting

### "GEMINI_API_KEY not found"
- Make sure you added it to GitHub Secrets
- Make sure you added it to Render Environment Variables
- Check spelling (case-sensitive!)

### "API quota exceeded"
- Free tier: 1,500 requests/day
- Our system uses ~200/day
- Should never hit limit unless running manually many times

### "API key invalid"
- Get a new key from https://makersuite.google.com/app/apikey
- Make sure you copied the entire key
- No spaces or newlines

---

## Security Notes

✅ **Safe:**
- API key in GitHub Secrets (encrypted)
- API key in Render Environment Variables (encrypted)
- Never in source code
- Never in Git history

❌ **Never:**
- Commit API key to Git
- Share API key publicly
- Put in documentation

---

## Next Steps

1. Get your free API key (2 min)
2. Add to GitHub Secrets (1 min)
3. Add to Render (1 min)
4. Trigger workflow to test
5. Watch AI-rewritten articles appear! 🎉

**Total setup time: 5 minutes**

---

**Questions?** Check the Gemini API docs: https://ai.google.dev/docs
