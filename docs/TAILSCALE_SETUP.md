# Tailscale Setup Guide - Remote Access Anywhere

Tailscale creates a secure VPN network between your devices. Access Item from anywhere without port forwarding!

---

## What is Tailscale?

- **Free VPN** for personal use (up to 100 devices)
- **Secure** - All traffic encrypted
- **Easy** - No port forwarding needed
- **Works everywhere** - Mobile data, different networks, etc.

---

## Step 1: Install Tailscale on Laptop

### Download

1. Visit: https://tailscale.com/download
2. Download **Windows** version
3. Run installer
4. Follow installation wizard

### Verify Installation

```powershell
tailscale --version
# Should show version info
```

---

## Step 2: Sign In to Tailscale

### First Time Setup

1. After installation, Tailscale icon appears in system tray
2. Click icon → "Sign in"
3. Browser opens to login page
4. Sign in with:
   - Google account
   - Microsoft account
   - GitHub account
   - Apple account

### After Sign In

1. Tailscale connects to VPN
2. You get a **Tailscale IP** (e.g., `100.101.102.103`)
3. Icon shows "Connected" ✅

### Find Your Tailscale IP

```powershell
tailscale ip -4
# Shows your Tailscale IPv4 address
```

**Save this IP!** You'll need it for the app.

---

## Step 3: Install Tailscale on Phone

### Android

1. Open **Google Play Store**
2. Search: "Tailscale"
3. Install official Tailscale app
4. Open app
5. Tap "Sign in"
6. Sign in with **SAME account** as laptop
7. Approve device

### iPhone

1. Open **App Store**
2. Search: "Tailscale"
3. Install official Tailscale app
4. Open app
5. Tap "Sign in"
6. Sign in with **SAME account** as laptop
7. Approve device

---

## Step 4: Verify Connection

### On Laptop

```powershell
tailscale status
# Shows all connected devices
```

You should see your phone listed.

### On Phone

1. Open Tailscale app
2. Should show laptop as "Connected"
3. Tap laptop to see its Tailscale IP

---

## Step 5: Configure Item App

### In Android App Settings

1. Open Item Assistant app
2. Tap ⚙️ Settings
3. Enter:
   - **Auth Token:** `ia9dz57KRh3CjQPyN9R7gNRVwkHKBRJ1h73g4rXA7jQ`
   - **Laptop IP:** Your **Tailscale IP** (e.g., `100.101.102.103`)
   - **Port:** `8765`
4. Tap "Test Connection"
5. If successful, tap "Save Settings"

---

## Step 6: Test Remote Access

### Test from Different Network

1. Disconnect phone from home Wi-Fi
2. Use mobile data
3. Open Item app
4. Send command: "what time is it"
5. Should work! ✅

### Test Commands

- "what time is it"
- "open notepad"
- "open chrome"

---

## Troubleshooting

### "Can't connect to Tailscale"

**Solution:**
1. Check internet connection
2. Restart Tailscale app
3. Sign out and sign back in
4. Restart phone

### "Phone doesn't see laptop"

**Solution:**
1. Ensure both signed into same Tailscale account
2. Check laptop shows "Connected" in Tailscale
3. Wait 30 seconds for sync
4. Restart both apps

### "Connection test fails in app"

**Solution:**
1. Verify Tailscale IP is correct
2. Ensure Item system is running on laptop
3. Check auth token is correct
4. Test from laptop first: `curl http://TAILSCALE_IP:8765/health`

### "Works on Wi-Fi but not mobile data"

**Solution:**
1. Ensure Tailscale is connected on phone
2. Check Tailscale app shows "Connected"
3. Restart Tailscale on phone
4. Check firewall on laptop

---

## Advanced: Tailscale Admin Console

### Access Admin Console

1. Visit: https://login.tailscale.com
2. Sign in with your account
3. See all connected devices
4. Manage access controls
5. View device IPs

### Useful Features

- **Device names** - Rename devices for easy identification
- **Access controls** - Restrict which devices can communicate
- **Sharing** - Share access with other Tailscale accounts
- **DNS** - Custom DNS configuration

---

## Security Notes

✅ **Secure:**
- All traffic encrypted end-to-end
- No data stored on Tailscale servers
- Private network - only your devices
- No port forwarding needed

⚠️ **Best Practices:**
- Keep auth token secret
- Use strong passwords
- Don't share Tailscale IP publicly
- Review connected devices regularly

---

## Tailscale Pricing

- **Free Plan:** Up to 100 devices, personal use
- **Pro Plan:** $60/year, more features
- **Business Plan:** For organizations

For personal use, **Free Plan is perfect!**

---

## What's Next?

1. ✅ Install Tailscale on laptop and phone
2. ✅ Sign in with same account
3. ✅ Configure Item app with Tailscale IP
4. ✅ Test from different network
5. Enjoy remote access from anywhere! 🌍

---

## Quick Reference

| Step | Command/Action |
|------|---|
| Find Tailscale IP | `tailscale ip -4` |
| Check status | `tailscale status` |
| Restart Tailscale | Restart app or `tailscale down && tailscale up` |
| Admin console | https://login.tailscale.com |
| Support | https://tailscale.com/support |

---

**Now you can control Item from anywhere in the world! 🚀**
