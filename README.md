# 🤖 SnapCapAI

AI-Powered Screen Capture with Stealth Mode - Capture screenshots using PrtSc and analyze them with AI.

---

## ✨ Features

### 🕵️ Stealth Mode
- Swallows PrtSc key - won't interrupt games/videos
- Requires Administrator privileges

### 📸 Smart Capture
- Batch capture (max 10 images, 5s debounce)
- HUD overlay notification (click-through, 2 themes)
- Double-click LEFT: Show last result | RIGHT: Hide notification

### 🤖 AI Analysis
- Google Gemini API (gemini-2.5-flash default)
- 6 prompt templates: General, Code Review, OCR, Translation, etc.
- Hot-switch model while running

### Optional Features
- 🎤 Audio Transcription (Azure Speech-to-Text)
- 🔄 File Converter (49+ formats via CloudConvert)

---

## 🚀 Installation

**Requirements:** Windows 10/11, Python 3.10+, Admin privileges

```powershell
git clone https://github.com/QuangNew/SnapCapAI.git
cd SnapCapAI
pip install -r requirements.txt
python gui_app.py  # Auto-requests Admin rights
```

---

## 🔑 API Keys

- **Gemini** (Required): [Get API Key](https://aistudio.google.com/app/apikey) - Free tier: 5 req/min, 25 req/day
- Azure Speech (Optional): For audio transcription
- CloudConvert (Optional): For file conversion

---

## 🎮 Usage

1. Enter Gemini API Key → Save
2. Select `gemini-2.5-flash` model
3. Click **"▶ ENGAGE STEALTH MODE"**
4. Press **PrtSc** to capture
5. AI analyzes and shows results

**Controls:**
- Double-click LEFT: Show last result
- Double-click RIGHT: Hide notification

---

## 🔧 Build EXE

```powershell
.\setup-and-build.bat          # Output: dist\SnapCapAI.exe
.\build-installer.bat          # Output: Output\SnapCapAI-Setup.exe
```

**Requirements:** [Inno Setup 6](https://jrsoftware.org/isdl.php) for installer

---



## ❓ Troubleshooting

- **PrtSc not working**: Run as Administrator
- **"429 Rate limit"**: Wait 1 minute (free tier: 5 req/min)
- **API Error**: Check API key validity

---



## 📜 License

MIT License - Free to use and modify.

---

## 👨‍💻 Author

**Built with ❤️ by QuangNew | December 2025**
