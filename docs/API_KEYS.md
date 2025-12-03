# API Keys Guide - Item AI Assistant

This guide provides step-by-step instructions for obtaining all required API keys.

## Overview

Item uses several free-tier APIs. All are **100% free** for personal use with no auto-upgrade to paid plans.

| Service | Purpose | Required | Free Tier Limits |
|---------|---------|----------|------------------|
| **Picovoice** | Wake word detection | For wake word | 3 models free |
| **Groq** | Online LLM (primary) | Optional | 14,400 requests/day |
| **Google Gemini** | Online LLM (fallback) | Optional | 60 requests/min free |

---

## 1. Picovoice Access Key (Wake Word)

**Purpose**: Enables "Item" wake word detection

### Steps:

1. **Go to Picovoice Console**
   - Visit: https://console.picovoice.ai/signup
   
2. **Create Account**
   - Sign up with email (free account)
   - Verify email

3. **Get Access Key**
   - After login, you'll see your Access Key on the dashboard
   - Copy the key (format: `xxxxx==`)

4. **Add to Config**
   - Open `item_assistant\config\config.yaml`
   - Find `voice.wake_word.access_key`
   - Paste your key:
     ```yaml
     voice:
       wake_word:
         enabled: true
         access_key: "YOUR_ACCESS_KEY_HERE"
     ```

### Notes:
- Free tier: 3 custom wake words
- For "Item" wake word, you need to train it at console.picovoice.ai
- Temporary: Use built-in "porcupine" keyword for testing

---

## 2. Groq API Key (Online LLM - Primary)

**Purpose**: Fast online LLM inference

### Steps:

1. **Go to Groq Console**
   - Visit: https://console.groq.com/

2. **Sign Up**
   - Click "Sign Up" or "Get Started"
   - Use Google/GitHub account or email
   - No credit card required

3. **Create API Key**
   - Click on your profile → "API Keys"
   - Click "Create API Key"
   - Give it a name (e.g., "Item Assistant")
   - Copy the key immediately (format: `gsk_xxxxx`)
   - **Save it securely** - it won't be shown again!

4. **Add to Config**
   - Open `item_assistant\config\config.yaml`
   - Find `llm.online.groq.api_key`
   - Paste your key:
     ```yaml
     llm:
       online:
         groq:
           enabled: true
           api_key: "YOUR_GROQ_API_KEY"
     ```

### Free Tier Limits:
- 14,400 requests per day
- 30 requests per minute
- Sufficient for heavy personal use

---

## 3. Google Gemini API Key (Online LLM - Fallback)

**Purpose**: Fallback when Groq is unavailable

### Steps:

1. **Go to Google AI Studio**
   - Visit: https://ai.google.dev/

2. **Get API Key**
   - Click "Get API Key" or "Get started"
   - Sign in with Google account
   - Click "Create API Key"
   - Select "Create API key in new project"
   - Copy the key (format: `AIzaSyxxxxx`)

3. **Add to Config**
   - Open `item_assistant\config\config.yaml`
   - Find `llm.online.gemini.api_key`
   - Paste your key:
     ```yaml
     llm:
       online:
         gemini:
           enabled: true
           api_key: "YOUR_GEMINI_API_KEY"
     ```

### Free Tier Limits:
- 60 requests per minute
- 1,500 requests per day (free tier)
- No credit card required for free tier

---

## 4. Tailscale (Optional - For Remote Access)

**Purpose**: Secure VPN for accessing laptop from anywhere

### Steps:

1. **Sign Up**
   - Visit: https://tailscale.com/
   - Click "Get Started"
   - Sign up with Google/GitHub/email

2. **Install on Laptop**
   - Download Windows installer
   - Install and sign in
   - Your laptop gets a Tailscale IP (e.g., `100.101.102.103`)

3. **Install on Phone**
   - Install Tailscale app from Play Store
   - Sign in with same account
   - Your phone gets a Tailscale IP

4. **Use in Android App**
   - In Item Android app, use laptop's Tailscale IP
   - Works from anywhere with internet!

### Free Tier:
- Up to 100 devices
- Unlimited bandwidth
- Perfect for personal use

---

## Configuration File Template

After getting all keys, your `config.yaml` should look like:

```yaml
voice:
  wake_word:
    enabled: true
    access_key: "YOUR_PICOVOICE_KEY"

llm:
  online:
    groq:
      enabled: true
      api_key: "YOUR_GROQ_KEY"
    
    gemini:
      enabled: true
      api_key: "YOUR_GEMINI_KEY"
```

---

## Verification

Test each service:

### 1. Test Picovoice
```powershell
python -c "import pvporcupine; print('Picovoice OK')"
```

### 2. Test Groq
```python
from groq import Groq
client = Groq(api_key="YOUR_KEY")
# Should not error
```

### 3. Test Gemini
```python
import google.generativeai as genai
genai.configure(api_key="YOUR_KEY")
# Should not error
```

---

## Troubleshooting

### "Invalid API key" errors

- Double-check you copied the full key (no extra spaces)
- Ensure key is within quotes in YAML file
- For Groq: Key should start with `gsk_`
- For Gemini: Key should start with `AIza`

### "Rate limit exceeded"

- Groq: 14,400/day limit reached, wait or use Gemini fallback
- Gemini: 60/min limit, Item will auto-fallback to local

### "Picovoice keyword not found"

- Use built-in keyword "porcupine" for testing
- Train custom "Item" keyword at console.picovoice.ai

---

## Security Best Practices

1. **Never commit config.yaml to Git** (already in .gitignore)
2. **Keep API keys private** - don't share screenshots
3. **Rotate keys** if accidentally exposed
4. **Use separate keys** for different projects

---

## Cost Management

All services have generous free tiers. To avoid any charges:

1. **Groq**: No credit card needed, hard limits on free tier
2. **Gemini**: No auto-upgrade, hard stops at free limits
3. **Picovoice**: Free tier, no credit card required

**Item is designed to work entirely within free tiers!**

---

## Need Help?

- **Groq docs**: https://console.groq.com/docs
- **Gemini docs**: https://ai.google.dev/docs
- **Picovoice docs**: https://picovoice.ai/docs/

---

**You're all set! 🎉**

Once all keys are added to `config.yaml`, start Item:
```powershell
python -m item_assistant.main
```
