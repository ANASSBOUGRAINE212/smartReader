#!/bin/bash
# SmartReader Network Setup Script
# Run this on Raspberry Pi to configure network and check connectivity

echo "========================================="
echo "SmartReader Network Setup"
echo "========================================="
echo ""

# Check if running on Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo ""
fi

# Get current IP addresses
echo "📡 Current Network Configuration:"
echo "-----------------------------------"
hostname -I | tr ' ' '\n' | while read ip; do
    if [ ! -z "$ip" ]; then
        echo "  IP Address: $ip"
    fi
done
echo ""

# Check WiFi status
echo "📶 WiFi Status:"
echo "-----------------------------------"
if command -v iwgetid &> /dev/null; then
    SSID=$(iwgetid -r)
    if [ ! -z "$SSID" ]; then
        echo "  Connected to: $SSID"
        echo "  ✅ WiFi is connected"
    else
        echo "  ❌ Not connected to WiFi"
        echo ""
        echo "To connect to WiFi:"
        echo "  sudo raspi-config"
        echo "  → System Options → Wireless LAN"
    fi
else
    echo "  Unable to check WiFi status"
fi
echo ""

# Check if server port is open
echo "🔌 Server Port Check:"
echo "-----------------------------------"
if command -v netstat &> /dev/null; then
    if netstat -tuln | grep -q ":5000"; then
        echo "  ✅ Port 5000 is open"
    else
        echo "  ❌ Port 5000 is not open"
        echo "  Start the server with: python -m src.app"
    fi
else
    echo "  Unable to check port status"
fi
echo ""

# Test local server
echo "🏥 Server Health Check:"
echo "-----------------------------------"
if command -v curl &> /dev/null; then
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/health 2>/dev/null)
    if [ "$RESPONSE" = "200" ]; then
        echo "  ✅ Server is running and healthy"
        curl -s http://localhost:5000/api/health | python3 -m json.tool 2>/dev/null || echo ""
    else
        echo "  ❌ Server is not responding (HTTP $RESPONSE)"
        echo "  Start the server with: python -m src.app"
    fi
else
    echo "  curl not installed - cannot test server"
fi
echo ""

# Get primary IP for mobile app
echo "📱 Mobile App Configuration:"
echo "-----------------------------------"
PRIMARY_IP=$(hostname -I | awk '{print $1}')
if [ ! -z "$PRIMARY_IP" ]; then
    echo "  Enter this in your mobile app:"
    echo ""
    echo "  ┌─────────────────────────────┐"
    echo "  │ Hostname: $PRIMARY_IP"
    echo "  │ Port:     5000              │"
    echo "  └─────────────────────────────┘"
    echo ""
    echo "  Full URL: http://$PRIMARY_IP:5000"
else
    echo "  ❌ No IP address found"
fi
echo ""

# Check firewall
echo "🔥 Firewall Status:"
echo "-----------------------------------"
if command -v ufw &> /dev/null; then
    UFW_STATUS=$(sudo ufw status 2>/dev/null | grep -i "status:" | awk '{print $2}')
    if [ "$UFW_STATUS" = "active" ]; then
        echo "  ⚠️  Firewall is active"
        echo "  Allow port 5000 with: sudo ufw allow 5000"
    else
        echo "  ✅ Firewall is inactive"
    fi
else
    echo "  No firewall detected"
fi
echo ""

# Network test from external device
echo "🌐 Network Accessibility Test:"
echo "-----------------------------------"
echo "  From another device on the same network, run:"
echo ""
echo "  curl http://$PRIMARY_IP:5000/api/health"
echo ""
echo "  Expected response:"
echo '  {"status": "ok", "timestamp": "..."}'
echo ""

# Summary
echo "========================================="
echo "Summary"
echo "========================================="
echo ""

# Check all requirements
ALL_GOOD=true

# Check WiFi
if [ ! -z "$SSID" ]; then
    echo "✅ WiFi: Connected to $SSID"
else
    echo "❌ WiFi: Not connected"
    ALL_GOOD=false
fi

# Check IP
if [ ! -z "$PRIMARY_IP" ]; then
    echo "✅ IP Address: $PRIMARY_IP"
else
    echo "❌ IP Address: Not found"
    ALL_GOOD=false
fi

# Check server
if [ "$RESPONSE" = "200" ]; then
    echo "✅ Server: Running"
else
    echo "❌ Server: Not running"
    ALL_GOOD=false
fi

echo ""

if [ "$ALL_GOOD" = true ]; then
    echo "🎉 Everything looks good!"
    echo ""
    echo "Next steps:"
    echo "1. Make sure your phone is on the same WiFi network: $SSID"
    echo "2. Open SmartReader app on your phone"
    echo "3. Go to Settings → Pi Connection Settings"
    echo "4. Enter: $PRIMARY_IP (port 5000)"
    echo "5. Tap 'Save & Connect'"
else
    echo "⚠️  Some issues need to be fixed"
    echo ""
    echo "Common fixes:"
    echo "1. Connect to WiFi: sudo raspi-config → Wireless LAN"
    echo "2. Start server: cd ~/SmartReader/pi-server && python -m src.app"
    echo "3. Allow firewall: sudo ufw allow 5000"
fi

echo ""
echo "========================================="
