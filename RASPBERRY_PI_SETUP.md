# 🍓 Raspberry Pi Setup Guide for Ozark Finances

Complete setup guide for deploying Ozark Finances to Raspberry Pi 3B+ using Docker and automated GitHub Actions deployment.

## 📋 **Prerequisites**

### **Hardware Requirements**
- Raspberry Pi 3B+ or newer
- MicroSD card (32GB+ recommended)
- Stable internet connection
- Power supply (5V/2.5A minimum)

### **Software Requirements**
- Raspberry Pi OS (64-bit recommended)
- Docker and Docker Compose
- Git
- SSH enabled

## 🔧 **Phase 1: Raspberry Pi Initial Setup**

### **1.1 Install Raspberry Pi OS**
```bash
# Download Raspberry Pi Imager
# Flash Raspberry Pi OS (64-bit) to SD card
# Enable SSH during imaging process
```

### **1.2 First Boot Configuration**
```bash
# SSH into your Pi
ssh pi@YOUR_PI_IP

# Update system
sudo apt update && sudo apt upgrade -y

# Configure timezone
sudo timedatectl set-timezone Europe/Amsterdam

# Enable SSH permanently
sudo systemctl enable ssh
```

### **1.3 Create Application User**
```bash
# Create dedicated user for the application
sudo useradd -m -s /bin/bash ozark
sudo usermod -aG docker ozark
sudo usermod -aG sudo ozark

# Set password
sudo passwd ozark
```

## 🐳 **Phase 2: Docker Installation**

### **2.1 Install Docker**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
sudo usermod -aG docker ozark

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### **2.2 Install Docker Compose**
```bash
# Install Docker Compose
sudo apt install docker-compose -y

# Verify installation
docker --version
docker-compose --version
```

### **2.3 Configure Docker for ARM**
```bash
# Enable experimental features for multi-arch support
sudo mkdir -p /etc/docker
echo '{
  "experimental": true,
  "storage-driver": "overlay2"
}' | sudo tee /etc/docker/daemon.json

# Restart Docker
sudo systemctl restart docker
```

## 🔑 **Phase 3: SSH Key Setup for GitHub Actions**

### **3.1 Generate SSH Key Pair**
```bash
# Switch to ozark user
sudo su - ozark

# Generate SSH key pair
ssh-keygen -t ed25519 -C "ozark-finances-deploy" -f ~/.ssh/ozark_deploy

# Display public key (add to Pi's authorized_keys)
cat ~/.ssh/ozark_deploy.pub >> ~/.ssh/authorized_keys

# Display private key (copy to GitHub Secrets)
cat ~/.ssh/ozark_deploy

# Set proper permissions
chmod 600 ~/.ssh/ozark_deploy
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### **3.2 Test SSH Connection**
```bash
# From your development machine, test SSH connection
ssh -i path/to/private/key ozark@YOUR_PI_IP
```

## 📁 **Phase 4: Directory Structure Setup**

### **4.1 Create Application Directories**
```bash
# Create application directories
sudo mkdir -p /opt/ozark-finances/{data,uploads,generated,logs,backups}

# Set ownership
sudo chown -R ozark:ozark /opt/ozark-finances

# Set permissions
chmod 755 /opt/ozark-finances
chmod 755 /opt/ozark-finances/{data,uploads,generated,logs,backups}
```

### **4.2 Create Docker Compose Override (Optional)**
```bash
# Switch to application directory
cd /opt/ozark-finances

# Create local override for development
cat > docker-compose.override.yml << 'EOF'
version: '3.8'

services:
  ozark-finances:
    # Override for local development
    environment:
      - FLASK_DEBUG=0
      - LOG_LEVEL=INFO
    
    # Expose additional debugging port if needed
    # ports:
    #   - "5001:5000"

EOF
```

## 🔐 **Phase 5: GitHub Secrets Configuration**

Add these secrets to your GitHub repository (`Settings > Secrets and variables > Actions`):

### **5.1 Required Secrets**
```
RASPBERRY_PI_HOST=your.pi.ip.address
RASPBERRY_PI_USER=ozark
RASPBERRY_PI_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
[paste the entire private key content here]
-----END OPENSSH PRIVATE KEY-----
```

### **5.2 Optional Secrets**
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/... (for notifications)
DISCORD_WEBHOOK_URL=https://discord.com/... (for notifications)
```

## 🚀 **Phase 6: Initial Deployment Test**

### **6.1 Manual Deployment Test**
```bash
# Switch to ozark user
sudo su - ozark

# Navigate to application directory
cd /opt/ozark-finances

# Clone repository (first time only)
git clone https://github.com/FastAsFack/OzarkFinances.git .

# Test Docker build locally
docker build -t ozark-finances-test .

# Run health check
docker run --rm -p 5000:5000 ozark-finances-test &
sleep 10
curl http://localhost:5000/health

# Stop test container
docker stop $(docker ps -q --filter ancestor=ozark-finances-test)
```

### **6.2 Test GitHub Actions Deployment**
```bash
# Make a small change to README.md and push
# Watch GitHub Actions tab for deployment progress
# Verify deployment at http://YOUR_PI_IP:5000
```

## 📊 **Phase 7: Monitoring and Maintenance**

### **7.1 Container Monitoring**
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f

# Check resource usage
docker stats

# Monitor Pi resources
htop
```

### **7.2 Backup Strategy**
```bash
# Create backup script
cat > /opt/ozark-finances/backup.sh << 'EOF'
#!/bin/bash
timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="/opt/ozark-finances/backups/manual_$timestamp"
mkdir -p "$backup_dir"

# Backup databases
cp -r /opt/ozark-finances/data/*.db "$backup_dir/" 2>/dev/null || true

# Create archive
tar -czf "$backup_dir.tar.gz" -C /opt/ozark-finances/backups "manual_$timestamp"
rm -rf "$backup_dir"

echo "Backup created: $backup_dir.tar.gz"
EOF

chmod +x /opt/ozark-finances/backup.sh
```

### **7.3 Automatic Cleanup**
```bash
# Add to crontab for weekly cleanup
crontab -e

# Add this line for weekly cleanup at 3 AM Sunday
0 3 * * 0 docker system prune -f && docker image prune -f
```

## 🔧 **Phase 8: Firewall and Security**

### **8.1 Configure UFW Firewall**
```bash
# Install and configure firewall
sudo apt install ufw -y

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow ssh

# Allow application port
sudo ufw allow 5000/tcp

# Enable firewall
sudo ufw enable
```

### **8.2 Security Hardening**
```bash
# Disable password authentication for SSH (optional)
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Update packages automatically
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 🌐 **Phase 9: Network Configuration**

### **9.1 Static IP Configuration**
```bash
# Edit network configuration
sudo nano /etc/dhcpcd.conf

# Add static IP configuration
echo "
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8 8.8.4.4
" | sudo tee -a /etc/dhcpcd.conf

# Restart networking
sudo systemctl restart dhcpcd
```

### **9.2 Port Forwarding (Router Configuration)**
```
Router Settings:
- External Port: 5000
- Internal IP: 192.168.1.100
- Internal Port: 5000
- Protocol: TCP
```

## ✅ **Phase 10: Verification Checklist**

### **Deployment Verification**
- [ ] Docker and Docker Compose installed
- [ ] SSH keys configured
- [ ] GitHub secrets added
- [ ] Application directories created
- [ ] Firewall configured
- [ ] Static IP assigned
- [ ] GitHub Actions deployment successful
- [ ] Application accessible at http://PI_IP:5000
- [ ] Health check endpoint responding
- [ ] Database persistence working
- [ ] Backups being created

### **Post-Deployment Tests**
```bash
# Test application health
curl http://YOUR_PI_IP:5000/health

# Test database functionality
curl http://YOUR_PI_IP:5000/

# Check container status
docker-compose ps

# Verify volumes
docker volume ls

# Check logs
docker-compose logs
```

## 🆘 **Troubleshooting**

### **Common Issues**

**Container won't start:**
```bash
# Check logs
docker-compose logs ozark-finances

# Check resources
free -h
df -h

# Restart Docker
sudo systemctl restart docker
```

**Database errors:**
```bash
# Check permissions
ls -la /opt/ozark-finances/data/

# Fix permissions
sudo chown -R ozark:ozark /opt/ozark-finances/
```

**Network issues:**
```bash
# Check firewall
sudo ufw status

# Check port binding
netstat -tlnp | grep 5000

# Test internal connectivity
curl http://localhost:5000/health
```

**GitHub Actions deployment fails:**
```bash
# Check SSH connection
ssh ozark@YOUR_PI_IP "docker ps"

# Verify secrets
# Check GitHub Actions logs
# Verify Pi connectivity
```

## 📞 **Support**

If you encounter issues:
1. Check the GitHub Actions logs
2. Review Pi system logs: `journalctl -xe`
3. Check Docker logs: `docker-compose logs`
4. Verify network connectivity
5. Check disk space: `df -h`

---

**🎉 Congratulations! Your Ozark Finances application is now running on Raspberry Pi with automated deployments!**
