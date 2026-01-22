# 🤖 SnapCapAI

**AI-Powered Screen Capture with Stealth Mode**

Capture screenshots using PrtSc and analyze them with AI without interrupting running applications (browser, games, videos).

---

## ⚠️ Important Notice (12/14/2025)

> **Google Free Tier currently only supports `gemini-2.5-flash`**
> 
> Other models (`gemini-2.0-flash`, `gemini-2.5-pro`, `gemini-3-pro`) require:
> - Paid account (billing enabled)
> - Or free tier quota exhausted
>
> **⏱️ Free Tier Limits (gemini-2.5-flash):**
> | Type | Limit |
> |------|-------|
> | RPM (Requests/minute) | **5 requests** |
> | TPM (Tokens/minute) | **250,000 tokens** |
> | RPD (Requests/day) | **25 requests** |
>
> **Recommendation:** Use `gemini-2.5-flash` (default) and avoid spamming PrtSc.

---

## ✨ Features

### 🕵️ Stealth Mode
- Low-level keyboard hook (WH_KEYBOARD_LL)
- Swallows PrtSc key - Browser/Game won't detect captures
- Requires Administrator privileges

### 🎯 HUD Overlay Notification
- TopMost notification without stealing focus (WS_EX_NOACTIVATE + WS_EX_TRANSPARENT)
- Click-through - Doesn't interfere with interactions
- 2 themes: ⬜ White (dim text) / ⬛ Dark
- Customizable duration: 1-10 seconds
- **600px width notification** - Clearer display

### 📸 Batch Capture
- Capture multiple screenshots in succession (max 10 images)
- 5-second debounce - Resets timer with each capture
- Auto-combines and sends all images after 5s of inactivity
- **Smart Context** - AI analyzes connections between images

### 🖱️ Double-Click Controls (0.5s threshold)
| Action | Function |
|--------|----------|
| **Double-click LEFT** | Show last notification from history |
| **Double-click RIGHT** | Hide notification immediately |

- **Only active when Stealth Mode is ON** - Disabled when capture stops
- Detects on **button release** (not press) - Avoids confusion with hold
- **Notification History** - Stores up to 10 recent results
- Secure - Others can't see results immediately

### 🤖 AI Analysis
- Google Gemini API (2.5-flash default)
- **6 Optimized Prompt Templates**:
  - 📝 General Analysis
  - 🔍 Code Review  
  - ✅ Answer Questions
  - 📄 Text Extraction (OCR)
  - 🔐 Explain Technical
  - 🌐 Translate (Vietnamese ↔ English)
- Custom prompts or use templates
- **Hot-switch model** while running (no restart needed)

### 🎤 Audio Transcription (Optional)
- Azure Speech-to-Text
- Record directly or upload file
- Real-time transcription from microphone

### 🔄 File Converter (Optional)
- 49+ formats via CloudConvert API
- Supports: Audio, Image, Document, Video

---

## 🚀 Installation

### System Requirements
- Windows 10/11
- Python 3.10+ (recommended 3.12+)
- Administrator privileges (for Stealth Mode)

### Quick Installation

```powershell
# Clone repository
git clone https://github.com/QuangNew/SnapCapAI.git
cd SnapCapAI

# Install dependencies
pip install -r requirements.txt

# Run application (auto-requests Admin rights)
python gui_app.py
```

---

## 🔑 API Keys Configuration

| Service | Required | Notes | Link |
|---------|----------|-------|------|
| **Gemini** | ✅ | Free tier only has 2.5-flash | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| Azure Speech | ❌ | For audio transcription | [portal.azure.com](https://portal.azure.com) |
| CloudConvert | ❌ | For file conversion | [cloudconvert.com](https://cloudconvert.com/dashboard/api/v2/keys) |

---

## 🎮 Usage

### Basic Usage
1. Enter Gemini API Key → **Save All Credentials**
2. Select model: `gemini-2.5-flash` (recommended for free tier)
3. Click **"▶ ENGAGE STEALTH MODE"**
4. Press **PrtSc** to capture screenshot
5. Wait 5s or capture more (max 10 images)
6. AI automatically analyzes and shows results

### 🖱️ Notification Controls
| Action | Function |
|--------|----------|
| **Double-click LEFT** (0.5s) | Show last notification again |
| **Double-click RIGHT** (0.5s) | Hide notification immediately |
| Automatic | Notification auto-hides after set duration |

### Operation Modes
| Status | Color | Description |
|--------|-------|-------------|
| 👑 Admin Mode | 🟢 Green | Full Stealth Mode, PrtSc swallowed |
| ⚠️ Standard Mode | 🟡 Yellow | Fallback (pynput), may be detectable |

### Notification Customization
- **Theme:** ⬜ White / ⬛ Dark (dim text for stealth)
- **Duration:** 1s - 10s
- **Width:** 600px (clear display)

---

## 🔧 Build EXE

Create executable file (.exe) to use without Python:

```powershell
# Method 1: Batch file (recommended)
.\setup-and-build.bat

# Method 2: Manual build
pip install pyinstaller
pyinstaller SnapCapAI.spec --clean
```

**Output**: `dist\SnapCapAI.exe`

---

## 📁 Project Structure

```
SnapCapAI/
├── gui_app.py                      # Main application
├── config.json                     # Saved settings & API keys
├── requirements.txt                # Python dependencies
├── SnapCapAI.spec                  # PyInstaller spec
├── setup-and-build.bat             # Build script
├── src/                            # Source modules
│   ├── __init__.py
│   ├── keyboard_hook_manager.py    # Low-level keyboard hook (WH_KEYBOARD_LL)
│   ├── hud_notification.py         # HUD overlay (WS_EX_NOACTIVATE)
│   ├── resource_manager.py         # Context managers, SafeFileWriter
│   ├── audio_handler.py            # Azure Speech integration
│   ├── cloudconvert_handler.py     # CloudConvert API wrapper
│   ├── universal_converter.py      # Multi-format converter
│   └── convert_ui_compact.py       # Converter UI
└── temp/                           # Output folders
    ├── audio/
    ├── image/
    ├── document/
    ├── video/
    └── speechtotext_output/
```

---

## ❓ Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| PrtSc not detected | No Admin privileges | Right-click → Run as Administrator |
| "429 Quota exceeded" | Free tier quota exhausted | Wait for reset (1 min for RPM, 24h for RPD) |
| "429 Rate limit" | Sent over 5 requests/minute | Wait 1 minute and try again |
| HUD steals focus | Old Windows bug | Restart app, check Windows 10/11 |
| API Error | Wrong or expired key | Verify API key |
| Model not changing | Old bug (fixed) | Update to latest code |
| Double-click not working | Holding button too long | Click twice quickly within 0.5s |
| Overlapping notifications | Old bug (fixed) | Update to latest code |

---

## 🔄 Changelog

### v1.4.0 (12/15/2025)
- ✅ **Double-click only works when capture is ON** - Disabled when capture stops
- ✅ **Memory leak fix** - Clear batch screenshots and pending results on stop
- ✅ **Import optimization** - Move `time` import to top-level (avoid repeated imports every 30ms)
- ✅ **Keep temp files** - Don't delete temp folder files on app close

### v1.3.0 (12/14/2025)
- ✅ **Notification History** - Store 10 recent results
- ✅ **Double-click LEFT** (0.5s) - Show last notification
- ✅ **Double-click RIGHT** (0.5s) - Hide notification immediately
- ✅ **Smart button release detection** - Avoid confusing hold with double-click
- ✅ **Notification overlap fix** - No more overlapping
- ✅ **Wider notification** - 600px width for readability
- ✅ **6 Optimized prompts** - More detailed templates
- ✅ **Thread-safe batch timer** - Fix 5s debounce bug

### v1.2.0 (12/13/2025)
- ✅ Hot-switch model while running
- ✅ Default `gemini-2.5-flash` (free tier compatible)
- ✅ Batch capture (5s debounce, max 10 images)
- ✅ Double-click to reveal results
- ✅ Notification theme & duration settings

### v1.1.0
- ✅ HUD Notification with click-through
- ✅ Stealth Mode with keyboard hook
- ✅ Admin auto-elevation

### v1.0.0
- 🚀 Initial release

---

## 📜 License

MIT License - Free to use and modify.

---

## 👨‍💻 Author

**Built with ❤️ by QuangNew | December 2025**
