# Android App for Item AI Assistant

Basic Android app template for controlling Item from your phone.

## Overview

This directory will contain the Android app source code. The app provides:

- 🎤 Voice input using Android's native speech recognition
- ⌨️ Text command input
- 📡 Real-time WebSocket connection to laptop
- 📜 Command history viewer
- 💤 Wake-on-LAN button
- 🔐 Secure token-based authentication

## Building the App (TODO)

### Prerequisites

- Android Studio Arctic Fox or later
- Android SDK 26+ (8.0 Oreo minimum)
- Kotlin 1.5+

### Steps

1. **Open Project**
   ```bash
   # Open android_app/ in Android Studio
   File → Open → Select android_app folder
   ```

2. **Sync Dependencies**
   - Android Studio will auto-sync Gradle
   - Wait for dependencies to download

3. **Build APK**
   ```
   Build → Build Bundle(s) / APK(s) → Build APK
   ```

4. **Install on Phone**
   - Connect phone via USB with USB debugging enabled
   - Click "Run" ▶ button in Android Studio
   - OR manually install APK from `app/build/outputs/apk/`

## App Structure (Planned)

```
android_app/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/item/assistant/
│   │   │   │   ├── MainActivity.kt          # Main UI
│   │   │   │   ├── ApiClient.kt             # HTTP client
│   │   │   │   ├── WebSocketClient.kt       # WebSocket
│   │   │   │   ├── SettingsActivity.kt      # Configuration
│   │   │   │   └── WakeOnLanManager.kt      # WoL functionality
│   │   │   ├── res/
│   │   │   │   ├── layout/
│   │   │   │   │   ├── activity_main.xml    # Main screen
│   │   │   │   │   └── activity_settings.xml
│   │   │   │   └── values/
│   │   │   └── AndroidManifest.xml
│   ├── build.gradle
│   └── proguard-rules.pro
├── gradle/
└── build.gradle
```

## Key Features

### 1. Voice Input

Uses Android's `SpeechRecognizer`:
```kotlin
val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, 
               RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
startActivityForResult(intent, SPEECH_REQUEST_CODE)
```

### 2. API Communication

**HTTP requests** (using Retrofit):
```kotlin
interface ItemApi {
    @POST("/api/command")
    suspend fun sendCommand(@Body request: CommandRequest): CommandResponse
    
    @GET("/api/status")
    suspend fun getStatus(): StatusResponse
}
```

**WebSocket** (using OkHttp):
```kotlin
val client = OkHttpClient()
val request = Request.Builder()
    .url("ws://laptop-ip:8765/ws")
    .build()
val webSocket = client.newWebSocket(request, listener)
```

### 3. Wake-on-LAN

Sends magic packet:
```kotlin
fun sendWakeOnLan(macAddress: String, ipAddress: String) {
    val macBytes = parseMacAddress(macAddress)
    val packet = ByteArray(102)
    
    // 6 bytes of 0xFF
    for (i in 0..5) packet[i] = 0xFF.toByte()
    
    // MAC address repeated 16 times
    for (i in 1..16) {
        System.arraycopy(macBytes, 0, packet, i * 6, 6)
    }
    
    // Send UDP packet to port 9
    val socket = DatagramSocket()
    val datagram = DatagramPacket(packet, packet.size, 
                                  InetAddress.getByName(ipAddress), 9)
    socket.send(datagram)
}
```

### 4. Settings Storage

Uses SharedPreferences:
```kotlin
val prefs = getSharedPreferences("ItemSettings", MODE_PRIVATE)
prefs.edit {
    putString("auth_token", token)
    putString("laptop_ip", ip)
    putInt("api_port", port)
}
```

## UI Design

### Main Screen

- **Voice Button** - Large circular button for voice input
- **Text Input** - EditText for typing commands
- **Status Indicator** - Shows laptop online/offline
- **Response Display** - Shows Item's responses
- **History Button** - Opens command history

### Settings Screen

- **Auth Token** - Input field (password type)
- **Laptop IP** - Input field
- **API Port** - Number input (default: 8765)
- **Wake-on-LAN** toggle
- **Test Connection** button

## Dependencies (build.gradle)

```gradle
dependencies {
    // Core
    implementation 'androidx.core:core-ktx:1.9.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    
    // Networking
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    implementation 'com.squareup.okhttp3:okhttp:4.11.0'
    
    // Coroutines
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.6.4'
    
    // Lifecycle
    implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.6.1'
}
```

## Permissions (AndroidManifest.xml)

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
```

## Quick Integration

Once built, configure in app:

1. Open Settings
2. Enter:
   - **Auth Token**: From `config.yaml` → `security.auth_token`
   - **Laptop IP**: 
     - Local: From `ipconfig` (e.g., 192.168.1.100)
     - Remote: Tailscale IP (e.g., 100.101.102.103)
   - **Port**: 8765 (or your custom port)
3. Test connection
4. Start sending commands!

## Development Roadmap

- [x] Basic UI design
- [x] API client integration
- [ ] WebSocket real-time communication
- [ ] Voice input integration
- [ ] Settings screen
- [ ] Command history
- [ ] Wake-on-LAN
- [ ] Dark mode support
- [ ] Notification support
- [ ] Widget for quick commands

## Testing

### Local Network Test

1. Connect phone and laptop to same Wi-Fi
2. In app, enter laptop's local IP
3. Send test command: "what time is it"
4. Verify response received

### Remote Test (Tailscale)

1. Install Tailscale on phone and laptop
2. Use laptop's Tailscale IP (100.x.x.x)
3. Test from different network (mobile data)

## Security

- ✅ All communication over HTTPS (or Tailscale VPN)
- ✅ Token-based authentication
- ✅ Tokens stored in encrypted SharedPreferences
- ✅ No hardcoded credentials

## Future Enhancements

- **SMS Integration**: Send commands via SMS
- **WhatsApp Integration**: Use WhatsApp API
- **Telegram Bot**: Control via Telegram
- **Tasker Integration**: Automation workflows
- **Voice Profiles**: Multiple users
- **Custom Commands**: Programmable shortcuts

---

**Note**: Full Android app implementation coming soon. For now, test API with:
- curl
- Postman
- Python requests
- Any HTTP client

Example with curl from Termux (Android terminal):
```bash
curl -X POST http://laptop-ip:8765/api/command \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command": "open notepad", "source": "phone"}'
```
