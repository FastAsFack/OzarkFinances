#!/bin/bash
# Force update script - Run this on the Pi to get immediate updates
# This bypasses waiting for GitHub Actions

echo "🚀 FORCE UPDATE: Pulling latest changes and rebuilding container..."

# Navigate to the deployment directory
cd ~/ozark-finances || exit 1

# Pull latest changes from git
echo "📥 Pulling latest changes from Git..."
git remote set-url origin https://github.com/FastAsFack/OzarkFinances.git
git pull origin Main

# Stop the current container
echo "🛑 Stopping current container..."
docker compose down

# Remove old images to force rebuild
echo "🗑️ Removing old Docker images..."
docker image prune -f
docker compose pull

# Rebuild and start the container
echo "🔨 Rebuilding and starting container..."
docker compose up -d --build

# Show container status
echo "📊 Container status:"
docker compose ps

# Show recent logs
echo "📋 Recent logs:"
docker compose logs --tail=20 ozark-finances

echo "✅ Force update completed!"
echo "🌐 Your application should now have the latest changes"
echo "🔄 If issues persist, try clearing your browser cache (Ctrl+F5)"
