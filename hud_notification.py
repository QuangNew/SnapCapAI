"""
HUD Notification Overlay - Anti-Detection Result Display
=========================================================

A stealth notification overlay designed for displaying AI results over 
full-screen applications without triggering focus detection.

Critical Anti-Detection Features:
---------------------------------
1. WS_EX_NOACTIVATE (0x08000000): Window never becomes the active window
2. WS_EX_TRANSPARENT (0x00000020): Click-through - clicks pass to window below
3. WS_EX_TOOLWINDOW (0x00000080): Hidden from Alt+Tab and taskbar
4. WS_EX_TOPMOST (0x00000008): Always renders above all windows
5. WS_EX_LAYERED (0x00080000): Required for per-pixel alpha/transparency

Window Behavior:
- Appears instantly or with fade-in
- NEVER steals focus (browser.onblur will NOT trigger)
- Auto-destroys after exactly 3 seconds
- 85% opacity dark HUD aesthetic
- Click-through: mouse events pass to underlying window
"""

import tkinter as tk
import ctypes
from ctypes import wintypes
from typing import Optional, Literal
from datetime import datetime


class HUDNotification(tk.Toplevel):
    """
    Stealth HUD Notification Overlay.
    
    Displays AI analysis results in a game-HUD style overlay that:
    - Stays above full-screen browsers
    - NEVER steals focus (critical for anti-detection)
    - Allows click-through to underlying windows
    - Auto-dismisses after duration
    
    Usage:
        notif = HUDNotification(
            parent=root,
            title="✅ Analysis Complete",
            message="The answer is: 42",
            duration_ms=3000,
            notification_type="success"
        )
    """
    
    # ==================== WINDOWS API CONSTANTS ====================
    # Extended Window Styles (WS_EX_*)
    GWL_EXSTYLE = -20
    WS_EX_NOACTIVATE = 0x08000000    # CRITICAL: Prevents focus stealing
    WS_EX_TRANSPARENT = 0x00000020   # Click-through to window below
    WS_EX_TOOLWINDOW = 0x00000080    # Hide from taskbar and Alt+Tab
    WS_EX_TOPMOST = 0x00000008       # Always on top
    WS_EX_LAYERED = 0x00080000       # Layered window for transparency
    
    # SetWindowPos flags
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_NOACTIVATE = 0x0010
    SWP_SHOWWINDOW = 0x0040
    HWND_TOPMOST = -1
    
    # ==================== HUD COLOR THEMES ====================
    # Two preset themes: White (light) and Dark (black)
    COLOR_THEMES = {
        'white': {
            # Background - WHITE
            'bg_dark': '#FFFFFF',
            'bg_panel': '#F8F8F8',
            # Accent colors - light/faded for subtlety
            'neon_yellow': '#E6E6B3',
            'neon_green': '#B3E6CC',
            'neon_red': '#E6B3C2',
            'neon_cyan': '#B3E6E6',
            'neon_orange': '#E6D4B3',
            # Text - dark on light background
            'text_bright': '#333333',
            'text_dim': '#666666',
            # Borders
            'border': '#E0E0E0',
            'glow': '#F0F0F0',
        },
        'dark': {
            # Background - DARK
            'bg_dark': '#0D0D0D',
            'bg_panel': '#1A1A1A',
            # Accent colors - FADED/DIM on dark (hard to detect)
            'neon_yellow': '#3D3D1A',      # Very dim yellow
            'neon_green': '#1A3D2B',       # Very dim green
            'neon_red': '#3D1A26',         # Very dim red
            'neon_cyan': '#1A3D3D',        # Very dim cyan
            'neon_orange': '#3D2B1A',      # Very dim orange
            # Text - VERY DIM (barely visible, matches white theme opacity)
            'text_bright': '#4D4D4D',      # Dark gray - hard to see
            'text_dim': '#2A2A2A',         # Even darker
            # Borders
            'border': '#1F1F1F',           # Very subtle
            'glow': '#1A1A1A',             # Nearly invisible
        }
    }
    
    # Default theme (can be overridden per-instance)
    COLORS = COLOR_THEMES['white']
    
    # Notification type to color mapping
    TYPE_COLORS = {
        'success': 'neon_green',
        'error': 'neon_red',
        'info': 'neon_cyan',
        'warning': 'neon_orange',
    }
    
    TYPE_ICONS = {
        'success': '✓',
        'error': '✕',
        'info': 'ℹ',
        'warning': '⚠',
    }
    
    def __init__(
        self,
        parent: tk.Tk,
        title: str,
        message: str,
        duration_ms: int = 3000,
        notification_type: Literal["success", "error", "info", "warning"] = "success",
        width: int = 500,
        position: Literal["center", "top-center", "bottom-right"] = "top-center",
        click_through: bool = True,
        fade_in: bool = False,
        color_theme: Literal["white", "dark"] = "white"
    ):
        """
        Initialize HUD notification overlay.
        
        Args:
            parent: Parent Tk window (can be hidden)
            title: Notification title (displayed in accent color)
            message: Main message content (displayed in high-contrast)
            duration_ms: Auto-close after this many milliseconds (default: 3000 = 3s)
            notification_type: Visual style - "success", "error", "info", "warning"
            width: Notification width in pixels
            position: Screen position - "center", "top-center", "bottom-right"
            click_through: If True, mouse clicks pass through to window below
            fade_in: If True, fade in animation; otherwise instant appear
            color_theme: Color scheme - "white" (light) or "dark" (black)
        """
        super().__init__(parent)
        
        # Apply color theme
        self.COLORS = self.COLOR_THEMES.get(color_theme, self.COLOR_THEMES['white'])
        self.notification_type = notification_type
        self.duration_ms = duration_ms
        self.width = width
        self.position = position
        self.click_through = click_through
        self.fade_in = fade_in
        self.is_closing = False
        self._hwnd = None
        
        # Get accent color for this notification type
        color_key = self.TYPE_COLORS.get(notification_type, 'neon_green')
        self.accent_color = self.COLORS[color_key]
        self.icon = self.TYPE_ICONS.get(notification_type, '•')
        
        # ===== STEP 1: Configure Tkinter window properties =====
        self._setup_tkinter_window()
        
        # ===== STEP 2: Create HUD UI elements =====
        self._create_hud_ui(title, message)
        
        # ===== STEP 3: Position window on screen =====
        self._position_on_screen()
        
        # ===== STEP 4: Apply Windows extended styles (CRITICAL) =====
        self._apply_stealth_window_styles()
        
        # ===== STEP 5: Show window and start auto-dismiss timer =====
        self._show_and_start_timer()
    
    def _setup_tkinter_window(self):
        """Configure base Tkinter window properties."""
        # Remove window decorations (title bar, borders)
        self.overrideredirect(True)
        
        # Set initial opacity (0 if fading in, otherwise 90%)
        initial_alpha = 0.0 if self.fade_in else 0.90
        self.attributes('-alpha', initial_alpha)
        
        # Set topmost (backup - Windows API will also set this)
        self.attributes('-topmost', True)
        
        # Set background color
        self.configure(bg=self.COLORS['bg_dark'])
        
        # NOTE: Don't use transient() - it hides notification when parent is withdrawn
        # WS_EX_TOOLWINDOW will hide from taskbar instead
        
        # Withdraw initially to prevent flash
        self.withdraw()
    
    def _create_hud_ui(self, title: str, message: str):
        """
        Create HUD-style UI with high-contrast typography.
        
        Layout:
        ┌─────────────────────────────────────┐
        │ [accent bar - 4px height]           │
        │                                     │
        │ ✓  ANALYSIS COMPLETE     12:34:56  │
        │ ─────────────────────────────────── │
        │                                     │
        │ The answer is: 42                   │
        │                                     │
        │ (This is the AI result displayed    │
        │  in large, high-contrast text)      │
        │                                     │
        │ [countdown bar - 2px height]        │
        └─────────────────────────────────────┘
        """
        # Main container
        main_frame = tk.Frame(self, bg=self.COLORS['bg_dark'])
        main_frame.pack(fill='both', expand=True)
        
        # ===== TOP ACCENT BAR (4px) =====
        accent_bar = tk.Frame(main_frame, bg=self.accent_color, height=4)
        accent_bar.pack(fill='x', side='top')
        accent_bar.pack_propagate(False)
        
        # ===== CONTENT AREA =====
        content_frame = tk.Frame(main_frame, bg=self.COLORS['bg_dark'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=15)
        
        # ----- Header Row (Icon + Title + Timestamp) -----
        header_frame = tk.Frame(content_frame, bg=self.COLORS['bg_dark'])
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Icon + Title (left side)
        title_text = f"{self.icon}  {title}"
        title_label = tk.Label(
            header_frame,
            text=title_text,
            font=('Consolas', 14, 'bold'),
            fg=self.accent_color,
            bg=self.COLORS['bg_dark'],
            anchor='w'
        )
        title_label.pack(side='left')
        
        # Timestamp (right side)
        timestamp = datetime.now().strftime("%H:%M:%S")
        time_label = tk.Label(
            header_frame,
            text=timestamp,
            font=('Consolas', 10),
            fg=self.COLORS['text_dim'],
            bg=self.COLORS['bg_dark'],
            anchor='e'
        )
        time_label.pack(side='right')
        
        # ----- Separator Line -----
        separator = tk.Frame(content_frame, bg=self.COLORS['border'], height=1)
        separator.pack(fill='x', pady=(0, 12))
        
        # ----- Message Area (HIGH CONTRAST) -----
        # This is where the AI result is displayed
        # Use large, bold, high-contrast text for instant readability
        
        # Truncate very long messages
        max_chars = 500
        display_message = message[:max_chars] + "..." if len(message) > max_chars else message
        
        message_label = tk.Label(
            content_frame,
            text=display_message,
            font=('Segoe UI', 13, 'bold'),  # Large, bold for readability
            fg=self.COLORS['neon_yellow'],  # HIGH CONTRAST - Neon Yellow
            bg=self.COLORS['bg_dark'],
            justify='left',
            wraplength=self.width - 50,
            anchor='nw'
        )
        message_label.pack(fill='both', expand=True, pady=(0, 10))
        
        # ===== BOTTOM COUNTDOWN BAR (2px) =====
        self.countdown_frame = tk.Frame(main_frame, bg=self.accent_color, height=2)
        self.countdown_frame.pack(fill='x', side='bottom')
        self.countdown_frame.pack_propagate(False)
        
        # Store reference for countdown animation
        self._countdown_start = None
    
    def _position_on_screen(self):
        """Position the notification window on screen."""
        # Update to calculate actual dimensions
        self.update_idletasks()
        
        # Get screen dimensions - use work area to account for taskbar
        try:
            # Try to get work area (excludes taskbar)
            import ctypes
            from ctypes import wintypes
            
            class RECT(ctypes.Structure):
                _fields_ = [
                    ('left', ctypes.c_long),
                    ('top', ctypes.c_long),
                    ('right', ctypes.c_long),
                    ('bottom', ctypes.c_long)
                ]
            
            rect = RECT()
            ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)  # SPI_GETWORKAREA
            
            screen_width = rect.right - rect.left
            screen_height = rect.bottom - rect.top
            work_left = rect.left
            work_top = rect.top
        except:
            # Fallback to basic screen dimensions
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            work_left = 0
            work_top = 0
        
        # Get window dimensions - use reqheight first, then actual height
        win_width = self.width
        win_height = max(self.winfo_reqheight(), 150)  # Minimum height fallback
        
        # Calculate position based on setting
        if self.position == "center":
            x = work_left + (screen_width - win_width) // 2
            y = work_top + (screen_height - win_height) // 2
        elif self.position == "top-center":
            x = work_left + (screen_width - win_width) // 2
            y = work_top + 30  # 30px from top of work area
        elif self.position == "bottom-right":
            x = work_left + screen_width - win_width - 20  # 20px from right edge
            y = work_top + screen_height - win_height - 20  # 20px from bottom of work area
        else:
            # Default: top-center
            x = work_left + (screen_width - win_width) // 2
            y = work_top + 30
        
        # Ensure coordinates are valid
        x = max(0, x)
        y = max(0, y)
        
        # Set geometry
        self.geometry(f'{win_width}x{win_height}+{x}+{y}')
    
    def _apply_stealth_window_styles(self):
        """
        Apply Windows Extended Styles for stealth operation.
        
        CRITICAL: This is what makes the overlay undetectable!
        
        Styles applied:
        - WS_EX_NOACTIVATE: Window never receives activation (focus stays on browser)
        - WS_EX_TRANSPARENT: Click-through (optional)
        - WS_EX_TOOLWINDOW: Hidden from Alt+Tab and taskbar
        - WS_EX_TOPMOST: Always above other windows
        - WS_EX_LAYERED: Allows transparency effects
        """
        try:
            # Get the Windows handle (HWND) for this window
            # Need to call update first to ensure window is created
            self.update_idletasks()
            
            # Get HWND - for Toplevel, we need the actual window handle
            self._hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            
            if not self._hwnd:
                # Fallback: try getting handle directly
                self._hwnd = self.winfo_id()
            
            # Get current extended style
            current_style = ctypes.windll.user32.GetWindowLongW(
                self._hwnd, 
                self.GWL_EXSTYLE
            )
            
            # Build new style with stealth flags
            new_style = current_style | self.WS_EX_NOACTIVATE | self.WS_EX_TOOLWINDOW | self.WS_EX_LAYERED
            
            # Add click-through if enabled
            if self.click_through:
                new_style |= self.WS_EX_TRANSPARENT
            
            # Apply new extended style
            ctypes.windll.user32.SetWindowLongW(
                self._hwnd,
                self.GWL_EXSTYLE,
                new_style
            )
            
            # Use SetWindowPos to ensure TOPMOST without activating
            ctypes.windll.user32.SetWindowPos(
                self._hwnd,
                self.HWND_TOPMOST,  # Place at top of Z-order
                0, 0, 0, 0,         # Don't change position/size
                self.SWP_NOMOVE | self.SWP_NOSIZE | self.SWP_NOACTIVATE | self.SWP_SHOWWINDOW
            )
            
            print(f"[HUD] Stealth styles applied successfully (HWND: {self._hwnd})")
            
        except Exception as e:
            print(f"[HUD] Warning: Could not apply stealth styles: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_and_start_timer(self):
        """Show the window and start the auto-dismiss timer."""
        # Make window visible
        self.deiconify()
        
        # Lift to top (Tkinter level)
        self.lift()
        
        if self.fade_in:
            # Start fade-in animation
            self._fade_in_step(0.0)
        else:
            # Set final opacity immediately (90%)
            self.attributes('-alpha', 0.90)
        
        # Start countdown animation
        self._countdown_start = datetime.now()
        self._animate_countdown()
        
        # Schedule auto-dismiss (exactly after duration_ms)
        self.after(self.duration_ms, self._auto_dismiss)
    
    def _fade_in_step(self, current_alpha: float):
        """Perform one step of fade-in animation."""
        if self.is_closing:
            return
        
        try:
            if current_alpha < 0.90:
                new_alpha = min(current_alpha + 0.1, 0.90)
                self.attributes('-alpha', new_alpha)
                self.after(20, lambda: self._fade_in_step(new_alpha))
            # else: fade-in complete
        except tk.TclError:
            pass  # Window destroyed
    
    def _animate_countdown(self):
        """Animate the countdown bar showing time remaining."""
        if self.is_closing or self._countdown_start is None:
            return
        
        try:
            # Calculate elapsed time
            elapsed = (datetime.now() - self._countdown_start).total_seconds() * 1000
            remaining_ratio = max(0, 1.0 - (elapsed / self.duration_ms))
            
            if remaining_ratio > 0:
                # Update countdown bar width
                new_width = int(self.width * remaining_ratio)
                self.countdown_frame.configure(width=max(1, new_width))
                
                # Schedule next frame (60fps)
                self.after(16, self._animate_countdown)
        except tk.TclError:
            pass  # Window destroyed
    
    def _auto_dismiss(self):
        """Auto-dismiss callback - starts fade out then destroys window."""
        if self.is_closing:
            return
        
        self.is_closing = True
        self._fade_out_step(0.90)
    
    def _fade_out_step(self, current_alpha: float):
        """Perform one step of fade-out animation."""
        try:
            if current_alpha > 0.0:
                new_alpha = current_alpha - 0.1
                self.attributes('-alpha', max(0, new_alpha))
                self.after(25, lambda: self._fade_out_step(new_alpha))
            else:
                # Fully faded - destroy window
                self.destroy()
        except tk.TclError:
            pass  # Window already destroyed
    
    def close(self):
        """Manually close the notification with fade-out."""
        if not self.is_closing:
            self.is_closing = True
            self._fade_out_step(self.attributes('-alpha'))


# ==================== STANDALONE TEST ====================
if __name__ == "__main__":
    import time
    
    print("=" * 70)
    print("  HUD NOTIFICATION TEST - Anti-Detection Overlay")
    print("=" * 70)
    print()
    print("This test will display notifications that:")
    print("  ✓ Stay on top of all windows (including full-screen)")
    print("  ✓ NEVER steal focus (WS_EX_NOACTIVATE)")
    print("  ✓ Allow click-through (WS_EX_TRANSPARENT)")
    print("  ✓ Auto-dismiss after 3 seconds")
    print()
    print("To test anti-detection: Open a browser and watch the window.onblur event.")
    print("The notification should appear WITHOUT triggering onblur!")
    print()
    
    # Create hidden root window
    root = tk.Tk()
    root.withdraw()
    
    # Test all notification types
    tests = [
        {
            "type": "success",
            "title": "✅ Analysis Complete!",
            "message": "The AI has analyzed your screenshot.\n\nResult: The answer to the question is 42.\n\nThis notification uses WS_EX_NOACTIVATE to prevent focus stealing.",
            "position": "top-center"
        },
        {
            "type": "error", 
            "title": "❌ API Error",
            "message": "Failed to connect to Gemini API.\nPlease check your API key and internet connection.",
            "position": "center"
        },
        {
            "type": "info",
            "title": "ℹ️ Processing",
            "message": "Analyzing screenshot with gemini-2.0-flash model...\nThis may take a few seconds.",
            "position": "bottom-right"
        },
        {
            "type": "warning",
            "title": "⚠️ Low Confidence",
            "message": "The AI result may not be accurate.\nPlease verify the answer manually.",
            "position": "top-center"
        },
    ]
    
    for i, test in enumerate(tests):
        print(f"[{i+1}/{len(tests)}] Showing {test['type']} notification at {test['position']}...")
        
        HUDNotification(
            parent=root,
            title=test['title'],
            message=test['message'],
            duration_ms=3000,  # Exactly 3 seconds
            notification_type=test['type'],
            position=test['position'],
            click_through=True,
            fade_in=True
        )
        
        time.sleep(1.0)  # Stagger notifications
    
    print()
    print("All notifications created!")
    print("They will auto-dismiss after 3 seconds each.")
    print()
    print("Press Ctrl+C to exit...")
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nExiting...")
        root.destroy()
