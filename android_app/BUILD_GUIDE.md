# Android App Build Guide

## Prerequisites

1. **Android Studio** (Latest version)
   - Download: https://developer.android.com/studio
   - Install and launch

2. **Android SDK 26+** (8.0 Oreo minimum)
   - Installed automatically with Android Studio
   - Verify: Tools → SDK Manager → Android 8.0 (API 26) or higher

3. **Java 11+**
   - Included with Android Studio

## Step-by-Step Build Instructions

### 1. Open Project in Android Studio

```
File → Open → Select android_app folder
```

Android Studio will automatically:
- Detect the Gradle build files
- Download Gradle wrapper
- Sync dependencies
- Index the project

**Wait for "Gradle sync finished" message** (may take 2-5 minutes on first build)

### 2. Configure Your Settings

Before building, update the default settings in the app:

**File:** `app/src/main/java/com/item/assistant/MainActivity.kt`

Update these values:
```kotlin
val ip = prefs.getString("laptop_ip", "192.168.1.100") ?: "192.168.1.100"
val port = prefs.getInt("api_port", 8765)
```

Or configure in the app's Settings screen after installation.

### 3. Build APK

**Option A: Debug APK (Faster, for testing)**
```
Build → Build Bundle(s) / APK(s) → Build APK
```

**Option B: Release APK (Optimized, for production)**
```
Build → Build Bundle(s) / APK(s) → Build APK (Release)
```

**Wait for "Build successful" message**

### 4. Locate APK

Debug APK location:
```
app/build/outputs/apk/debug/app-debug.apk
```

Release APK location:
```
app/build/outputs/apk/release/app-release.apk
```

### 5. Install on Phone

**Option A: Via Android Studio (Easiest)**
1. Connect phone via USB
2. Enable USB Debugging on phone:
   - Settings → Developer Options → USB Debugging
3. Click "Run" ▶ button in Android Studio
4. Select your phone
5. App installs and launches automatically

**Option B: Manual Installation**
1. Copy APK to phone
2. Open file manager on phone
3. Tap APK file
4. Tap "Install"
5. Grant permissions
6. Launch app

**Option C: Via ADB Command**
```powershell
adb install app/build/outputs/apk/debug/app-debug.apk
```

## Configuration in App

### First Launch

1. Open Item Assistant app
2. Tap ⚙️ Settings button
3. Enter:
   - **Auth Token:** `ia9dz57KRh3CjQPyN9R7gNRVwkHKBRJ1h73g4rXA7jQ`
   - **Laptop IP:** Your laptop's IP (find with `ipconfig`)
   - **Port:** `8765`
4. Tap "Test Connection"
5. If successful, tap "Save Settings"

### Finding Your Laptop IP

**On Laptop (PowerShell):**
```powershell
ipconfig
# Look for "IPv4 Address" (e.g., 192.168.1.100)
```

**Network Types:**
- **Local Network:** 192.168.x.x or 10.x.x.x
- **Tailscale:** 100.x.x.x (if using Tailscale)

## Testing

### Test Commands

After configuration, try these commands in the app:

1. **"what time is it"** - Should return current time
2. **"open notepad"** - Should open Notepad on laptop
3. **"open chrome"** - Should open Chrome on laptop

### Troubleshooting

**"Connection Failed"**
- Verify laptop IP is correct
- Ensure phone and laptop on same network
- Check firewall allows port 8765
- Verify auth token is correct

**"App crashes on startup"**
- Check Android version is 8.0 or higher
- Reinstall app
- Clear app cache: Settings → Apps → Item Assistant → Storage → Clear Cache

**"Commands not executing"**
- Verify Item system is running on laptop
- Check auth token in settings
- Test with API from laptop first

## Building Release APK

For publishing to Google Play Store:

1. Create signing key:
   ```
   Build → Generate Signed Bundle / APK
   ```

2. Create new keystore:
   - Key store path: Choose location
   - Password: Create strong password
   - Key alias: "item-assistant"
   - Key password: Same as keystore

3. Build Release APK:
   - Select your keystore
   - Enter passwords
   - Choose "Release" variant

4. Signed APK ready for distribution

## Project Structure

```
android_app/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/item/assistant/
│   │   │   │   ├── MainActivity.kt          # Main UI
│   │   │   │   ├── SettingsActivity.kt      # Settings
│   │   │   │   └── ApiClient.kt             # API communication
│   │   │   ├── res/
│   │   │   │   ├── layout/
│   │   │   │   │   ├── activity_main.xml
│   │   │   │   │   └── activity_settings.xml
│   │   │   │   └── values/
│   │   │   │       ├── strings.xml
│   │   │   │       └── themes.xml
│   │   │   └── AndroidManifest.xml
│   │   └── test/
│   ├── build.gradle
│   └── proguard-rules.pro
├── build.gradle
├── settings.gradle
└── BUILD_GUIDE.md
```

## Next Steps

1. ✅ Build APK
2. ✅ Install on phone
3. ✅ Configure settings
4. ✅ Test commands
5. Setup Tailscale for remote access (optional)
6. Build release APK for distribution (optional)

## Support

For issues:
1. Check troubleshooting section above
2. Review Item system logs on laptop
3. Test API directly from laptop
4. Check Android Studio logcat for app errors

---

**Happy building! 🚀**
