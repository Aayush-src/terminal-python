#!/bin/bash
# Quick setup script for Ubuntu EC2 deployment
# This script prepares the system and runs the main deployment

echo "🔧 Preparing Ubuntu system for Python Terminal deployment..."

# Make sure we're on Ubuntu
if ! grep -q "Ubuntu" /etc/os-release; then
    echo "❌ This script is designed for Ubuntu. Please use the appropriate script for your OS."
    exit 1
fi

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root. Use a regular user with sudo privileges."
    exit 1
fi

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "📦 Installing git..."
    sudo apt update && sudo apt install git -y
fi

# Download and run the main deployment script
echo "📥 Downloading deployment script..."
curl -o deploy_ec2.sh https://raw.githubusercontent.com/Aayush-src/terminal-python/main/deploy_ec2.sh

# Make it executable
chmod +x deploy_ec2.sh

# Run the deployment
echo "🚀 Starting deployment..."
./deploy_ec2.sh

echo "✅ Setup complete!"
