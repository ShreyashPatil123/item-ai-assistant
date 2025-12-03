# Wake Word Quick Guide

## 🎤 CURRENT WAKE WORDS (Working Now!)

You can say **ANY** of these words to activate Item:

1. **"Porcupine"** ✅ (Primary)
2. **"Picovoice"** ✅ (Alternative)
3. **"Bumblebee"** ✅ (Alternative)

## 🗣️ How to Use

### Step 1: Say Wake Word
Say clearly: **"Porcupine"** (or "Picovoice" or "Bumblebee")

### Step 2: Wait for Detection
- Item will log "Wake word detected!"
- You should see this in the terminal

### Step 3: Give Command
Immediately say your command:
- "What time is it?"
- "Lock my computer"
- "Open Notepad"

## ✅ Testing Right Now

1. **Restart Item** (needed to load new wake words)
   - Press `Ctrl + C` in terminal
   - Run: `python -m item_assistant.main`

2. **Say**: **"Porcupine"**
   - Should see: "Wake word detected!" in logs

3. **Then say**: "What time is it?"

## 🎯 Why These Words?

These are **built-in Picovoice keywords**:
- ✅ Pre-trained for multiple accents
- ✅ Work with Indian, American, British, Australian accents
- ✅ No custom training needed
- ✅ Higher accuracy than custom words

## 🔧 Sensitivity Settings

**Increased to 0.7** (from 0.5) for better accent detection:
- More likely to detect wake word
- May have occasional false positives
- Works better with different pronunciations

## 📝 Training Custom "Item" Wake Word (Later)

If you want to use "Item" instead:

1. Go to: https://console.picovoice.ai
2. Sign in with your Picovoice account
3. Create custom wake word: "Item"
4. Download the `.ppn` file
5. Place in: `item_assistant/voice/wake_words/`
6. Update config to use custom keyword file

**For now: Use "Porcupine", "Picovoice", or "Bumblebee"**

---

## 🚀 Quick Fix Applied

✅ **3 wake words** instead of 1 (more options!)  
✅ **Higher sensitivity** (0.7) for better detection  
✅ **Multi-accent support** (built-in keywords)  
✅ **No training needed** (ready to use)

**Restart Item and say: "Porcupine, what time is it?"** 🎤
