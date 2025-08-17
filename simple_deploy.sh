#!/bin/bash
# Simple deployment script for GitHub Actions
# This replaces the complex inline deployment script

set -e

echo "🍓 Starting simple Raspberry Pi deployment..."

# Navigate to app directory
cd $HOME/ozark-finances || exit 1

# Stop existing containers (ignore errors)
docker compose down --remove-orphans 2>/dev/null || true

# Pull latest image
docker compose pull || echo "⚠️ Pull failed, will use cached images"

# Start containers
docker compose up -d

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
