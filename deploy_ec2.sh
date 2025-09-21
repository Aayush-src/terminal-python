#!/bin/bash
# EC2 Deployment Script for Python Terminal (Ubuntu)
# Run this script on your EC2 instance

echo "🚀 Setting up Python Terminal on Ubuntu EC2..."

# Update system
echo "📦 Updating system packages..."
sudo apt update -y
sudo apt upgrade -y

# Install Python 3 and pip
echo "🐍 Installing Python 3 and pip..."
sudo apt install python3 python3-pip python3-venv git curl -y

# Install additional system packages that might be needed
echo "🔧 Installing additional packages..."
sudo apt install build-essential python3-dev -y

# Create application directory
echo "📁 Creating application directory..."
mkdir -p /home/ubuntu/terminal-app
cd /home/ubuntu/terminal-app

# Clone repository
echo "📥 Cloning repository from GitHub..."
git clone https://github.com/Aayush-src/terminal-python.git .

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create systemd service for auto-start
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/terminal-app.service > /dev/null <<EOF
[Unit]
Description=Python Terminal Streamlit App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/terminal-app
Environment=PATH=/home/ubuntu/terminal-app/venv/bin:/usr/bin:/usr/local/bin
ExecStart=/home/ubuntu/terminal-app/venv/bin/streamlit run app_simple.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Set proper permissions
echo "🔐 Setting proper permissions..."
sudo chown -R ubuntu:ubuntu /home/ubuntu/terminal-app
chmod +x /home/ubuntu/terminal-app/app_simple.py

# Enable and start the service
echo "🔄 Enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable terminal-app
sudo systemctl start terminal-app

# Wait a moment for service to start
sleep 5

# Check service status
echo "📊 Checking service status..."
sudo systemctl status terminal-app --no-pager

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

echo ""
echo "✅ Deployment complete!"
echo "🌐 Your terminal should be available at: http://$PUBLIC_IP:8501"
echo "📝 To check logs: sudo journalctl -u terminal-app -f"
echo "🔄 To restart: sudo systemctl restart terminal-app"
echo "🛑 To stop: sudo systemctl stop terminal-app"
echo ""
echo "🔧 Useful commands:"
echo "   - View logs: sudo journalctl -u terminal-app -f"
echo "   - Restart app: sudo systemctl restart terminal-app"
echo "   - Check status: sudo systemctl status terminal-app"
echo "   - Update code: cd /home/ubuntu/terminal-app && git pull && sudo systemctl restart terminal-app"