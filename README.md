# 🤖 SnapCapAI - AI Screen Capture & Analysis

**Chụp màn hình thông minh với AI - Không làm gián đoạn bất kỳ ứng dụng nào**

SnapCapAI cho phép bạn nhấn **PrtSc** để chụp màn hình và nhận kết quả phân tích AI ngay lập tức, mà không làm gián đoạn browser, game, video hay bất kỳ ứng dụng toàn màn hình nào đang chạy.

---

## ✨ Tính năng chính

### 🕵️ Stealth Mode (Chế độ ẩn)
- **Hook keyboard cấp thấp** - Chặn và xử lý phím PrtSc trước khi hệ thống nhận được
- **Không làm mất focus** - Browser/game vẫn giữ nguyên trạng thái active
- **Yêu cầu quyền Admin** để hoạt động đầy đủ

### 🎯 HUD Notification (Thông báo overlay)
- **Hiển thị trên mọi ứng dụng** - TopMost window luôn ở trên cùng
- **Không chiếm focus** - Sử dụng WS_EX_NOACTIVATE, browser.onblur không trigger
- **Click-through** - Click chuột xuyên qua thông báo tới ứng dụng bên dưới
- **Ẩn khỏi Alt+Tab** - Không xuất hiện trong danh sách cửa sổ
- **Thời gian tùy chỉnh** - Chọn từ 1-10 giây (mặc định 3 giây)
- **2 theme màu**: Trắng (Light) hoặc Đen (Dark) - cả 2 đều có chữ mờ để tránh bị phát hiện
- **Hiệu ứng fade** - Biến mất mượt mà

### 🤖 AI Analysis (Phân tích AI)
- **Google Gemini** - Hỗ trợ các model: 2.0 Flash, 2.5 Pro, 2.5 Flash
- **Prompt tùy chỉnh** - Chọn template hoặc viết prompt riêng
- **Các template có sẵn**:
  - Chỉ trả lời câu hỏi (mặc định)
  - Code Analysis
  - Translate to Vietnamese
  - Math Solver
  - Text Extraction

### 🎤 Audio Transcription (Tùy chọn)
- **Azure Speech-to-Text** - Chuyển đổi giọng nói thành văn bản
- **Ghi âm trực tiếp** từ microphone
- **Hỗ trợ nhiều ngôn ngữ** bao gồm tiếng Việt

### 🔄 File Converter (Tùy chọn)
- **CloudConvert API** - Chuyển đổi 49+ định dạng file
- **Hỗ trợ**: Audio, Image, Document (PDF, Word, Excel), Video

---

## 🚀 Cài đặt

### Yêu cầu hệ thống
- Windows 10/11
- Python 3.10+ (khuyến nghị 3.12+)
- Quyền Administrator (cho Stealth Mode)

### Cài đặt nhanh

```powershell
# Clone repository
git clone https://github.com/QuangNew/SnapCapAI.git
cd SnapCapAI

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy ứng dụng (tự động yêu cầu quyền Admin)
python gui_app.py
```

---

## 🔑 Cấu hình API Keys

| Dịch vụ | Bắt buộc | Mục đích | Đăng ký |
|---------|:--------:|----------|---------|
| **Google Gemini** | ✅ | Phân tích ảnh bằng AI | [makersuite.google.com](https://makersuite.google.com/app/apikey) |
| Azure Speech | ❌ | Chuyển giọng nói → text | [portal.azure.com](https://portal.azure.com) |
| CloudConvert | ❌ | Chuyển đổi file | [cloudconvert.com](https://cloudconvert.com/dashboard/api/v2/keys) |

> 💡 **Chỉ cần Gemini API Key** là có thể sử dụng tính năng chính (chụp & phân tích ảnh)

---

## 🎮 Hướng dẫn sử dụng

### Bước 1: Cấu hình
1. Mở ứng dụng → Nhập **Gemini API Key**
2. Click **"💾 SAVE ALL CREDENTIALS"**
3. (Tùy chọn) Chọn **Prompt Template** phù hợp
4. (Tùy chọn) Chọn **Notification Theme**: ⬜ White hoặc ⬛ Dark
5. (Tùy chọn) Chọn **Notification Duration**: ⏱️ 1s - 10s (mặc định 3s)

### Bước 2: Bắt đầu
1. Click **"▶ ENGAGE STEALTH MODE"**
2. Ứng dụng sẽ chạy ngầm và lắng nghe phím PrtSc

### Bước 3: Sử dụng
1. Mở browser/game/video bất kỳ
2. Nhấn **PrtSc** khi muốn chụp & phân tích
3. Kết quả hiển thị ở góc **phải dưới màn hình**
4. Tiếp tục làm việc - không cần chuyển cửa sổ

### Bước 4: Thu nhỏ
- Click **"🔽 MINIMIZE TO TRAY"** để ẩn vào khay hệ thống
- Click icon ở khay để mở lại

---

## 📊 Chế độ hoạt động

| Chế độ | Biểu tượng | Mô tả | Yêu cầu |
|--------|:----------:|-------|---------|
| **Admin Mode** | 👑 Xanh | Stealth Mode đầy đủ, hook keyboard cấp thấp | Chạy với quyền Admin |
| **Standard Mode** | ⚠️ Vàng | Fallback dùng pynput, có thể bị phát hiện | Không cần Admin |

> ⚠️ **Khuyến nghị**: Luôn chạy với quyền Admin để có trải nghiệm tốt nhất

---

## 🔧 Build EXE

Tạo file thực thi (.exe) để sử dụng không cần Python:

```powershell
# Cách 1: Sử dụng batch file
.\setup-and-build.bat

# Cách 2: Build thủ công
pip install pyinstaller
pyinstaller SnapCapAI.spec --clean
```

**Output**: `dist\SnapCapAI.exe`

---

## 📁 Cấu trúc dự án

```
SnapCapAI/
├── gui_app.py              # Ứng dụng chính (GUI)
├── keyboard_hook_manager.py # Hook keyboard cấp thấp (Windows API)
├── hud_notification.py      # HUD overlay (WS_EX_NOACTIVATE)
├── resource_manager.py      # Quản lý tài nguyên (context managers)
├── audio_handler.py         # Xử lý ghi âm + Azure Speech
├── cloudconvert_handler.py  # Wrapper cho CloudConvert API
├── universal_converter.py   # Chuyển đổi file đa định dạng
├── config.json             # Lưu API keys và cài đặt
├── requirements.txt        # Dependencies
├── SnapCapAI.spec          # PyInstaller config
├── setup-and-build.bat     # Script build tự động
└── temp/                   # Folder chứa file tạm
    ├── audio/
    ├── image/
    ├── document/
    └── video/
```

---

## ❓ Xử lý sự cố

| Vấn đề | Nguyên nhân | Giải pháp |
|--------|-------------|-----------|
| PrtSc không hoạt động | Thiếu quyền Admin | Chạy lại với quyền Administrator |
| Thông báo không hiện | Window bị ẩn | Restart ứng dụng, kiểm tra Windows 10/11 |
| "API Error" | Key sai hoặc hết quota | Kiểm tra API key, internet connection |
| App bị treo | Xử lý ảnh lớn | Chờ xử lý xong, kiểm tra console |
| Build EXE lỗi | Thiếu module | Chạy `pip install -r requirements.txt` |

---

## 🔒 Bảo mật

- API keys được lưu cục bộ trong `config.json`
- Không gửi dữ liệu đến server ngoại trừ API của Google/Azure/CloudConvert
- Ảnh chụp màn hình chỉ tồn tại trong RAM, không lưu file

---

## 🛠️ Công nghệ sử dụng

- **Python 3.12+** - Ngôn ngữ chính
- **CustomTkinter** - Modern UI framework
- **ctypes + Windows API** - Low-level keyboard hook
- **Google Generative AI** - Gemini models
- **Azure Cognitive Services** - Speech-to-Text
- **CloudConvert** - File conversion
- **Pillow** - Image processing
- **PyInstaller** - Build executable

---

## 📜 License

MIT License - Tự do sử dụng và chỉnh sửa

---

## 👨‍💻 Tác giả

**QuangNew** | December 2025

[![GitHub](https://img.shields.io/badge/GitHub-QuangNew-black?style=flat-square&logo=github)](https://github.com/QuangNew)
