# 🤖 SnapCapAI

**AI-Powered Screen Capture with Stealth Mode**

Chụp màn hình bằng PrtSc và phân tích bằng AI mà không làm gián đoạn ứng dụng đang chạy (browser, game, video).

---

## ✨ Tính năng

- **🕵️ Stealth Mode** - Hook keyboard cấp thấp, nuốt phím PrtSc
- **🎯 HUD Overlay** - Thông báo TopMost không chiếm focus (WS_EX_NOACTIVATE)
- **🤖 AI Analysis** - Google Gemini 2.0/2.5/3.0
- **🎤 Audio Transcription** - Azure Speech-to-Text (tùy chọn)
- **🔄 File Converter** - 49+ định dạng qua CloudConvert (tùy chọn)

---

## 🚀 Cài đặt

```powershell
# Clone
git clone <repo-url> SnapCapAI
cd SnapCapAI

# Install
pip install -r requirements.txt

# Run (tự động yêu cầu quyền Admin)
python gui_app.py
```

---

## 🔑 API Keys

| Service | Bắt buộc | Link |
|---------|----------|------|
| **Gemini** | ✅ | [makersuite.google.com](https://makersuite.google.com/app/apikey) |
| Azure Speech | ❌ | [portal.azure.com](https://portal.azure.com) |
| CloudConvert | ❌ | [cloudconvert.com](https://cloudconvert.com/dashboard/api/v2/keys) |

---

## 🎮 Sử dụng

1. Nhập Gemini API Key → **Save**
2. Click **"▶ ENGAGE STEALTH MODE"**
3. Nhấn **PrtSc** bất kỳ đâu
4. Kết quả hiện ở góc phải dưới màn hình (3 giây)

**Chế độ:**
- 👑 **Admin Mode** (xanh) - Stealth Mode đầy đủ
- ⚠️ **Standard Mode** (vàng) - Fallback, có thể bị phát hiện

---

## 🔧 Build EXE

```powershell
# Cách 1: Batch file
.\setup-and-build.bat

# Cách 2: Thủ công
pip install pyinstaller
pyinstaller SnapCapAI.spec --clean
```

Output: `dist\SnapCapAI.exe`

---

## 📁 Cấu trúc

```
SnapCapAI/
├── gui_app.py              # Main app
├── keyboard_hook_manager.py # Low-level keyboard hook
├── hud_notification.py      # HUD overlay (WS_EX_NOACTIVATE)
├── resource_manager.py      # Context managers
├── audio_handler.py         # Azure Speech
├── universal_converter.py   # CloudConvert wrapper
├── config.json             # API keys
└── requirements.txt
```

---

## ❓ Troubleshooting

| Vấn đề | Giải pháp |
|--------|-----------|
| PrtSc không detect | Chạy với quyền Admin |
| HUD chiếm focus | Kiểm tra Windows 10/11, restart app |
| API Error | Kiểm tra API key, internet |

---

## 📜 License

MIT License

---

**Built by QuangNew | December 2025**
