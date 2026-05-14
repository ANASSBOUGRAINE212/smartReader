# 🚀 SCP Transfer Guide - Update Pi Server

## Files That Need to Be Transferred

Only 2 files were modified for the audio fix:

1. `pi-server/src/routes/api.py` - Added audio serving endpoint
2. `pi-server/src/services/history_service.py` - Updated audio URL format

## Quick Transfer Commands

### Option 1: Transfer Individual Files (Recommended)

```bash
# From your Windows computer (in PowerShell or CMD)
# Navigate to your project directory first
cd C:\Users\dell\Downloads\SmartReader

# Transfer api.py
scp pi-server\src\routes\api.py hibaanasibtissame@192.168.137.123:~/SmartReader/pi-server/src/routes/api.py

# Transfer history_service.py
scp pi-server\src\services\history_service.py hibaanasibtissame@192.168.137.123:~/SmartReader/pi-server/src/services/history_service.py
```

**Replace `192.168.137.123` with your Pi's actual IP address!**

### Option 2: Transfer Entire pi-server Directory

```bash
# From your Windows computer
cd C:\Users\dell\Downloads\SmartReader

# Transfer entire pi-server folder (excluding venv and cache)
scp -r pi-server hibaanasibtissame@192.168.137.123:~/SmartReader/
```

**Note:** This will overwrite the entire pi-server directory on the Pi.

## Step-by-Step Instructions

### Step 1: Find Your Pi's IP Address

```bash
# On Raspberry Pi, run:
hostname -I
```

Example output: `192.168.137.123`

**Write this down!**

### Step 2: Open PowerShell on Windows

1. Press `Win + X`
2. Select "Windows PowerShell" or "Terminal"
3. Navigate to your project:
   ```powershell
   cd C:\Users\dell\Downloads\SmartReader
   ```

### Step 3: Transfer Files

**Method A: Transfer only changed files (faster)**

```powershell
# Replace 192.168.137.123 with your Pi's IP
scp pi-server\src\routes\api.py hibaanasibtissame@192.168.137.123:~/SmartReader/pi-server/src/routes/api.py

scp pi-server\src\services\history_service.py hibaanasibtissame@192.168.137.123:~/SmartReader/pi-server/src/services/history_service.py
```

**Method B: Transfer entire src directory**

```powershell
scp -r pi-server\src hibaanasibtissame@192.168.137.123:~/SmartReader/pi-server/
```

### Step 4: Verify Transfer

```bash
# On Raspberry Pi
cd ~/SmartReader/pi-server

# Check file timestamps (should be recent)
ls -lh src/routes/api.py
ls -lh src/services/history_service.py

# Check file sizes
du -h src/routes/api.py
du -h src/services/history_service.py
```

### Step 5: Restart Server

```bash
# On Raspberry Pi
cd ~/SmartReader/pi-server
source venv/bin/activate
python -m src.app
```

## Troubleshooting SCP

### Error: "Connection refused"

**Cause:** SSH not enabled on Pi or wrong IP

**Fix:**
```bash
# On Raspberry Pi, enable SSH
sudo systemctl start ssh
sudo systemctl enable ssh

# Verify SSH is running
sudo systemctl status ssh
```

### Error: "Permission denied"

**Cause:** Wrong username or password

**Fix:**
- Verify username: `hibaanasibtissame`
- Enter password when prompted
- Or use SSH key authentication

### Error: "No such file or directory"

**Cause:** Directory doesn't exist on Pi

**Fix:**
```bash
# On Raspberry Pi, create directory structure
mkdir -p ~/SmartReader/pi-server/src/routes
mkdir -p ~/SmartReader/pi-server/src/services
```

### Error: "Host key verification failed"

**Cause:** Pi's SSH key changed

**Fix:**
```powershell
# On Windows, remove old key
ssh-keygen -R 192.168.137.123
# Then try SCP again
```

## Alternative: Use WinSCP (GUI Tool)

If you prefer a graphical interface:

### Download WinSCP
1. Go to: https://winscp.net/
2. Download and install WinSCP

### Connect to Pi
1. Open WinSCP
2. Enter:
   - **Host name:** `192.168.137.123` (your Pi's IP)
   - **User name:** `hibaanasibtissame`
   - **Password:** (your Pi password)
3. Click "Login"

### Transfer Files
1. Navigate to `C:\Users\dell\Downloads\SmartReader\pi-server\src\routes\`
2. Drag `api.py` to `/home/hibaanasibtissame/SmartReader/pi-server/src/routes/`
3. Navigate to `C:\Users\dell\Downloads\SmartReader\pi-server\src\services\`
4. Drag `history_service.py` to `/home/hibaanasibtissame/SmartReader/pi-server/src/services/`

## Verify Files Were Updated

### Check File Contents

```bash
# On Raspberry Pi
cd ~/SmartReader/pi-server

# Check if audio endpoint exists in api.py
grep -n "serve_audio" src/routes/api.py
# Should show line numbers with the function

# Check if audio URL format is correct
grep -n "/api/audio/" src/services/history_service.py
# Should show the updated URL format
```

### Expected Output

```bash
# For api.py
src/routes/api.py:XXX:def serve_audio(filename: str):
src/routes/api.py:XXX:@api_bp.route('/audio/<filename>', methods=['GET'])

# For history_service.py
src/services/history_service.py:XX:'audioUrl': f'/api/audio/{os.path.basename(audio_path)}'
```

## Quick Reference Card

```
╔════════════════════════════════════════════════╗
║   SCP Transfer Quick Reference                 ║
╠════════════════════════════════════════════════╣
║                                                ║
║  1. Get Pi IP:                                 ║
║     hostname -I                                ║
║                                                ║
║  2. Transfer files (Windows):                  ║
║     cd C:\Users\dell\Downloads\SmartReader     ║
║                                                ║
║     scp pi-server\src\routes\api.py \          ║
║       user@IP:~/SmartReader/pi-server/...      ║
║                                                ║
║     scp pi-server\src\services\history_*.py \  ║
║       user@IP:~/SmartReader/pi-server/...      ║
║                                                ║
║  3. Restart server (Pi):                       ║
║     cd ~/SmartReader/pi-server                 ║
║     source venv/bin/activate                   ║
║     python -m src.app                          ║
║                                                ║
╚════════════════════════════════════════════════╝
```

## Complete Transfer Script

Save this as `transfer.ps1` and run in PowerShell:

```powershell
# transfer.ps1
# Update these variables
$PI_IP = "192.168.137.123"  # Your Pi's IP
$PI_USER = "hibaanasibtissame"
$PROJECT_PATH = "C:\Users\dell\Downloads\SmartReader"

# Navigate to project
cd $PROJECT_PATH

# Transfer files
Write-Host "Transferring api.py..."
scp pi-server\src\routes\api.py ${PI_USER}@${PI_IP}:~/SmartReader/pi-server/src/routes/api.py

Write-Host "Transferring history_service.py..."
scp pi-server\src\services\history_service.py ${PI_USER}@${PI_IP}:~/SmartReader/pi-server/src/services/history_service.py

Write-Host "Transfer complete!"
Write-Host "Now restart the server on Pi:"
Write-Host "  cd ~/SmartReader/pi-server"
Write-Host "  source venv/bin/activate"
Write-Host "  python -m src.app"
```

Run it:
```powershell
.\transfer.ps1
```

## After Transfer Checklist

- [ ] Files transferred successfully (no errors)
- [ ] Verified files exist on Pi
- [ ] Checked file contents (grep commands)
- [ ] Restarted Pi server
- [ ] Tested scanning with mobile app
- [ ] Audio plays on phone (no 404 error)

## Summary

**What to transfer:** 2 files
- `pi-server/src/routes/api.py`
- `pi-server/src/services/history_service.py`

**How:** Use SCP command or WinSCP GUI

**Then:** Restart server on Pi

**Test:** Scan document, audio should play on phone

---

**Ready?** Get your Pi's IP and run the SCP commands! 🚀
