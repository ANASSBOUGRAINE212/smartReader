# Camera Preview Window Guide

## Overview

The Pi server now supports opening a native camera preview window directly on the Raspberry Pi display. This allows you to see what the camera sees in real-time.

## Features

- **Native GUI Window**: Opens using OpenCV (not HTML)
- **Live Preview**: Real-time camera feed
- **Overlay Information**: Shows status and instructions
- **Auto-close**: Press ESC or close window to stop
- **Thread-safe**: Runs in background without blocking server

## Requirements

Make sure OpenCV is installed on your Pi:

```bash
pip install opencv-python
# or
pip install opencv-contrib-python
```

For GUI support on Raspberry Pi OS Lite, you may need:

```bash
sudo apt-get install python3-opencv
```

## Usage

### Option 1: Test Script

Run the standalone test script:

```bash
cd ~/SmartReader/pi-server
python3 test_camera_preview.py
```

Press Ctrl+C to stop.

### Option 2: API Endpoints

Control the preview from the mobile app or curl:

**Start Preview:**
```bash
curl -X POST http://eldercare-pi.local:5000/api/camera/preview/start
```

**Stop Preview:**
```bash
curl -X POST http://eldercare-pi.local:5000/api/camera/preview/stop
```

**Check Status:**
```bash
curl http://eldercare-pi.local:5000/api/camera/preview/status
```

### Option 3: Integrate with Mobile App

Add a button in the mobile app to toggle the camera preview:

```typescript
const togglePreview = async () => {
  const api = getApiService();
  if (previewRunning) {
    await api.post('/camera/preview/stop');
  } else {
    await api.post('/camera/preview/start');
  }
};
```

## Window Controls

- **ESC key**: Close preview window
- **X button**: Close preview window
- **Window resize**: Drag corners to resize

## Camera Settings

The preview uses these camera settings:
- Resolution: 1280x720
- Window size: 800x600 (resizable)
- Frame rate: ~30 FPS

## Troubleshooting

### "Failed to open camera"

Check if camera is enabled:
```bash
vcgencmd get_camera
```

Should show: `supported=1 detected=1`

Enable camera:
```bash
sudo raspi-config
# Interface Options → Camera → Enable
```

### "No display found"

If running headless (no monitor), the preview won't work. You need:
- Physical monitor connected to Pi, OR
- VNC with X11 forwarding, OR
- Use the HTML preview instead

### "ImportError: libGL.so.1"

Install OpenGL libraries:
```bash
sudo apt-get install libgl1-mesa-glx
```

### Preview window is black

- Check camera connection
- Restart the Pi
- Try: `raspistill -o test.jpg` to verify camera works

## Integration with Scanning

The preview can run continuously while scanning:

1. Start preview when app launches
2. Keep it running in background
3. When user scans, the same camera is used
4. Preview continues after scan completes

## Performance

- CPU usage: ~5-10% on Pi 4
- Memory: ~50MB
- No impact on scanning performance
- Runs in separate thread

## Auto-start on Boot

To start preview automatically when Pi boots:

1. Create systemd service:
```bash
sudo nano /etc/systemd/system/smartreader-preview.service
```

2. Add:
```ini
[Unit]
Description=SmartReader Camera Preview
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/SmartReader/pi-server
ExecStart=/usr/bin/python3 test_camera_preview.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Enable:
```bash
sudo systemctl enable smartreader-preview
sudo systemctl start smartreader-preview
```

## Next Steps

- Add preview toggle button in mobile app Settings
- Add zoom/focus controls
- Add snapshot button to save current frame
- Add grid overlay for alignment
