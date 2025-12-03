# 📱 Install Item Assistant App - Complete Guide

## Your Tailscale Addresses

```
PC (Laptop) Address: 100.82.56.25
Phone Address: 100.74.124.62
```

**✅ Both devices are connected to Tailscale!**

---

## Step 1: Build the Android App

### Option A: Using Android Studio (Recommended)

#### 1.1 Download Android Studio
1. Visit: https://developer.android.com/studio
2. Download the installer
3. Run the installer
4. Follow the installation wizard
5. Launch Android Studio

#### 1.2 Open the Project
1. Click **File → Open**
2. Navigate to: `C:\Users\Shreyash\OneDrive\Desktop\Assistant\item-assistant\android_app`
3. Click **Open**
4. Wait for Gradle sync (2-5 minutes)
   - You'll see "Gradle sync finished" message

#### 1.3 Build the APK
1. Click **Build** menu
2. Select **Build Bundle(s) / APK(s)**
3. Click **Build APK**
4. Wait for "Build successful" message
5. APK is ready at: `app/build/outputs/apk/debug/app-debug.apk`

#### 1.4 Install on Phone
1. Connect phone to laptop via USB cable
2. Enable USB Debugging on phone:
   - Settings → Developer Options → USB Debugging (toggle ON)
3. In Android Studio, click the **Run ▶** button
4. Select your phone from the list
5. Click **OK**
6. App installs and launches automatically

### Option B: Using Command Line

#### 1.1 Navigate to Project
```powershell
cd C:\Users\Shreyash\OneDrive\Desktop\Assistant\item-assistant\android_app
```

#### 1.2 Build APK
```powershell
.\gradlew.bat build
```

#### 1.3 Install on Phone
```powershell
adb install app\build\outputs\apk\debug\app-debug.apk
```

### Option C: Using Build Script

#### 1.1 Run Build Script
```powershell
cd C:\Users\Shreyash\OneDrive\Desktop\Assistant\item-assistant\android_app
.\build_apk.bat
```

#### 1.2 Install Manually
1. Copy APK to phone via USB
2. Open file manager on phone
3. Tap the APK file
4. Tap "Install"
5. Grant permissions
6. Launch app

---

## Step 2: First Launch Configuration

### On Your Phone

#### 2.1 Open the App
1. Find **Item Assistant** app on your phone
2. Tap to open

#### 2.2 Go to Settings
1. Tap **⚙️ Settings** button (top right)

#### 2.3 Enter Configuration

**For Local Network (Home Wi-Fi):**
```
Auth Token: ia9dz57KRh3CjQPyN9R7gNRVwkHKBRJ1h73g4rXA7jQ
Laptop IP: 192.168.1.10
Port: 8765
```

**For Remote Access (Tailscale - Recommended):**
```
Auth Token: ia9dz57KRh3CjQPyN9R7gNRVwkHKBRJ1h73g4rXA7jQ
Laptop IP: 100.82.56.25
Port: 8765
```

#### 2.4 Test Connection
1. Tap **"Test Connection"** button
2. Wait for response
3. Should see: **"✅ Connection successful!"**

#### 2.5 Save Settings
1. Tap **"Save Settings"** button
2. Settings are saved to phone

---

## Step 3: Test the App

### Test 1: Local Network (Home Wi-Fi)

**Configure with local IP first:**
```
Laptop IP: 192.168.1.10
```

**Then test:**
1. Open Item Assistant app
2. Type in command box: `what time is it`
3. Tap **Send** button
4. Should see response ✅

### Test 2: Remote Access (Tailscale)

**Configure with Tailscale IP:**
```
Laptop IP: 100.82.56.25
```

**Then test:**
1. Disconnect from home Wi-Fi
2. Use mobile data
3. Open Item Assistant app
4. Type: `what time is it`
5. Tap **Send**
6. Should work from anywhere! ✅

### Test 3: Try Different Commands

```
"what time is it"      → Current time
"open notepad"         → Opens Notepad on laptop
"open chrome"          → Opens Chrome on laptop
"tell me a joke"       → LLM generates joke
"what is python"       → LLM explanation
"open calculator"      → Opens Calculator
```

---

## 📋 Configuration Summary

### Your Credentials
```
Auth Token: ia9dz57KRh3CjQPyN9R7gNRVwkHKBRJ1h73g4rXA7jQ
API Port: 8765
```

### Your Network Addresses

#### Local Network (Home Wi-Fi)
```
Laptop IP: 192.168.1.10
Full URL: http://192.168.1.10:8765
```

#### Remote Access (Tailscale)
```
Laptop IP: 100.82.56.25
Phone IP: 100.74.124.62
Full URL: http://100.82.56.25:8765
```

---

## 🎯 Quick Setup (5 Steps)

### Step 1: Download Android Studio
- Visit: https://developer.android.com/studio
- Download and install

### Step 2: Open Project
- File → Open → Select `android_app` folder
- Wait for Gradle sync

### Step 3: Build APK
- Build → Build Bundle(s) / APK(s) → Build APK
- Wait for "Build successful"

### Step 4: Install on Phone
- Connect phone via USB
- Enable USB Debugging
- Click Run ▶ button

### Step 5: Configure App
- Open Item Assistant app
- Tap ⚙️ Settings
- Enter:
  - Auth Token: `ia9dz57KRh3CjQPyN9R7gNRVwkHKBRJ1h73g4rXA7jQ`
  - Laptop IP: `100.82.56.25` (Tailscale)
  - Port: `8765`
- Tap "Test Connection"
- Tap "Save Settings"

---

## ✅ Verification Checklist

- [ ] Android Studio downloaded and installed
- [ ] Project opened in Android Studio
- [ ] Gradle sync completed
- [ ] APK built successfully
- [ ] Phone connected via USB
- [ ] USB Debugging enabled on phone
- [ ] App installed on phone
- [ ] App launches successfully
- [ ] Settings configured with Tailscale IP
- [ ] Connection test successful
- [ ] Test command executed successfully

---

## 🆘 Troubleshooting

### "Gradle sync failed"
**Solution:**
- Close Android Studio
- Delete `.gradle` folder in project
- Reopen project
- Wait for sync again

### "Build failed"
**Solution:**
- Check Android SDK is installed
- Check Java version is 11+
- Check internet connection
- Try: Build → Clean Project, then Build again

### "Can't find phone"
**Solution:**
- Check USB cable is connected
- Enable USB Debugging on phone
- Restart Android Studio
- Restart phone

### "Connection test fails"
**Solution:**
- Verify IP is correct (100.82.56.25)
- Check Item system is running on laptop
- Verify auth token is correct
- Check Tailscale is connected on both devices

### "App crashes on startup"
**Solution:**
- Check Android version is 8.0 or higher
- Reinstall app
- Clear app cache: Settings → Apps → Item Assistant → Storage → Clear Cache

### "Can't connect to Tailscale IP"
**Solution:**
- Verify Tailscale is running on laptop
- Check Tailscale status: `tailscale status`
- Verify both devices signed into same Tailscale account
- Restart Tailscale on both devices

---

## 📁 Important Paths

### Android App
- **Project:** `android_app/`
- **Source Code:** `android_app/app/src/main/java/com/item/assistant/`
- **APK Output:** `android_app/app/build/outputs/apk/debug/app-debug.apk`
- **Build Guide:** `android_app/BUILD_GUIDE.md`

### Item System
- **Config:** `item_assistant/config/config.yaml`
- **Logs:** `C:\Users\Shreyash\ItemAssistant\logs\`

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `android_app/BUILD_GUIDE.md` | Detailed build instructions |
| `TAILSCALE_QUICK_SETUP.md` | Tailscale setup |
| `FINAL_SETUP_GUIDE.md` | Complete setup guide |
| `docs/TROUBLESHOOTING.md` | Fix issues |

---

## 🎉 What's Next

### After Installation
1. ✅ App installed on phone
2. ✅ Configured with Tailscale IP
3. ✅ Connection tested
4. ✅ Ready to use!

### You Can Now
- Send commands from phone
- Control laptop from anywhere
- Use mobile data (not just Wi-Fi)
- Automate tasks remotely

---

## 💡 Pro Tips

1. **Test locally first** (192.168.1.10) before trying remote
2. **Save your Tailscale IP** (100.82.56.25) somewhere safe
3. **Keep auth token private** - don't share it
4. **Restart systems** if having issues
5. **Check logs** for error details

---

## 🚀 You're Ready!

**Everything is set up. Time to build and install the app!**

### Next Action
1. Download Android Studio
2. Build the APK
3. Install on phone
4. Configure with Tailscale IP
5. Test and enjoy!

---

**Let's build the app! 🎉**
