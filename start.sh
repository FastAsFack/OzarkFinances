#!/bin/bash
# Startup script for Ozark Finances Docker container
# Ensures database initialization before starting the Flask app

set -e  # Exit on any error

echo "🚀 Starting Ozark Finances application..."

# Wait a moment for volumes to be properly mounted
sleep 2

# Ensure data directory exists and is writable
echo "📁 Ensuring data directory is ready..."
mkdir -p /app/data
chmod 755 /app/data

# Run database initialization
echo "🗄️ Initializing database..."
python docker_init.py

# Check if initialization was successful
if [ $? -eq 0 ]; then
    echo "✅ Database initialization completed successfully"
else
    echo "❌ Database initialization failed!"
    exit 1
fi

# Verify database file exists
if [ -f "/app/data/ozark_finances.db" ]; then
    echo "✅ Database file confirmed at /app/data/ozark_finances.db"
    ls -la /app/data/ozark_finances.db
else
    echo "❌ Database file not found after initialization!"
    ls -la /app/data/
    exit 1
fi

# Start the Flask application
echo "🌐 Starting Flask application..."
exec python app.py
