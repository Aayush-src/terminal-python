# 🚀 Ubuntu EC2 Deployment Guide

This guide will help you deploy the Python Terminal on an Ubuntu EC2 instance.

## 📋 Prerequisites

- AWS EC2 instance running Ubuntu 20.04+ or 22.04+
- Security group configured to allow:
  - SSH (port 22)
  - HTTP (port 8501)
- SSH access to your EC2 instance

## 🎯 Quick Deployment

### Option 1: One-Command Setup
```bash
# Connect to your EC2 instance via SSH
ssh -i your-key.pem ubuntu@your-ec2-ip

# Run the setup script
curl -sSL https://raw.githubusercontent.com/Aayush-src/terminal-python/main/setup_ubuntu.sh | bash
```

### Option 2: Manual Setup
```bash
# Connect to your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Clone the repository
git clone https://github.com/Aayush-src/terminal-python.git
cd terminal-python

# Make deployment script executable
chmod +x deploy_ec2.sh

# Run deployment
./deploy_ec2.sh
```

## 🔧 What the Script Does

1. **Updates system packages** using `apt`
2. **Installs Python 3, pip, and dependencies**
3. **Clones your GitHub repository**
4. **Creates a virtual environment**
5. **Installs Python dependencies** from `requirements.txt`
6. **Creates a systemd service** for auto-start
7. **Starts the application** on port 8501

## 🌐 Accessing Your Terminal

After deployment, your terminal will be available at:
```
http://your-ec2-public-ip:8501
```

## 🛠️ Management Commands

```bash
# Check service status
sudo systemctl status terminal-app

# View logs
sudo journalctl -u terminal-app -f

# Restart the application
sudo systemctl restart terminal-app

# Stop the application
sudo systemctl stop terminal-app

# Update code and restart
cd /home/ubuntu/terminal-app
git pull
sudo systemctl restart terminal-app
```

## 🔒 Security Features

The deployed terminal includes Ubuntu system protection:
- ✅ Prevents deletion of critical system files
- ✅ Blocks access to system directories (`/bin`, `/etc`, `/boot`, etc.)
- ✅ Protects kernel files, configuration files, and system binaries
- ✅ Allows safe operations in user directories

## 📁 File Structure

```
/home/ubuntu/terminal-app/
├── app_simple.py          # Main Streamlit application
├── terminal_backend.py    # Command executor
├── commands/              # Command implementations
├── nlp/                   # NLP processing
├── utils/                 # Utility functions
├── requirements.txt       # Python dependencies
└── venv/                  # Virtual environment
```

## 🐛 Troubleshooting

### Service won't start
```bash
# Check logs for errors
sudo journalctl -u terminal-app -f

# Check if port 8501 is in use
sudo netstat -tlnp | grep 8501
```

### Permission issues
```bash
# Fix ownership
sudo chown -R ubuntu:ubuntu /home/ubuntu/terminal-app
```

### Update dependencies
```bash
cd /home/ubuntu/terminal-app
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart terminal-app
```

## 🔄 Updating the Application

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Navigate to app directory
cd /home/ubuntu/terminal-app

# Pull latest changes
git pull

# Restart the service
sudo systemctl restart terminal-app
```

## 💰 Cost Optimization

- Use **t3.micro** for free tier (12 months)
- Use **t3.small** for better performance (~$8-15/month)
- Consider **Spot Instances** for development

## 🎉 Success!

Your Python Terminal is now running on Ubuntu EC2 with:
- ✅ Full pip package management
- ✅ Ubuntu system protection
- ✅ Auto-start on boot
- ✅ Easy updates via git
- ✅ Professional logging and monitoring
