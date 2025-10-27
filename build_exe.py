"""
Script để build CapSnap AI thành file .exe
Build với CapSnapAI.spec file
"""

import os
import sys
import subprocess

def build_exe():
    """Build executable với PyInstaller sử dụng spec file"""
    
    spec_file = "CapSnapAI.spec"
    
    # Kiểm tra spec file tồn tại
    if not os.path.exists(spec_file):
        print(f"❌ Spec file not found: {spec_file}")
        return False
    
    print("=" * 60)
    print("CapSnap AI - Executable Builder")
    print("=" * 60)
    print()
    
    # Check PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    print()
    print(f"📋 Using spec file: {spec_file}")
    print("🔨 Building executable...")
    print("This may take several minutes...")
    print()
    
    # Run PyInstaller via Python module
    try:
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", spec_file],
            check=True,
            capture_output=False
        )
        
        print()
        print("=" * 60)
        print("🎉 Build successful!")
        print("📁 Location: dist\\CapSnapAI.exe")
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
