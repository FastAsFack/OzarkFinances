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
if [ -d "/home/pi/actions-runner" ]; then
    echo "✅ Runner directory exists"
    cd /home/pi/actions-runner
    if [ -f "./run.sh" ]; then
        echo "✅ Runner script exists"
        echo "To manually start runner:"
        echo "cd /home/pi/actions-runner && ./run.sh"
    fi
else
    echo "❌ Runner directory not found"
fi

# Check recent workflow runs
echo ""
echo "📊 To check workflows manually:"
echo "Visit: https://github.com/FastAsFack/OzarkFinances/actions"
