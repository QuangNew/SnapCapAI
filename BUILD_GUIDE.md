# 🔨 Build Guide - SnapCapAI

> Hướng dẫn build SnapCapAI thành file `.exe` độc lập

---

## 📋 Yêu cầu

- **Python**: 3.12+
- **PyInstaller**: 6.0+
- **OS**: Windows 10/11
- **RAM**: 8GB+ (recommended cho build)

---

## 🚀 Các bước build

### 1️⃣ Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Kiểm tra spec file

Đảm bảo `CapSnapAI.spec` tồn tại và có đầy đủ:
- ✅ Hiddenimports (tất cả modules)
- ✅ Data files (customtkinter assets, config.json)
- ✅ Binaries (Azure Speech DLLs)
- ✅ Icon file (`cap_ans.ico`)

### 3️⃣ Chạy build script

```bash
python build_exe.py
```

Build sẽ mất **5-10 phút** tùy máy.

### 4️⃣ Kết quả

File exe sẽ nằm ở:
```
dist/CapSnapAI.exe
```

Kích thước: ~150-250 MB (bao gồm tất cả dependencies)

---

## 🧪 Test executable

### Trước khi phân phối:

```bash
cd dist
.\CapSnapAI.exe
```

**Checklist:**
- [ ] App khởi động không lỗi
- [ ] Load config.json thành công
- [ ] UI hiển thị đầy đủ
- [ ] Gemini API hoạt động
- [ ] Azure Speech hoạt động
- [ ] File converter hoạt động
- [ ] System tray icon hiển thị
- [ ] Windows notification hoạt động

---

## 🐛 Troubleshooting

### ❌ Lỗi: "Failed to execute script"

**Nguyên nhân**: Thiếu DLL hoặc module

**Giải pháp**:
1. Thêm module vào `hiddenimports` trong `CapSnapAI.spec`
2. Rebuild với flag `--clean`:
   ```bash
   python -m PyInstaller CapSnapAI.spec --clean
   ```

### ❌ Lỗi: "Missing Azure DLLs"

**Nguyên nhân**: Hook không collect đủ Azure DLLs

**Giải pháp**:
1. Kiểm tra `hook-azure.cognitiveservices.speech.py`
2. Thêm manual binary copy vào spec file:
   ```python
   binaries += [('path/to/azure/dlls/*.dll', 'azure/cognitiveservices/speech')]
   ```

### ❌ Lỗi: "CustomTkinter themes not found"

**Nguyên nhân**: Data files không được copy

**Giải pháp**:
- Ensure `collect_data_files('customtkinter')` trong spec file
- Or manually add: `datas += [('venv/Lib/site-packages/customtkinter', 'customtkinter')]`

### ❌ Exe size quá lớn (>500MB)

**Giải pháp**:
1. Enable UPX compression (đã bật mặc định)
2. Xóa unnecessary modules khỏi `hiddenimports`
3. Build với `--onefile` thay vì `--onedir` (chậm hơn nhưng nhỏ hơn)

---

## 📦 Phân phối

### Standalone exe:
- Copy toàn bộ folder `dist/` hoặc chỉ `CapSnapAI.exe`
- Không cần cài Python
- Cần có internet để gọi API

### Installer (Optional):
Sử dụng [Inno Setup](https://jrsoftware.org/isinfo.php) hoặc [NSIS](https://nsis.sourceforge.io/):

```iss
[Setup]
AppName=SnapCapAI
AppVersion=1.0
DefaultDirName={pf}\SnapCapAI
DefaultGroupName=SnapCapAI
OutputBaseFilename=SnapCapAI_Setup

[Files]
Source: "dist\CapSnapAI.exe"; DestDir: "{app}"
Source: "config.json"; DestDir: "{app}"; Flags: onlyifdoesntexist

[Icons]
Name: "{group}\SnapCapAI"; Filename: "{app}\CapSnapAI.exe"
Name: "{commondesktop}\SnapCapAI"; Filename: "{app}\CapSnapAI.exe"
```

---

## 🔧 Advanced: Manual build

Nếu `build_exe.py` không hoạt động:

```bash
# Clean old builds
rmdir /s /q build dist

# Build with spec
python -m PyInstaller CapSnapAI.spec --clean --noconfirm

# Or build from scratch (not recommended)
python -m PyInstaller gui_app.py ^
  --name CapSnapAI ^
  --onefile ^
  --windowed ^
  --icon cap_ans.ico ^
  --add-data "config.json;." ^
  --hidden-import customtkinter ^
  --hidden-import azure.cognitiveservices.speech ^
  --collect-data customtkinter ^
  --collect-binaries azure.cognitiveservices.speech
```

---

## 📊 Build metrics

**Typical build time:**
- Clean build: 5-10 minutes
- Incremental: 2-4 minutes

**Typical exe size:**
- Onefile: 180-250 MB
- Onedir: 150-200 MB (multiple files)

**Memory usage during build:**
- Peak: ~2-4 GB RAM

---

## ✅ Best practices

1. **Always clean build** trước khi release
2. **Test trên máy sạch** (không có Python)
3. **Scan virus** trước khi phân phối
4. **Version tagging** trong filename: `CapSnapAI_v1.0.exe`
5. **Include README** và LICENSE trong dist folder

---

<div align="center">
  <sub>Build instructions for SnapCapAI | Last updated: 2025</sub>
</div>
