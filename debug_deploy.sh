#!/bin/bash
# Simple UI deployment script - step by step debugging

echo "🔧 SIMPLE UI DEPLOYMENT DEBUG"
echo "Running as user: $(whoami)"
echo "Current directory: $(pwd)"
echo "Date: $(date)"
echo ""

# Step 1: Navigate to deployment directory
echo "📁 Step 1: Checking deployment directory..."
if [ -d "$HOME/ozark-finances" ]; then
    echo "✅ Found $HOME/ozark-finances"
    cd "$HOME/ozark-finances"
    echo "✅ Changed to: $(pwd)"
else
    echo "❌ Directory $HOME/ozark-finances not found"
    echo "Looking for alternatives..."
    if [ -d "./ozark-finances" ]; then
        echo "✅ Found ./ozark-finances"
        cd "./ozark-finances"
    elif [ -d "../ozark-finances" ]; then
        echo "✅ Found ../ozark-finances"
        cd "../ozark-finances"
    else
        echo "❌ Cannot find ozark-finances directory"
        echo "Please run: git clone https://github.com/FastAsFack/OzarkFinances.git ozark-finances"
        exit 1
    fi
fi

# Step 2: Check if docker-compose.yml exists
echo ""
echo "🐳 Step 2: Checking Docker setup..."
if [ -f "docker-compose.yml" ]; then
    echo "✅ Found docker-compose.yml"
else
    echo "❌ docker-compose.yml not found"
    echo "Current directory contents:"
    ls -la
    exit 1
fi

# Step 3: Check Docker status
echo ""
echo "🔍 Step 3: Checking Docker status..."
if docker --version > /dev/null 2>&1; then
    echo "✅ Docker is available"
    echo "Docker version: $(docker --version)"
else
    echo "❌ Docker not available"
    exit 1
fi

if docker compose version > /dev/null 2>&1; then
    echo "✅ Docker Compose is available"
else
    echo "❌ Docker Compose not available"
    exit 1
fi

# Step 4: Check current containers
echo ""
echo "📋 Step 4: Current container status..."
docker compose ps || echo "No containers running or compose file issue"

# Step 5: Pull latest code
echo ""
echo "📥 Step 5: Pulling latest code..."
git status
git pull origin Main || echo "Git pull failed - continuing anyway"

# Step 6: Simple container restart
echo ""
echo "🔄 Step 6: Restarting containers..."
echo "Stopping containers..."
docker compose down || echo "Stop failed - continuing"

echo "Starting containers..."
docker compose up -d || echo "Start failed"

# Step 7: Wait and check
echo ""
echo "⏳ Step 7: Waiting for startup..."
sleep 10

echo "Container status:"
docker compose ps

echo "Testing health:"
curl -f http://localhost:4999/health && echo " ✅ Health check passed" || echo " ❌ Health check failed"

echo ""
echo "🎯 Manual deployment attempt completed!"
echo "If this worked, your UI changes should be visible at: http://localhost:4999"
