#!/bin/bash
# Simple deployment script for GitHub Actions
# This replaces the complex inline deployment script

set -e

echo "🍓 Starting simple Raspberry Pi deployment..."

# Navigate to app directory
cd $HOME/ozark-finances || exit 1

# Stop existing containers (ignore errors)
echo "🛑 Stopping existing containers..."
docker compose down --remove-orphans 2>/dev/null || true

# Remove any existing containers to force fresh start
echo "🗑️ Removing existing containers and images..."
docker container prune -f || true
docker rmi fastasfack/ozark-finances:latest 2>/dev/null || echo "No existing image to remove"

# Force pull latest image (no cache)
echo "📥 Force pulling latest image..."
docker pull fastasfack/ozark-finances:latest || echo "⚠️ Direct pull failed, trying compose pull"
docker compose pull --ignore-pull-failures || echo "⚠️ Pull completed with some warnings"

# Start containers with fresh build
echo "🚀 Starting containers..."
docker compose up -d --force-recreate --remove-orphans

# Wait for container to be ready
echo "⏳ Waiting for container to start..."
sleep 15

# Run database fix if script exists
if [ -f "manual_db_fix.sh" ]; then
    echo "🗄️ Running database initialization..."
    chmod +x manual_db_fix.sh
    ./manual_db_fix.sh || echo "⚠️ Database script completed (warnings are normal)"
fi

# Simple health check
echo "🔍 Testing application health..."
for i in {1..10}; do
    if curl -f http://localhost:4999/health >/dev/null 2>&1; then
        echo "✅ Application is healthy!"
        exit 0
    fi
    echo "⏳ Attempt $i/10 - waiting for health check..."
    sleep 3
done

echo "❌ Health check failed after 10 attempts"
echo "📋 Container status:"
docker compose ps
echo "📋 Recent logs:"
docker compose logs --tail=20 ozark-finances
exit 1
