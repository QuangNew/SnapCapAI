# 🤖 SnapCapAI - Screen Capture & AI Analyzer

> **Công cụ chụp màn hình thông minh với AI phân tích hình ảnh, chuyển đổi giọng nói và convert file đa năng.**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://windows.com)

---

## 🌟 Tính năng chính

### 📸 **Image Analysis (Gemini AI)**
- Chụp màn hình bằng phím **PrtSc** (Print Screen)
- Phân tích hình ảnh tự động với Gemini AI
- Hỗ trợ nhiều prompt template:
  - Giải bài tập, trả lời câu hỏi
  - Phân tích code, tìm bug
  - Dịch văn bản, giải toán
  - Trích xuất text từ ảnh

### 🎤 **Audio Transcription (Azure Speech)**
- Ghi âm trực tiếp từ microphone
- Chuyển đổi file audio sang text
- Hỗ trợ realtime transcription
- Lưu kết quả tự động vào `temp/speechtotext_output/`
- Định dạng: WAV, MP3, M4A, FLAC

### 🔄 **Universal File Converter (CloudConvert)**
- **4 categories** - **49+ formats**
- **Audio**: MP3, WAV, AAC, OGG, FLAC, M4A...
- **Image**: JPG, PNG, WEBP, GIF, SVG, HEIC...
- **Document**: PDF, DOCX, XLSX, PPTX, TXT...
- **Video**: MP4, AVI, MKV, MOV, WEBM...
- Output tự động: `temp/{category}/`

---

## 📦 Cài đặt & Build

### 🚀 **Quick Start (Windows)**

**Build EXE tự động:**
```bash
setup-and-build.bat
```

Script sẽ:
- ✅ Check Python (3.12+)
- ✅ Cài tất cả dependencies
- ✅ Build thành file `dist/CapSnapAI.exe`
- ⏱️ Thời gian: ~10-15 phút

**Hoặc manual:**
```bash
pip install -r requirements.txt
python gui_app.py
```

### 3️⃣ Cấu hình API Keys
Tạo file `config.json` hoặc nhập trực tiếp trong app:

```json
{
  "api_key": "YOUR_GEMINI_API_KEY",
  "azure_api_key": "YOUR_AZURE_SPEECH_KEY",
  "azure_region": "southeastasia",
  "cloudconvert_api_key": "YOUR_CLOUDCONVERT_TOKEN",
  "gemini_model": "gemini-2.0-flash"
}
```

#### 🔑 API Keys:
- **Gemini** *(Required)*: [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Azure Speech** *(Optional)*: [Azure Portal](https://portal.azure.com) → Cognitive Services → Speech
- **CloudConvert** *(Optional)*: [CloudConvert Dashboard](https://cloudconvert.com/dashboard/api/v2/keys)

---

## 🚀 Sử dụng

### Chạy từ source:
```bash
python gui_app.py
```

### Build thành EXE:
```bash
setup-and-build.bat
```

File exe sẽ ở: `dist/CapSnapAI.exe`

---

## 💡 Hướng dẫn sử dụng

### 📸 Chụp & Phân tích ảnh:
1. Nhập **Gemini API Key**
2. Chọn **Prompt Template** hoặc tạo custom prompt
3. Click **Start Listening**
4. Nhấn **PrtSc** để chụp màn hình
5. Kết quả hiển thị trong tab **Image Analysis**

### 🎤 Chuyển đổi Audio:
1. Nhập **Azure Speech API Key** và chọn **Region** *(Optional)*
2. **Start Recording**: Ghi âm từ mic
3. **Stop Recording**: Dừng và tự động chuyển đổi
4. **Upload File**: Chọn file audio có sẵn
5. **Realtime**: Lắng nghe realtime (30s)

> **Note**: Tính năng này cần Azure Speech API Key (optional)

### 🔄 Convert File:
1. Click **Browse** → Chọn file
2. Chọn **Category** và **Format**
3. Click **Convert**
4. File output: `temp/{category}/`

> **Note**: Tính năng này cần CloudConvert API Key (optional)

---

## 📂 Cấu trúc dự án

```
SnapCapAI/
├── gui_app.py                 # Main GUI application
├── audio_handler.py           # Azure Speech integration
├── cloudconvert_handler.py    # CloudConvert API wrapper
├── universal_converter.py     # Universal file converter
├── build_exe.py              # Executable builder script
├── CapSnapAI.spec            # PyInstaller spec file
├── hook-azure.*.py           # PyInstaller hooks
├── requirements.txt          # Python dependencies
├── config.json              # Configuration file (auto-created)
└── temp/                    # Output folder
    ├── audio/
    ├── image/
    ├── video/
    ├── document/
    └── speechtotext_output/
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **GUI** | CustomTkinter |
| **AI Vision** | Google Gemini 2.0 |
| **Speech-to-Text** | Azure Cognitive Services |
| **File Conversion** | CloudConvert API |
| **Hotkey** | pynput |
| **Notification** | winotify |
| **System Tray** | pystray |

---

## ⚙️ Requirements

- **Python**: 3.12+
- **OS**: Windows 10/11
- **RAM**: 4GB minimum
- **Internet**: Required (API calls)

---

## 🐛 Troubleshooting

### ❌ Lỗi "API Key not found"
→ Kiểm tra `config.json` hoặc nhập lại API key trong app

### ❌ Lỗi Azure Speech connection
→ Verify API key và region (ví dụ: `southeastasia`)

### ❌ Build exe thất bại
→ Chạy: `pip install --upgrade pyinstaller`

### ❌ Thiếu DLL khi chạy exe
→ Cài Visual C++ Redistributable: [Download](https://aka.ms/vs/17/release/vc_redist.x64.exe)

---

## 📝 License

MIT License - See [LICENSE](LICENSE) for details

---

## 👨‍💻 Author

**QuangNew**
- GitHub: [@QuangNew](https://github.com/QuangNew)

---

## 🙏 Credits

- [Google Gemini AI](https://ai.google.dev/)
- [Azure Cognitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/)
- [CloudConvert](https://cloudconvert.com/)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)

---

<div align="center">
  <sub>Built with ❤️ by QuangNew</sub>
</div>