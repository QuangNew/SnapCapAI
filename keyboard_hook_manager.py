"""
Windows Low-Level Keyboard Hook Manager
Compatible with Python 3.14+

CRITICAL: This module MUST be imported BEFORE pynput, as pynput breaks ctypes.WINFUNCTYPE
"""

import ctypes
import ctypes.wintypes as wintypes
from ctypes import POINTER, byref, c_int, c_void_p
import threading
import time
from typing import Callable


# Windows API Constants
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105
VK_SNAPSHOT = 0x2C  # Print Screen key
PM_REMOVE = 0x0001

# Load DLLs
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Configure CallNextHookEx properly for Python 3.14
# lParam needs to be c_void_p to handle large pointers
user32.CallNextHookEx.argtypes = [wintypes.HHOOK, c_int, wintypes.WPARAM, c_void_p]
user32.CallNextHookEx.restype = c_int


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", POINTER(wintypes.ULONG))
    ]


# Global state
_hook_manager = None


class KeyboardHookManager:
    """Low-level Windows keyboard hook for intercepting PrtSc."""
    
    def __init__(self, callback: Callable[[], None]):
        self.callback = callback
        self.hook_id = None
        self._running = False
        self._thread = None
        self._hook_proc = None
        self._prtsc_down = False
    
    def _hook_callback(self, nCode, wParam, lParam):
        """
        Keyboard hook callback.
        Returns int (not c_long) to avoid conversion errors.
        """
        try:
            if nCode >= 0:
                # Cast lParam to pointer to KBDLLHOOKSTRUCT
                kbd = ctypes.cast(lParam, POINTER(KBDLLHOOKSTRUCT)).contents
                
                if kbd.vkCode == VK_SNAPSHOT:
                    # Handle key down - trigger callback once
                    if wParam in (WM_KEYDOWN, WM_SYSKEYDOWN):
                        if not self._prtsc_down:
                            self._prtsc_down = True
                            if self.callback:
                                threading.Thread(target=self.callback, daemon=True).start()
                    elif wParam in (WM_KEYUP, WM_SYSKEYUP):
                        self._prtsc_down = False
                    
                    # SWALLOW the key - return 1, don't call next hook
                    return 1
        except Exception as e:
            print(f"Hook error: {e}")
        
        # Pass other keys through - cast lParam to c_void_p for Python 3.14 compatibility
        return user32.CallNextHookEx(self.hook_id, nCode, wParam, c_void_p(lParam))
    
    def _run_hook(self):
        """Install hook and run message loop."""
        global _hook_manager
        _hook_manager = self
        
        # Create HOOKPROC type - return type is c_int for Python compatibility
        HOOKPROC = ctypes.WINFUNCTYPE(c_int, c_int, wintypes.WPARAM, wintypes.LPARAM)
        
        # Create and store callback reference
        self._hook_proc = HOOKPROC(self._hook_callback)
        
        kernel32.SetLastError(0)
        
        self.hook_id = user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            self._hook_proc,
            None,
            0
        )
        
        if not self.hook_id:
            error = kernel32.GetLastError()
            _hook_manager = None
            raise RuntimeError(f"Hook failed. Error: {error}. Run as Admin.")
        
        print(f"✅ Keyboard hook installed: {self.hook_id}")
        
        # Message loop
        msg = wintypes.MSG()
        while self._running:
            if user32.PeekMessageW(byref(msg), None, 0, 0, PM_REMOVE):
                user32.TranslateMessage(byref(msg))
                user32.DispatchMessageW(byref(msg))
            else:
                time.sleep(0.001)
        
        # Cleanup
        if self.hook_id:
            user32.UnhookWindowsHookEx(self.hook_id)
            print("✅ Keyboard hook removed")
            self.hook_id = None
        
        _hook_manager = None
    
    def start(self):
        """Start the keyboard hook."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(
            target=self._run_hook,
            daemon=True,
            name="KeyboardHookThread"
        )
        self._thread.start()
        
        time.sleep(0.3)
        
        if not self.hook_id:
            self._running = False
            raise RuntimeError(
                "Keyboard hook failed to initialize.\n"
                "1. Run as Administrator\n"
                "2. Check if another app is blocking hooks"
            )
    
    def stop(self):
        """Stop the keyboard hook."""
        global _hook_manager
        
        if not self._running:
            return
        
        self._running = False
        
        if self._thread:
            self._thread.join(timeout=2.0)
        
        if self.hook_id:
            user32.UnhookWindowsHookEx(self.hook_id)
            self.hook_id = None
        
        _hook_manager = None
    
    def is_running(self) -> bool:
        return self._running and self.hook_id is not None
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args):
        self.stop()
        return False
