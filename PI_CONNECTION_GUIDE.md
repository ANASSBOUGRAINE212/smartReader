# Connecting Mobile App to Raspberry Pi

## Overview

The mobile app needs to connect to the Raspberry Pi server over the local network. There are several methods to establish this connection.

## Connection Methods

### Method 1: Using mDNS (Recommended for Local Network)

**What is mDNS?**
mDNS (Multicast DNS) allows devices to discover each other on a local network using `.local` hostnames instead of IP addresses.

**Setup on Raspberry Pi:**

1. Install Avahi (mDNS service):
```bash
sudo apt-get update
sudo apt-get install avahi-daemon avahi-utils
```

2. Set hostname to `smartreader`:
```bash
sudo hostnamectl set-hostname smartreader
sudo reboot
```

3. Verify mDNS is working:
```bash
avahi-browse -a
# Should show your Pi as smartreader.local
```

**Mobile App Configuration:**

The app is already configured to use `smartreader.local:5000` by default. No changes needed!

**Test Connection:**
```bash
# From your computer on the same network
ping smartreader.local
curl http://smartreader.local:5000/api/health
```

**Pros:**
- ✅ No need to find IP address
- ✅ Works even if Pi IP changes
- ✅ Easy to remember

**Cons:**
- ❌ Requires Avahi on Pi
- ❌ May not work on all networks (corporate/guest WiFi)

---

### Method 2: Using Static IP Address

**Setup on Raspberry Pi:**

1. Find current IP address:
```bash
hostname -I
# Example output: 192.168.1.100
```

2. Set static IP (optional but recommended):

Edit `/etc/dhcpcd.conf`:
```bash
sudo nano /etc/dhcpcd.conf
```

Add at the end:
```
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

Save and reboot:
```bash
sudo reboot
```

**Mobile App Configuration:**

Update the API service to use the IP address:

Edit `smartreader-mobile-clean/src/services/api.ts`:

```typescript
// Change line 11 from:
constructor(hostname: string = 'smartreader.local', port: number = 5000) {

// To:
constructor(hostname: string = '192.168.1.100', port: number = 5000) {
```

**Test Connection:**
```bash
curl http://192.168.1.100:5000/api/health
```

**Pros:**
- ✅ Works on all networks
- ✅ Reliable and fast
- ✅ No additional software needed

**Cons:**
- ❌ Need to update app if IP changes
- ❌ Need to find IP address first

---

### Method 3: Dynamic IP Discovery (Add Settings Screen)

**Best for production!** Let users enter the Pi IP address in the app.

**Implementation:**

1. Add a connection settings screen to the mobile app:

Create `smartreader-mobile-clean/app/connection-settings.tsx`:

```typescript
import React, { useState } from 'react';
import { StyleSheet, View, TextInput, TouchableOpacity, Alert } from 'react-native';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { useAppStore } from '@/src/store';
import { setApiHostname } from '@/src/services/api';
import { router } from 'expo-router';

export default function ConnectionSettings() {
  const { piHostname, piPort, setPiConnection } = useAppStore();
  const [hostname, setHostname] = useState(piHostname);
  const [port, setPort] = useState(piPort.toString());

  const handleSave = () => {
    const portNum = parseInt(port);
    if (isNaN(portNum) || portNum < 1 || portNum > 65535) {
      Alert.alert('Error', 'Invalid port number');
      return;
    }

    setPiConnection(hostname, portNum);
    setApiHostname(hostname, portNum);
    
    Alert.alert('Success', 'Connection settings saved. Reconnecting...', [
      { text: 'OK', onPress: () => router.back() }
    ]);
  };

  return (
    <ThemedView style={styles.container}>
      <ThemedText style={styles.title}>Pi Server Connection</ThemedText>
      
      <View style={styles.inputContainer}>
        <ThemedText style={styles.label}>Hostname or IP Address</ThemedText>
        <TextInput
          style={styles.input}
          value={hostname}
          onChangeText={setHostname}
          placeholder="smartreader.local or 192.168.1.100"
          autoCapitalize="none"
          autoCorrect={false}
        />
      </View>

      <View style={styles.inputContainer}>
        <ThemedText style={styles.label}>Port</ThemedText>
        <TextInput
          style={styles.input}
          value={port}
          onChangeText={setPort}
          placeholder="5000"
          keyboardType="number-pad"
        />
      </View>

      <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
        <ThemedText style={styles.saveButtonText}>Save & Connect</ThemedText>
      </TouchableOpacity>

      <View style={styles.helpContainer}>
        <ThemedText style={styles.helpTitle}>How to find your Pi:</ThemedText>
        <ThemedText style={styles.helpText}>
          1. On your Pi, run: hostname -I{'\n'}
          2. Use the first IP address shown{'\n'}
          3. Or use: smartreader.local if mDNS is set up
        </ThemedText>
      </View>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 30,
  },
  inputContainer: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#F5F5F5',
    padding: 15,
    borderRadius: 8,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  saveButton: {
    backgroundColor: '#2196F3',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  helpContainer: {
    marginTop: 40,
    padding: 15,
    backgroundColor: '#E3F2FD',
    borderRadius: 8,
  },
  helpTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  helpText: {
    fontSize: 14,
    lineHeight: 22,
  },
});
```

2. Add a button to access connection settings in the Settings screen:

Add to `smartreader-mobile-clean/app/(tabs)/settings.tsx` (after the header):

```typescript
import { router } from 'expo-router';

// Add this button after the header
<TouchableOpacity
  style={styles.connectionButton}
  onPress={() => router.push('/connection-settings')}
>
  <ThemedText style={styles.connectionButtonText}>
    Pi Connection Settings
  </ThemedText>
</TouchableOpacity>

// Add to styles
connectionButton: {
  backgroundColor: '#4CAF50',
  padding: 15,
  borderRadius: 8,
  alignItems: 'center',
  marginBottom: 20,
},
connectionButtonText: {
  color: '#FFFFFF',
  fontSize: 16,
  fontWeight: '600',
},
```

**Pros:**
- ✅ User-friendly
- ✅ Works with any setup
- ✅ No code changes needed
- ✅ Can switch between multiple Pis

**Cons:**
- ❌ Requires additional screen
- ❌ User needs to know Pi IP

---

## Network Requirements

### Both Devices Must Be On Same Network

**Check on Raspberry Pi:**
```bash
# Check WiFi connection
iwconfig

# Check IP address
hostname -I

# Check network name
iwgetid -r
```

**Check on Mobile Device:**
- Go to WiFi settings
- Verify connected to same network as Pi
- Note: Guest networks often block device-to-device communication

### Firewall Configuration

**On Raspberry Pi:**

1. Check if firewall is blocking:
```bash
sudo ufw status
```

2. If active, allow port 5000:
```bash
sudo ufw allow 5000/tcp
sudo ufw reload
```

3. Or disable firewall (for testing only):
```bash
sudo ufw disable
```

### Router Configuration

Some routers have "AP Isolation" or "Client Isolation" enabled, which prevents devices from communicating with each other.

**To disable:**
1. Access router admin panel (usually 192.168.1.1)
2. Look for "AP Isolation" or "Client Isolation"
3. Disable it
4. Restart router

---

## Testing Connection

### Step 1: Test from Computer

Before testing from mobile, verify the Pi server is accessible:

```bash
# Test from another computer on same network
curl http://smartreader.local:5000/api/health
# or
curl http://192.168.1.100:5000/api/health

# Expected response:
# {"status":"ok","timestamp":"2026-05-04T..."}
```

### Step 2: Test from Mobile Browser

1. Open mobile browser (Safari/Chrome)
2. Navigate to: `http://smartreader.local:5000/api/health`
3. Should see JSON response

If this works, the mobile app will work too!

### Step 3: Test from Mobile App

1. Open SmartReader app
2. Check connection status badge
3. Should show "Connected" in green
4. If not, tap "Reconnect"

---

## Troubleshooting

### Problem: "Cannot connect to smartreader.local"

**Solutions:**

1. **Use IP address instead:**
   ```bash
   # On Pi, find IP:
   hostname -I
   
   # Update mobile app to use IP
   ```

2. **Check mDNS is running on Pi:**
   ```bash
   sudo systemctl status avahi-daemon
   # Should show "active (running)"
   ```

3. **Restart mDNS:**
   ```bash
   sudo systemctl restart avahi-daemon
   ```

### Problem: "Connection refused"

**Solutions:**

1. **Check Pi server is running:**
   ```bash
   # On Pi:
   python -m src.app
   ```

2. **Check port 5000 is listening:**
   ```bash
   sudo netstat -tulpn | grep 5000
   ```

3. **Check firewall:**
   ```bash
   sudo ufw status
   sudo ufw allow 5000/tcp
   ```

### Problem: "Network request failed"

**Solutions:**

1. **Check both devices on same WiFi:**
   - Pi: `iwgetid -r`
   - Mobile: Check WiFi settings

2. **Check router AP Isolation:**
   - Disable in router settings

3. **Try pinging Pi from mobile:**
   - Use network utility app
   - Ping `smartreader.local` or Pi IP

### Problem: "Connection timeout"

**Solutions:**

1. **Check Pi is on network:**
   ```bash
   ping smartreader.local
   ```

2. **Check Pi server logs:**
   ```bash
   # Look for errors in terminal where server is running
   ```

3. **Restart both devices:**
   - Reboot Pi: `sudo reboot`
   - Restart mobile app

---

## Production Deployment

### For Real-World Use:

1. **Use Static IP** on the Pi
2. **Add Connection Settings Screen** in the app
3. **Add QR Code Setup:**
   - Generate QR code with Pi IP
   - Scan with app to auto-configure
   - Example: `smartreader://connect?host=192.168.1.100&port=5000`

4. **Add Network Discovery:**
   - Scan local network for Pi servers
   - Auto-detect and connect
   - Use mDNS service discovery

5. **Add Connection Status Notifications:**
   - Show toast when connected/disconnected
   - Retry connection automatically
   - Cache last known IP

---

## Quick Reference

### Find Pi IP Address
```bash
hostname -I
```

### Test Pi Server
```bash
curl http://localhost:5000/api/health
```

### Update Mobile App Hostname
Edit `smartreader-mobile-clean/src/services/api.ts` line 11

### Check Connection from Mobile
Open browser: `http://smartreader.local:5000/api/health`

### Common Hostnames
- `smartreader.local` (mDNS)
- `192.168.1.100` (example static IP)
- `localhost` (only works on Pi itself)

---

## Summary

**Easiest Setup (Recommended):**
1. Install Avahi on Pi: `sudo apt-get install avahi-daemon`
2. Set hostname: `sudo hostnamectl set-hostname smartreader`
3. Use default app settings (smartreader.local)
4. Both devices on same WiFi
5. Done! ✅

**Most Reliable Setup:**
1. Set static IP on Pi
2. Update app with Pi IP address
3. Both devices on same WiFi
4. Done! ✅

**Best for Production:**
1. Add connection settings screen to app
2. Let users enter Pi IP
3. Save in app state
4. Auto-reconnect on app launch
