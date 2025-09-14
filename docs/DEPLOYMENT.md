# Deployment Guide

## Heroku Deployment

### Prerequisites

1. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
2. **Heroku CLI**: Install from [devcenter.heroku.com](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git Repository**: Your code must be in a Git repository

### Quick Deploy

Use the automated script:

```bash
./scripts/deploy.sh your-app-name
```

### Manual Deployment

#### 1. Create Heroku App

```bash
heroku create your-app-name
```

#### 2. Configure Buildpacks

⚠️ **Order is critical**:

```bash
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/jcuervom/heroku-playwright-python-browsers.git
heroku buildpacks:add https://github.com/playwright-community/heroku-playwright-buildpack.git
```

#### 3. Set Environment Variables

```bash
heroku config:set TELEGRAM_BOT_TOKEN=your_bot_token
heroku config:set TELEGRAM_CHAT_ID=your_chat_id
heroku config:set PLAYWRIGHT_BUILDPACK_BROWSERS=chromium
heroku config:set HEADLESS=true
```

#### 4. Deploy

```bash
git push heroku main
```

### Monitoring

```bash
# View logs
heroku logs --tail

# Check app status
heroku ps

# Restart app
heroku restart

# Scale dynos
heroku ps:scale web=1
```

### Cost Optimization

#### Free Tier (Hobby)
- 550-1000 free dyno hours/month
- App sleeps after 30 minutes of inactivity
- 512MB RAM limit

#### Paid Tiers
- **Hobby ($7/month)**: No sleep, 512MB RAM
- **Standard-1X ($25/month)**: No sleep, 512MB RAM, metrics
- **Standard-2X ($50/month)**: No sleep, 1GB RAM, metrics

### Memory Management

The app is optimized for 512MB environments:

```python
# Browser args for memory efficiency
--max_old_space_size=460
--single-process
--disable-dev-shm-usage
```

## Alternative Deployments

### Railway

1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically

### DigitalOcean App Platform

1. Create app from GitHub
2. Configure environment variables
3. Add Playwright buildpack

### Docker

```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.40.0-focal

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### VPS Deployment

```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip

# Clone repository
git clone your-repo
cd citasDian

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium

# Run with supervisor
sudo apt install supervisor
```

## Environment Configuration

### Development
```env
HEADLESS=false
DEBUG=true
CHECK_INTERVAL=300
```

### Production
```env
HEADLESS=true
DEBUG=false
CHECK_INTERVAL=600
```

### Staging
```env
HEADLESS=true
DEBUG=true
CHECK_INTERVAL=300
TELEGRAM_CHAT_ID=staging_chat_id
```