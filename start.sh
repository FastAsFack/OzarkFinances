#!/bin/bash
# Startup script for Ozark Finances Docker container
# Ensures database initialization before starting the Flask app

echo "🚀 Starting Ozark Finances application..."

# Run database initialization
echo "🗄️ Initializing database..."
python docker_init.py

# Check if initialization was successful
if [ $? -eq 0 ]; then
    echo "✅ Database initialization completed successfully"
else
    echo "❌ Database initialization failed, but continuing..."
fi

# Start the Flask application
echo "🌐 Starting Flask application..."
exec python app.py
