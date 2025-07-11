#!/bin/bash

echo "🌸 Starting Hinata Discord Bot..."
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and add your Discord bot token."
    exit 1
fi

# Check if Discord token is set
if ! grep -q "DISCORD_TOKEN=" .env || grep -q "DISCORD_TOKEN=your_discord_bot_token_here" .env; then
    echo "❌ Error: Discord token not configured!"
    echo "Please edit the .env file and add your Discord bot token."
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f requirements.txt ]; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo "🚀 Starting bot..."
python3 bot.py

