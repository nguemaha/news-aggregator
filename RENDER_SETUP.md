# Quick Render Setup Guide

## 🚀 Quick Start (5 minutes)

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up (free account works)
3. Verify email

### Step 2: Deploy from GitHub
1. In Render dashboard: **New** → **Blueprint**
2. Connect GitHub (if not connected)
3. Select repository: `news-aggregator`
4. Select branch: `deployment`
5. Click **Apply** (Render reads `render.yaml` automatically)

### Step 3: Set Environment Variables
After services are created, go to `daily-digest-job` → **Environment** tab:

```
OPENAI_API_KEY=sk-...
MY_EMAIL=your.email@gmail.com
APP_PASSWORD=your_16_char_app_password
```

**Note**: `DATABASE_URL` is auto-set by Render - don't add it manually!

### Step 4: Install Chrome/ChromeDriver (Required for Selenium)
The WHO scraper uses Selenium, which requires Chrome. The Dockerfile should handle this, but if you encounter issues:

- ChromeDriver is installed via the Dockerfile
- Ensure the Dockerfile includes Chrome installation

### Step 5: Test
1. Go to `daily-digest-job` → **Logs**
2. Click **Manual Deploy** to test immediately
3. Check your email inbox

## ✅ What Gets Created

- **PostgreSQL Database**: `news-aggregator-db` (free tier)
- **Cron Job**: Runs `python main.py` daily at midnight UTC
  - Scrapes WHO news articles (past 24-72 hours)
  - Generates AI digests
  - Sends personalized email digest

## 📋 Pipeline Flow

The cron job runs the full pipeline:
1. **Scraping**: `app/runner.py` → `app/scrapers/who.py` (Selenium scraper)
2. **Digest Generation**: `app/services/process_digest.py` → OpenAI API
3. **Email Sending**: `app/services/process_email.py` → Personalized email

See `REPOSITORY_MAP.md` for detailed architecture.

## 📝 Schedule Customization

Edit `render.yaml` to change schedule:
```yaml
schedule: "0 8 * * *"  # 8 AM UTC instead of midnight
```

Then push to GitHub - Render auto-updates.

## 🔧 Configuration

### Default Parameters
- `hours=72`: Scrapes articles from past 72 hours (configurable in `main.py`)
- `top_n=10`: Top 10 articles in email digest

### Customize in `main.py`:
```python
hours = 72  # Change to 24, 48, etc.
top_n = 10  # Number of articles in email
```

## 🔍 Troubleshooting

**Database connection fails?**
- Check `DATABASE_URL` is set (should be automatic)
- Verify database service is running
- Note: Local development uses SQLite (`data/news.db`), Render uses PostgreSQL

**Selenium/Chrome errors?**
- Verify ChromeDriver is installed in Docker image
- Check Dockerfile includes Chrome dependencies
- Review logs for WebDriver errors

**Email not sending?**
- Verify Gmail app password (not regular password)
- Check `MY_EMAIL` and `APP_PASSWORD` are correct
- Ensure 2-Step Verification is enabled on Gmail account

**No articles found?**
- Check WHO website is accessible
- Verify date filtering (articles must be within specified hours)
- Review scraper logs for parsing errors

**Cron not running?**
- Check logs in Render dashboard
- Verify schedule syntax in `render.yaml`
- Ensure service is not paused

**OpenAI API errors?**
- Verify `OPENAI_API_KEY` is set correctly
- Check API quota/limits
- Review digest agent logs

## 📚 Additional Documentation

- **Architecture**: See `REPOSITORY_MAP.md` for component connections
- **Local Development**: See `README.md` for setup instructions
- **Database**: SQLite locally (`data/news.db`), PostgreSQL on Render

## 🚨 Important Notes

1. **Selenium Requirement**: The WHO scraper requires Selenium + Chrome, which adds complexity to deployment
2. **Database**: Local uses SQLite, Render uses PostgreSQL (configured via `DATABASE_URL`)
3. **ChromeDriver**: Must be compatible with Chrome version in Docker image
4. **Rate Limiting**: Be mindful of WHO website scraping - add delays if needed

