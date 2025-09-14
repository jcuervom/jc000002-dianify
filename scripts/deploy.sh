#!/bin/bash
# Deployment script for Heroku

echo "🚀 Deploying DIAN Appointment Checker to Heroku..."

# Check if heroku is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first."
    echo "   Visit: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "❌ Not logged in to Heroku. Please run: heroku login"
    exit 1
fi

# Get app name
if [ -z "$1" ]; then
    echo "📝 Usage: ./scripts/deploy.sh <app-name>"
    exit 1
fi

APP_NAME=$1

echo "📱 Creating Heroku app: $APP_NAME"
heroku create $APP_NAME || echo "App already exists, continuing..."

echo "🔧 Setting up buildpacks..."
heroku buildpacks:clear -a $APP_NAME
heroku buildpacks:add heroku/python -a $APP_NAME
heroku buildpacks:add https://github.com/jcuervom/heroku-playwright-python-browsers.git -a $APP_NAME
heroku buildpacks:add https://github.com/playwright-community/heroku-playwright-buildpack.git -a $APP_NAME

echo "⚙️ Setting default config vars..."
heroku config:set PLAYWRIGHT_BUILDPACK_BROWSERS=chromium -a $APP_NAME
heroku config:set HEADLESS=true -a $APP_NAME

echo "🚀 Deploying to Heroku..."
git push heroku main

echo "📊 Showing app status..."
heroku ps -a $APP_NAME

echo "✅ Deployment complete!"
echo "📱 Your app is available at: https://$APP_NAME.herokuapp.com"
echo "📄 View logs with: heroku logs --tail -a $APP_NAME"
echo ""
echo "⚠️  Don't forget to set your environment variables:"
echo "   heroku config:set TELEGRAM_BOT_TOKEN=your_token -a $APP_NAME"
echo "   heroku config:set TELEGRAM_CHAT_ID=your_chat_id -a $APP_NAME"