# SmartReader - Raspberry Pi Setup Guide

## 🎯 Complete Setup Guide for Raspberry Pi 3B

This guide will walk you through setting up SmartReader on your Raspberry Pi from scratch.

---

## 📋 Prerequisites

### Hardware Required
- ✅ Raspberry Pi 3B (or newer)
- ✅ MicroSD card (16GB minimum, 32GB recommended)
- ✅ Power supply (5V 2.5A)
- ✅ Logitech C270 webcam
- ✅ Speaker (USB or 3.5mm jack)
- ✅ Optional: LED ring light for camera

### What You'll Need
- Computer with SD card reader
- WiFi network
- Mobile phone (iOS or Android)

---

## 🚀 Step-by-Step Setup

### Step 1: Install Raspberry Pi OS

**1.1 Download Raspberry Pi Imager**
- Go to: https://www.raspberrypi.com/software/
- Download for Windows/Mac/Linux
- Install the imager

**1.2 Flash the OS**
1. Insert SD card into computer
2. Open Raspberry Pi Imager
3. Choose OS: **Raspberry Pi OS (64-bit)** recommended
4. Choose Storage: Your SD card
5. Click ⚙️ (Settings) and configure:
   - ✅ Enable SSH
   - ✅ Set username: `pi`
   - ✅ Set password: (your choice)
   - ✅ Configure WiFi (your network name and password)
   - ✅ Set hostname: `smartreader`
6. Click **Write** and wait

**1.3 Boot the Pi**
1. Insert SD card into Raspberry Pi
2. Connect camera, speaker, power
3. Wait 2-3 minutes for first boot

---

### Step 2: Connect to Raspberry Pi

**Option A: SSH (Recommended)**

```bash
# From your computer
ssh pi@smartreader.local
# Or if that doesn't work:
ssh pi@<IP_ADDRESS>

# Enter password when prompted
```

**Option B: Direct Connection**
- Connect monitor, keyboard, mouse to Pi
- Login with username and password

**Find Pi IP Address:**
```bash
hostname -I
# Example output: 192.168.1.100
```

---

### Step 3: Update System

```bash
# Update package lists
sudo apt-get update

# Upgrade installed packages
sudo apt-get upgrade -y

# This may take 10-15 minutes
```

---

### Step 4: Install Python Dependencies

**4.1 Install Python 3 and pip**
```bash
# Check Python version (should be 3.9+)
python3 --version

# Install pip
sudo apt-get install python3-pip -y

# Install virtual environment
sudo apt-get install python3-venv -y
```

**4.2 Install System Dependencies**
```bash
# Install OpenCV dependencies
sudo apt-get install -y \
    libopencv-dev \
    python3-opencv \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test

# Install Tesseract OCR
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-ara \
    tesseract-ocr-fra \
    tesseract-ocr-eng

# Install audio dependencies
sudo apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    portaudio19-dev

# Install camera tools
sudo apt-get install -y \
    v4l-utils

# Install mDNS for smartreader.local
sudo apt-get install -y \
    avahi-daemon \
    avahi-utils
```

---

### Step 5: Transfer SmartReader Code to Pi

**Option A: Using Git (Recommended)**

```bash
# Install git
sudo apt-get install git -y

# Clone your repository
cd ~
git clone <YOUR_REPO_URL> SmartReader
cd SmartReader/pi-server
```

**Option B: Using SCP (from your computer)**

```bash
# From your computer (in SmartReader directory)
scp -r pi-server pi@smartreader.local:~/SmartReader/

# Then SSH into Pi
ssh pi@smartreader.local
cd ~/SmartReader/pi-server
```

**Option C: Manual Transfer**
1. Copy `pi-server` folder to USB drive
2. Insert USB into Pi
3. Copy to home directory:
```bash
cp -r /media/pi/USB/pi-server ~/SmartReader/
cd ~/SmartReader/pi-server
```

---

### Step 6: Setup Python Virtual Environment

```bash
# Navigate to pi-server directory
cd ~/SmartReader/pi-server

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt
```

---

### Step 7: Install Python Packages

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# This may take 15-30 minutes on Pi 3B
# Be patient! Some packages compile from source
```

**If you get errors:**
```bash
# For numpy/opencv errors:
pip install numpy==1.24.3
pip install opencv-python==4.8.1.78

# For TTS errors:
pip install TTS --no-deps
pip install -r requirements.txt
```

---

### Step 8: Configure Camera

**8.1 Enable Camera**
```bash
# Check if camera is detected
v4l2-ctl --list-devices

# Should show Logitech C270
```

**8.2 Test Camera**
```bash
# Install fswebcam for testing
sudo apt-get install fswebcam -y

# Take test photo
fswebcam test.jpg

# Check if test.jpg was created
ls -lh test.jpg
```

**8.3 Set Camera Permissions**
```bash
# Add user to video group
sudo usermod -a -G video pi

# Logout and login again for changes to take effect
exit
ssh pi@smartreader.local
```

---

### Step 9: Configure Audio

**9.1 Test Speaker**
```bash
# List audio devices
aplay -l

# Test audio output
speaker-test -t wav -c 2

# Press Ctrl+C to stop
```

**9.2 Set Default Audio Device**
```bash
# Edit ALSA config
sudo nano /etc/asound.conf

# Add (adjust card number based on aplay -l):
defaults.pcm.card 1
defaults.ctl.card 1

# Save: Ctrl+X, Y, Enter
```

---

### Step 10: Test Tesseract OCR

```bash
# Test Tesseract
tesseract --version

# Should show version 4.x or 5.x

# Test with sample image
tesseract test.jpg output -l eng

# Check output
cat output.txt
```

---

### Step 11: Start SmartReader Server

**11.1 First Run**
```bash
# Navigate to pi-server
cd ~/SmartReader/pi-server

# Activate virtual environment
source venv/bin/activate

# Start server
python -m src.app
```

**You should see:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.100:5000
```

**11.2 Test Server**

Open another terminal (or from your computer):
```bash
# Test health endpoint
curl http://smartreader.local:5000/api/health

# Should return:
# {"status":"ok","timestamp":"..."}
```

---

### Step 12: Configure Autostart (Optional)

**12.1 Create Systemd Service**
```bash
sudo nano /etc/systemd/system/smartreader.service
```

**Add this content:**
```ini
[Unit]
Description=SmartReader Pi Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/SmartReader/pi-server
Environment="PATH=/home/pi/SmartReader/pi-server/venv/bin"
ExecStart=/home/pi/SmartReader/pi-server/venv/bin/python -m src.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**12.2 Enable Service**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable smartreader

# Start service
sudo systemctl start smartreader

# Check status
sudo systemctl status smartreader
```

**12.3 Service Commands**
```bash
# Start
sudo systemctl start smartreader

# Stop
sudo systemctl stop smartreader

# Restart
sudo systemctl restart smartreader

# View logs
sudo journalctl -u smartreader -f
```

---

### Step 13: Configure Firewall (Optional)

```bash
# Install UFW
sudo apt-get install ufw -y

# Allow SSH
sudo ufw allow 22/tcp

# Allow SmartReader
sudo ufw allow 5000/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

### Step 14: Setup Static IP (Recommended)

```bash
# Edit DHCP config
sudo nano /etc/dhcpcd.conf

# Add at the end (adjust to your network):
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8

# Save and reboot
sudo reboot
```

---

## 📱 Connect Mobile App

### Step 1: Configure Mobile App

1. Open SmartReader app on phone
2. Go to **Settings** tab
3. Tap **"📡 Pi Connection Settings"**
4. Enter Pi IP: `192.168.1.100` (or `smartreader.local`)
5. Port: `5000`
6. Tap **"Save & Connect"**

### Step 2: Verify Connection

1. Go to **Home** tab
2. Check status badge
3. Should show **"Connected"** in green ✅

### Step 3: Test Scanning

1. Tap **SCAN** button
2. Wait for scan to complete
3. Text should appear below button
4. Check history for saved scan

---

## 🔧 Troubleshooting

### Problem: Can't SSH to Pi

**Solution:**
```bash
# Find Pi on network
sudo nmap -sn 192.168.1.0/24

# Or use router admin panel to find IP
# Then SSH with IP instead of hostname
ssh pi@192.168.1.100
```

### Problem: Camera Not Working

**Solution:**
```bash
# Check camera connection
lsusb | grep Logitech

# Check video devices
ls -l /dev/video*

# Test camera
fswebcam -r 1280x720 test.jpg

# Check permissions
groups pi
# Should include 'video'
```

### Problem: Tesseract Not Found

**Solution:**
```bash
# Reinstall Tesseract
sudo apt-get install --reinstall tesseract-ocr

# Install language packs
sudo apt-get install tesseract-ocr-ara tesseract-ocr-fra tesseract-ocr-eng

# Verify installation
tesseract --list-langs
```

### Problem: Python Packages Won't Install

**Solution:**
```bash
# Increase swap space (for Pi 3B)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change CONF_SWAPSIZE=100 to CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Try installing again
pip install -r requirements.txt
```

### Problem: Server Won't Start

**Solution:**
```bash
# Check Python version
python3 --version
# Should be 3.9+

# Check if port is in use
sudo netstat -tulpn | grep 5000

# Check logs
python -m src.app
# Look for error messages

# Try running with debug
export FLASK_DEBUG=1
python -m src.app
```

### Problem: Mobile App Can't Connect

**Solution:**
```bash
# Check server is running
curl http://localhost:5000/api/health

# Check firewall
sudo ufw status
sudo ufw allow 5000/tcp

# Check both devices on same WiFi
iwgetid -r

# Ping from phone to Pi
# Use network utility app
```

---

## 📊 Performance Optimization

### For Raspberry Pi 3B

**1. Reduce Camera Resolution**
Edit `src/services/capture_service.py`:
```python
# Change from 1280x720 to 640x480
self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

**2. Use Tesseract Only (Disable Cloud)**
- In mobile app settings, select "Tesseract (Offline)"
- Faster and no internet required

**3. Optimize Python**
```bash
# Use PyPy for faster execution (optional)
sudo apt-get install pypy3 pypy3-dev
```

---

## 🔐 Security Recommendations

### For Production Use

**1. Change Default Password**
```bash
passwd
```

**2. Disable Password SSH (Use Keys)**
```bash
# Generate SSH key on your computer
ssh-keygen -t rsa

# Copy to Pi
ssh-copy-id pi@smartreader.local

# Disable password auth
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart ssh
```

**3. Keep System Updated**
```bash
# Create update script
nano ~/update.sh

# Add:
#!/bin/bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get autoremove -y

# Make executable
chmod +x ~/update.sh

# Run weekly
sudo crontab -e
# Add: 0 2 * * 0 /home/pi/update.sh
```

---

## 📝 Maintenance

### Regular Tasks

**Weekly:**
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Check disk space
df -h

# Check logs
sudo journalctl -u smartreader --since "1 week ago"
```

**Monthly:**
```bash
# Clean old logs
sudo journalctl --vacuum-time=30d

# Clean package cache
sudo apt-get clean
sudo apt-get autoremove -y
```

**Backup:**
```bash
# Backup SmartReader data
cd ~/SmartReader/pi-server
tar -czf backup-$(date +%Y%m%d).tar.gz data/ audio/

# Copy to computer
scp backup-*.tar.gz user@computer:~/backups/
```

---

## ✅ Verification Checklist

Before using SmartReader, verify:

- [ ] Pi boots successfully
- [ ] Can SSH to Pi
- [ ] Camera detected (`lsusb`)
- [ ] Speaker works (`speaker-test`)
- [ ] Tesseract installed (`tesseract --version`)
- [ ] Python packages installed (`pip list`)
- [ ] Server starts without errors
- [ ] Health endpoint responds (`curl`)
- [ ] Mobile app connects
- [ ] Can trigger scan
- [ ] Text extracted successfully
- [ ] Audio generated
- [ ] History saved

---

## 🎉 Success!

If all steps completed successfully:

✅ Raspberry Pi is configured
✅ SmartReader server is running
✅ Mobile app can connect
✅ System is ready to use!

**Next Steps:**
1. Test scanning with real documents
2. Adjust settings for your needs
3. Try voice commands
4. Enjoy hands-free document reading!

---

## 📞 Getting Help

**Check Logs:**
```bash
# Server logs
sudo journalctl -u smartreader -f

# System logs
dmesg | tail -50
```

**Common Log Locations:**
- Server: `sudo journalctl -u smartreader`
- System: `/var/log/syslog`
- Camera: `dmesg | grep video`

**Documentation:**
- `QUICK_START.md` - Quick start guide
- `CONNECTION_SETUP.md` - Connection help
- `PI_CONNECTION_GUIDE.md` - Detailed connection guide
- `IMPLEMENTATION_SUMMARY.md` - System overview

---

## 🚀 Quick Reference

```bash
# Start server manually
cd ~/SmartReader/pi-server
source venv/bin/activate
python -m src.app

# Start as service
sudo systemctl start smartreader

# Check status
sudo systemctl status smartreader

# View logs
sudo journalctl -u smartreader -f

# Restart
sudo systemctl restart smartreader

# Stop
sudo systemctl stop smartreader

# Find IP
hostname -I

# Test health
curl http://localhost:5000/api/health
```

Happy SmartReading! 📖🎤🚀
