#!/bin/bash
# Runner status check script for Raspberry Pi

echo "🔍 GITHUB ACTIONS RUNNER STATUS CHECK"
echo "Run this on your Raspberry Pi to check runner status"

# Check if runner service is running
echo "📋 Checking GitHub Actions runner service..."
if systemctl is-active --quiet actions.runner.FastAsFack-OzarkFinances.github-runner; then
    echo "✅ GitHub Actions runner service is running"
    systemctl status actions.runner.FastAsFack-OzarkFinances.github-runner --no-pager
else
    echo "❌ GitHub Actions runner service is not running"
    echo "To start it, run:"
    echo "sudo systemctl start actions.runner.FastAsFack-OzarkFinances.github-runner"
    echo "sudo systemctl enable actions.runner.FastAsFack-OzarkFinances.github-runner"
fi

# Check runner directory
echo ""
echo "📁 Checking runner directory..."
if [ -d "/home/ozark/actions-runner" ]; then
    echo "✅ Runner directory exists"
    cd /home/ozark/actions-runner
    if [ -f "./run.sh" ]; then
        echo "✅ Runner script exists"
        
        # Check if runner is running in background
        if pgrep -f "./run.sh" > /dev/null; then
            echo "✅ Runner is currently running in background"
            echo "PID: $(pgrep -f './run.sh')"
        else
            echo "❌ Runner is not currently running"
            echo "To manually start runner:"
            echo "cd /home/ozark/actions-runner && ./run.sh &"
        fi
    fi
else
    echo "❌ Runner directory not found at /home/ozark/actions-runner"
    # Also check if it might be in home directory
    if [ -d "~/actions-runner" ]; then
        echo "✅ Found runner directory in home: ~/actions-runner"
    fi
fi

# Check for background jobs
echo ""
echo "🔄 Checking background jobs..."
if jobs | grep -q "run.sh"; then
    echo "✅ GitHub Actions runner found in background jobs"
else
    echo "ℹ️ No runner background jobs found"
fi

# Check recent workflow runs
echo ""
echo "📊 To check workflows manually:"
echo "Visit: https://github.com/FastAsFack/OzarkFinances/actions"
