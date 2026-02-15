# ⏰ RENDER CRON JOB SETUP
## Automatic Article Generation Every 12 Hours

---

## 🎯 QUICK SETUP (5 Minutes)

### **Step 1: Create Cron Job**

1. Go to: https://dashboard.render.com
2. Click **"New +"** (top right)
3. Select **"Cron Job"**

---

### **Step 2: Connect Repository**

1. Select: **"Build and deploy from a Git repository"**
2. Click **"Next"**
3. Find: `AnasBenRejeb/ai-content-intelligence`
4. Click **"Connect"**

---

### **Step 3: Configure Cron Job**

**Fill in these fields:**

```
Name: article-generator
Region: Oregon (Free)
Branch: main
Schedule: 0 */12 * * *
```

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python -c "from src.orchestrator import Orchestrator; o = Orchestrator(); o.run_pipeline()"
```

**Instance Type:** Free

---

### **Step 4: Add Environment Variables**

Click **"Add Environment Variable"** for each:

```
NEWSAPI_KEY
Value: b86bc01720554a51a966fc3c72af5dda

GNEWS_API_KEY
Value: d41d8a047305a163373d164e3bb43cbe

LOG_LEVEL
Value: INFO

MAX_WORKERS
Value: 5

PYTHON_VERSION
Value: 3.10.0
```

---

### **Step 5: Create**

1. Review settings
2. Click **"Create Cron Job"**
3. Wait for first build (2-3 minutes)

---

## ✅ VERIFICATION

**Check it's working:**

1. Go to Cron Job dashboard
2. Look for "Last Run" timestamp
3. Check logs for success messages
4. Visit your site - articles should appear after first run

---

## 📅 SCHEDULE EXPLAINED

`0 */12 * * *` means:
- **0** = At minute 0
- ***/12** = Every 12 hours
- **\* \* \*** = Every day, every month, every day of week

**Runs at:** 12:00 AM, 12:00 PM (UTC)

---

## 🔧 TROUBLESHOOTING

**If cron job fails:**

1. Check logs in Render dashboard
2. Verify environment variables are set
3. Ensure API keys are valid
4. Check API rate limits (100/day each)

**Common issues:**
- Missing environment variables → Add them
- API rate limit exceeded → Wait 24 hours
- Build fails → Check requirements.txt

---

## 🎯 EXPECTED BEHAVIOR

**First Run:**
- Collects news from APIs
- Analyzes content
- Generates articles
- Saves to filesystem
- Takes ~5-10 minutes

**Subsequent Runs:**
- Checks for duplicates
- Only generates new content
- Faster (~2-5 minutes)

---

## 📊 MONITORING

**Check cron job health:**
- Render dashboard shows last run time
- Logs show success/failure
- Website shows article count increasing

**Set up alerts:**
- Render can email on failures
- Enable in Cron Job settings

---

## 🚀 OPTIMIZATION

**Want more frequent updates?**

Change schedule:
- Every 6 hours: `0 */6 * * *`
- Every 4 hours: `0 */4 * * *`
- Daily at 9 AM: `0 9 * * *`

**Note:** More frequent = higher API usage!

---

## ✅ SUCCESS CHECKLIST

- [ ] Cron job created
- [ ] Environment variables added
- [ ] First build successful
- [ ] First run completed
- [ ] Articles appearing on site
- [ ] No errors in logs

---

**Status:** READY TO AUTOMATE! 🤖
