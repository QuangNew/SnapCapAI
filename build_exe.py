"""
Script để build CapSnap AI thành file .exe
Build với CapSnapAI.spec file
"""

import os
import sys
import subprocess
import shutil

def clean_build():
    """Dọn dẹp các folder build cũ"""
    folders_to_clean = ['build', 'dist']
    for folder in folders_to_clean:
        if os.path.exists(folder):
            print(f"🗑️  Cleaning {folder}/...")
            shutil.rmtree(folder)
    print()

def build_exe():
    """Build executable với PyInstaller sử dụng spec file"""
    
    spec_file = "CapSnapAI.spec"
    
    # Kiểm tra spec file tồn tại
    if not os.path.exists(spec_file):
        print(f"❌ Spec file not found: {spec_file}")
        return False
    
    print("=" * 60)
    print("🤖 CapSnap AI - Executable Builder")
    print("=" * 60)
    print()
    
    # Check PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller found: v{PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed")
    
    print()
    
    # Clean old builds
    clean_build()
    
    print(f"📋 Using spec file: {spec_file}")
    print("🔨 Building executable...")
    print("⏳ This may take several minutes...")
    print()
    print("-" * 60)
    
    # Run PyInstaller via Python module
    try:
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", spec_file, "--clean"],
            check=True,
            capture_output=False
        )
        
        print("-" * 60)
        print()
        print("=" * 60)
        print("🎉 Build successful!")
        print("=" * 60)
        print()
        
        # Check exe file
        exe_path = os.path.join("dist", "CapSnapAI.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"� Executable: {exe_path}")
            print(f"💾 Size: {size_mb:.2f} MB")
            print()
            print("✅ You can now run: dist\\CapSnapAI.exe")
        else:
            print("⚠️  Warning: Exe file not found in expected location")
        
        print("=" * 60)
        return True
        
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("❌ Build failed!")
        print(f"Error: {e}")
        print("=" * 60)
        return False
    except FileNotFoundError:
        print()
        print("=" * 60)
        print("❌ PyInstaller not found in PATH!")
        print("💡 Try: pip install pyinstaller")
        print("=" * 60)
        return False
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Unexpected error!")
        print(f"Error: {e}")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)
