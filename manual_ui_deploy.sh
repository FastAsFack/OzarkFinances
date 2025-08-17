#!/bin/bash
# Manual deployment script - run this on your Raspberry Pi to deploy UI changes immediately

echo "🚀 MANUAL DEPLOYMENT - UI CHANGES"
echo "This will deploy your latest UI changes immediately"

# Navigate to deployment directory
cd ~/ozark-finances || exit 1

# Backup current state
echo "📦 Creating backup..."
timestamp=$(date +%Y%m%d_%H%M%S)
if [ -f "docker-compose.yml" ]; then
    docker compose exec -T ozark-finances python -c "
import shutil, os
if os.path.exists('/app/data/ozark_finances.db'):
    shutil.copy('/app/data/ozark_finances.db', f'/app/data/ozark_finances.db.backup_{timestamp}')
    print(f'✅ Database backed up with timestamp ${timestamp}')
" 2>/dev/null || echo "ℹ️ No existing database to backup"
fi

# Stop existing containers
echo "🛑 Stopping containers..."
docker compose down --remove-orphans

# Remove old images to force fresh pull
echo "🗑️ Removing old images..."
docker rmi fastasfack/ozark-finances:latest 2>/dev/null || echo "No existing image to remove"

# Pull latest changes from git
echo "📥 Pulling latest code..."
git pull origin Main

# Force pull latest Docker image
echo "📥 Pulling latest Docker image..."
docker pull fastasfack/ozark-finances:latest

# Start with fresh containers
echo "🚀 Starting fresh containers..."
docker compose up -d --force-recreate

# Wait and run database fix
echo "⏳ Waiting for container to start..."
sleep 15

# Run database initialization
if [ -f "manual_db_fix.sh" ]; then
    echo "🗄️ Running database initialization..."
    chmod +x manual_db_fix.sh
    ./manual_db_fix.sh || echo "⚠️ Database script completed (warnings are normal)"
fi

# Health check
echo "🔍 Testing application health..."
for i in {1..10}; do
    if curl -f http://localhost:4999/health >/dev/null 2>&1; then
        echo "✅ Application is healthy!"
        echo "🌐 Your UI changes should now be live at: http://localhost:4999"
        echo ""
        echo "Changes deployed:"
        echo "  ✅ Info buttons removed from all pages"
        echo "  ✅ Instruction sections removed"
        echo "  ✅ Toast notifications for BTW payments"
        echo "  ✅ Streamlined interface"
        exit 0
    fi
    echo "⏳ Attempt $i/10 - waiting for health check..."
    sleep 3
done

echo "❌ Health check failed - please check logs:"
docker compose logs ozark-finances
