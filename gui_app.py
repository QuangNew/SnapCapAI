"""
SnapCapAI - AI-Powered Screen Capture & Analysis
Cyber Liquid Glass UI - Neon Cyberpunk + Glassmorphism Design
"""

import os
import io
import json
import shutil
import subprocess
import threading
import sys
import ctypes
import queue
import time
import tkinter as tk
import customtkinter as ctk
from datetime import datetime
from PIL import ImageGrab, Image, ImageTk
import google.generativeai as genai
from tkinter import scrolledtext, messagebox, filedialog, simpledialog
import pystray
from pystray import MenuItem as item
from src.audio_handler import AudioHandler
from src.cloudconvert_handler import CloudConvertHandler
from src.universal_converter import UniversalConverter
from src.keyboard_hook_manager import KeyboardHookManager
from src.hud_notification import HUDNotification
from src.resource_manager import screenshot_context, SafeFileWriter

# NOTE: pynput import is LAZY - only when needed as fallback
PYNPUT_AVAILABLE = False
pynput_keyboard = None


def _import_pynput():
    """Lazy import pynput to avoid breaking ctypes keyboard hook."""
    global PYNPUT_AVAILABLE, pynput_keyboard
    if pynput_keyboard is None:
        try:
            from pynput import keyboard as pk
            pynput_keyboard = pk
            PYNPUT_AVAILABLE = True
        except ImportError:
            PYNPUT_AVAILABLE = False
    return PYNPUT_AVAILABLE


def is_admin():
    """Check if running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """Restart with administrator privileges."""
    try:
        if sys.argv[0].endswith('.py'):
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable,
                f'"{os.path.abspath(sys.argv[0])}"', None, 1
            )
        else:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable,
                " ".join(sys.argv), None, 1
            )
        return True
    except Exception as e:
        print(f"Failed to elevate privileges: {e}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
# CYBER LIQUID GLASS THEME - Design System
# ══════════════════════════════════════════════════════════════════════════════
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CyberGlassTheme:
    """
    Cyber Liquid Glass Design System
    Combines Cyberpunk neon aesthetics with modern glassmorphism
    """
    
    # ═══════════════ COLORS ═══════════════
    # Dark backgrounds - good contrast
    BG_VOID = "#0d1117"           # Main background (GitHub dark)
    BG_DARK = "#161b22"           # Secondary background
    BG_PANEL = "#1c2128"          # Panel/card background
    BG_SURFACE = "#22272e"        # Elevated surface
    BG_INPUT = "#2d333b"          # Input field background
    
    # Glass effects 
    GLASS_BG = "#21262d"          # Glass panel bg
    GLASS_BORDER = "#444c56"      # Glass border - more visible
    GLASS_HIGHLIGHT = "#545d68"   # Glass highlight/hover
    
    # Neon accent colors
    NEON_CYAN = "#58a6ff"         # Primary accent - softer blue
    NEON_MAGENTA = "#d2a8ff"      # Secondary accent - soft purple
    NEON_GREEN = "#3fb950"        # Success/Active state
    NEON_PURPLE = "#a371f7"       # Tertiary accent
    NEON_ORANGE = "#d29922"       # Warning/CTA
    NEON_RED = "#f85149"          # Error/Danger
    NEON_BLUE = "#58a6ff"         # Info accent
    
    # Text colors - HIGH CONTRAST
    TEXT_PRIMARY = "#f0f6fc"      # Primary text - bright
    TEXT_SECONDARY = "#b1bac4"    # Secondary text - very readable
    TEXT_DIM = "#8b949e"          # Disabled/hint - still visible
    TEXT_GLOW = "#ffffff"         # Text with glow effect
    
    # Gradient definitions (for manual gradient implementation)
    GRADIENT_CYBER = ("#58a6ff", "#a371f7")  # Blue to Purple
    GRADIENT_NEON = ("#3fb950", "#58a6ff")   # Green to Blue
    GRADIENT_PURPLE = ("#a371f7", "#d2a8ff") # Purple shades
    
    # Status colors
    STATUS_ONLINE = "#3fb950"
    STATUS_OFFLINE = "#8b949e"
    STATUS_WARNING = "#d29922"
    STATUS_ERROR = "#f85149"
    
    # Spacing & Sizing
    SPACING_XS = 4
    SPACING_SM = 6
    SPACING_MD = 12
    SPACING_LG = 16
    SPACING_XL = 24
    
    RADIUS_SM = 6
    RADIUS_MD = 8
    RADIUS_LG = 10
    RADIUS_XL = 12
    RADIUS_FULL = 9999
    
    # Animation timing (ms)
    ANIM_FAST = 100
    ANIM_NORMAL = 200
    ANIM_SLOW = 300


# Create theme instance
THEME = CyberGlassTheme()


class GlassFrame(ctk.CTkFrame):
    """
    Custom glass panel with neon border glow effect
    Simulates glassmorphism in CustomTkinter
    """
    
    def __init__(self, parent, glow_color=None, **kwargs):
        # Default glass styling
        kwargs.setdefault('fg_color', THEME.BG_PANEL)
        kwargs.setdefault('corner_radius', THEME.RADIUS_MD)
        kwargs.setdefault('border_width', 1)
        kwargs.setdefault('border_color', glow_color or THEME.GLASS_BORDER)
        
        super().__init__(parent, **kwargs)
        self._glow_color = glow_color


class NeonButton(ctk.CTkButton):
    """
    Neon-styled button with glow effect
    """
    
    def __init__(self, parent, neon_color=THEME.NEON_CYAN, variant="solid", **kwargs):
        self._neon_color = neon_color
        self._variant = variant
        
        if variant == "solid":
            kwargs.setdefault('fg_color', neon_color)
            kwargs.setdefault('hover_color', self._darken_color(neon_color))
            kwargs.setdefault('text_color', THEME.BG_VOID)
        elif variant == "outline":
            kwargs.setdefault('fg_color', "transparent")
            kwargs.setdefault('hover_color', THEME.BG_INPUT)
            kwargs.setdefault('text_color', neon_color)
            kwargs.setdefault('border_width', 2)
            kwargs.setdefault('border_color', neon_color)
        elif variant == "ghost":
            kwargs.setdefault('fg_color', "transparent")
            kwargs.setdefault('hover_color', THEME.BG_SURFACE)
            kwargs.setdefault('text_color', neon_color)
        
        kwargs.setdefault('corner_radius', THEME.RADIUS_SM)
        kwargs.setdefault('font', ctk.CTkFont(size=13, weight="bold"))
        
        super().__init__(parent, **kwargs)
    
    def _darken_color(self, hex_color, factor=0.7):
        """Darken a hex color"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = int(r * factor), int(g * factor), int(b * factor)
        return f'#{r:02x}{g:02x}{b:02x}'


class NeonEntry(ctk.CTkEntry):
    """
    Neon-styled input field with glow border
    """
    
    def __init__(self, parent, accent_color=THEME.NEON_CYAN, **kwargs):
        kwargs.setdefault('fg_color', THEME.BG_INPUT)
        kwargs.setdefault('border_color', THEME.GLASS_BORDER)
        kwargs.setdefault('text_color', THEME.TEXT_PRIMARY)
        kwargs.setdefault('placeholder_text_color', THEME.TEXT_DIM)
        kwargs.setdefault('corner_radius', THEME.RADIUS_SM)
        kwargs.setdefault('height', 36)
        
        super().__init__(parent, **kwargs)
        self._accent_color = accent_color
        
        # Bind focus events for glow effect
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, event):
        self.configure(border_color=self._accent_color)
    
    def _on_focus_out(self, event):
        self.configure(border_color=THEME.GLASS_BORDER)


class NeonComboBox(ctk.CTkComboBox):
    """
    Neon-styled combo box
    """
    
    def __init__(self, parent, accent_color=THEME.NEON_CYAN, **kwargs):
        kwargs.setdefault('fg_color', THEME.BG_INPUT)
        kwargs.setdefault('border_color', THEME.GLASS_BORDER)
        kwargs.setdefault('button_color', accent_color)
        kwargs.setdefault('button_hover_color', THEME.BG_SURFACE)
        kwargs.setdefault('dropdown_fg_color', THEME.BG_PANEL)
        kwargs.setdefault('dropdown_hover_color', THEME.BG_SURFACE)
        kwargs.setdefault('text_color', THEME.TEXT_PRIMARY)
        kwargs.setdefault('corner_radius', THEME.RADIUS_SM)
        kwargs.setdefault('height', 34)
        
        super().__init__(parent, **kwargs)


class NeonTextbox(ctk.CTkTextbox):
    """
    Neon-styled textbox with glass effect
    """
    
    def __init__(self, parent, accent_color=THEME.NEON_CYAN, **kwargs):
        kwargs.setdefault('fg_color', THEME.BG_INPUT)
        kwargs.setdefault('border_color', THEME.GLASS_BORDER)
        kwargs.setdefault('text_color', THEME.TEXT_PRIMARY)
        kwargs.setdefault('corner_radius', THEME.RADIUS_SM)
        kwargs.setdefault('border_width', 1)
        
        super().__init__(parent, **kwargs)


class NeonLabel(ctk.CTkLabel):
    """
    Styled label with good contrast
    """
    
    def __init__(self, parent, variant="normal", **kwargs):
        if variant == "title":
            kwargs.setdefault('font', ctk.CTkFont(size=20, weight="bold"))
            kwargs.setdefault('text_color', THEME.NEON_CYAN)
        elif variant == "subtitle":
            kwargs.setdefault('font', ctk.CTkFont(size=13, weight="bold"))
            kwargs.setdefault('text_color', THEME.TEXT_PRIMARY)
        elif variant == "caption":
            kwargs.setdefault('font', ctk.CTkFont(size=12))
            kwargs.setdefault('text_color', THEME.TEXT_SECONDARY)
        elif variant == "section":
            kwargs.setdefault('font', ctk.CTkFont(size=12, weight="bold"))
            kwargs.setdefault('text_color', THEME.NEON_CYAN)
        else:
            kwargs.setdefault('font', ctk.CTkFont(size=12))
            kwargs.setdefault('text_color', THEME.TEXT_PRIMARY)
        
        super().__init__(parent, **kwargs)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

class ScreenCaptureGUI(ctk.CTk):
    """
    SnapCapAI - Cyber Liquid Glass Edition
    """
    
    def __init__(self):
        super().__init__()
        
        # ═══════════ CONFIG DEFAULTS ═══════════
        self.api_key = ""
        self.azure_api_key = ""
        self.azure_region = "southeastasia"
        self.cloudconvert_api_key = ""
        self.gemini_model = "gemini-2.5-flash"
        self.current_prompt = ""
        self.window_width = 1100
        self.window_height = 700
        self.notification_theme = "dark"
        self.notification_duration = 3
        
        # Load config
        self.load_config()
        
        # ═══════════ WINDOW SETUP ═══════════
        self.title("SnapCapAI")
        self.geometry(f"{self.window_width}x{self.window_height}")
        self.minsize(900, 600)
        self.configure(fg_color=THEME.BG_VOID)
        
        # ═══════════ STATE VARIABLES ═══════════
        self.is_running = False
        self.is_processing = False
        self.is_recording = False
        self.keyboard_hook = None
        self.pynput_listener = None
        self.stealth_mode = False
        self.history = []
        self.selected_convert_file = None
        
        # Temp folder
        self.temp_folder = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(self.temp_folder, exist_ok=True)
        
        # Handlers
        self.audio_handler = None
        self.cloudconvert_handler = None
        self.universal_converter = None
        
        # Thread-safe queues
        self._notification_queue = queue.Queue()
        self._screenshot_batch = []
        self._batch_timer = None
        self._batch_lock = threading.Lock()
        self.BATCH_DELAY_MS = 5000
        self.MAX_BATCH_SIZE = 10
        self._screenshot_request_queue = queue.Queue()
        
        # Double-click detection
        self._pending_results = queue.Queue()
        self._click_count = 0
        self._right_click_count = 0
        self.DOUBLE_CLICK_THRESHOLD = 0.5
        self._left_button_was_pressed = False
        self._right_button_was_pressed = False
        
        # Notification history
        self._notification_history = []
        self._current_notification = None
        self._current_notification_data = None
        self.MAX_NOTIFICATION_HISTORY = 10
        
        # ═══════════ BUILD UI ═══════════
        self._create_ui()
        
        # Start polling loops
        self._poll_notifications()
        self._poll_screenshot_requests()
        self._poll_double_click()
        
        # Window close protocol
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    # ══════════════════════════════════════════════════════════════════════════
    # UI CONSTRUCTION
    # ══════════════════════════════════════════════════════════════════════════
    
    def _create_ui(self):
        """Build the Cyber Liquid Glass interface"""
        
        # ═══════════ HEADER BAR ═══════════
        self._create_header()
        
        # ═══════════ MAIN CONTENT ═══════════
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        
        # Left sidebar (config)
        self._create_sidebar(main_container)
        
        # Right content (tabs)
        self._create_content_area(main_container)
        
        # ═══════════ FOOTER / ACTION BAR ═══════════
        self._create_action_bar()
    
    def _create_header(self):
        """Create the header with glassmorphism effect"""
        header = GlassFrame(self, glow_color=THEME.NEON_CYAN)
        header.pack(fill="x", padx=16, pady=(16, 12))
        
        # Inner padding
        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(fill="x", padx=16, pady=12)
        
        # Left: Logo and title
        left_section = ctk.CTkFrame(header_inner, fg_color="transparent")
        left_section.pack(side="left", fill="y")
        
        # App icon (using canvas for neon glow effect)
        icon_frame = ctk.CTkFrame(left_section, fg_color=THEME.BG_SURFACE, 
                                   corner_radius=THEME.RADIUS_SM, width=48, height=48)
        icon_frame.pack(side="left", padx=(0, 16))
        icon_frame.pack_propagate(False)
        
        icon_label = ctk.CTkLabel(icon_frame, text="S", 
                                   font=ctk.CTkFont(size=24, weight="bold"),
                                   text_color=THEME.NEON_CYAN)
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title stack
        title_stack = ctk.CTkFrame(left_section, fg_color="transparent")
        title_stack.pack(side="left", fill="y")
        
        NeonLabel(title_stack, text="SNAPCAP", variant="title").pack(anchor="w")
        
        # Subtitle with version and status
        subtitle_frame = ctk.CTkFrame(title_stack, fg_color="transparent")
        subtitle_frame.pack(anchor="w")
        
        NeonLabel(subtitle_frame, text="AI Screen Analyzer", variant="caption").pack(side="left")
        
        # Separator dot
        ctk.CTkLabel(subtitle_frame, text="  •  ", text_color=THEME.TEXT_DIM,
                     font=ctk.CTkFont(size=10)).pack(side="left")
        
        NeonLabel(subtitle_frame, text="v2.0", variant="caption").pack(side="left")
        
        # Right: Status indicators
        right_section = ctk.CTkFrame(header_inner, fg_color="transparent")
        right_section.pack(side="right", fill="y")
        
        # Admin status badge
        admin_text = "ADMIN" if is_admin() else "STANDARD"
        admin_color = THEME.NEON_GREEN if is_admin() else THEME.STATUS_WARNING
        
        admin_badge = ctk.CTkFrame(right_section, fg_color=THEME.BG_SURFACE,
                                    corner_radius=THEME.RADIUS_FULL)
        admin_badge.pack(side="right", padx=(8, 0))
        
        # Status dot
        status_dot = ctk.CTkFrame(admin_badge, fg_color=admin_color,
                                   width=8, height=8, corner_radius=4)
        status_dot.pack(side="left", padx=(12, 6), pady=8)
        
        ctk.CTkLabel(admin_badge, text=admin_text, font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=admin_color).pack(side="left", padx=(0, 12), pady=8)
        
        # Capture status
        self.status_badge = ctk.CTkFrame(right_section, fg_color=THEME.BG_SURFACE,
                                          corner_radius=THEME.RADIUS_FULL)
        self.status_badge.pack(side="right", padx=(0, 8))
        
        self.status_dot = ctk.CTkFrame(self.status_badge, fg_color=THEME.STATUS_OFFLINE,
                                        width=8, height=8, corner_radius=4)
        self.status_dot.pack(side="left", padx=(12, 6), pady=8)
        
        self.status_label = ctk.CTkLabel(self.status_badge, text="OFFLINE",
                                          font=ctk.CTkFont(size=11, weight="bold"),
                                          text_color=THEME.STATUS_OFFLINE)
        self.status_label.pack(side="left", padx=(0, 12), pady=8)
    
    def _create_sidebar(self, parent):
        """Create the left sidebar with configuration options"""
        sidebar = GlassFrame(parent, glow_color=THEME.GLASS_BORDER, width=320)
        sidebar.pack(side="left", fill="y", padx=(0, 12))
        sidebar.pack_propagate(False)
        
        # Scrollable content
        sidebar_scroll = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
        sidebar_scroll.pack(fill="both", expand=True, padx=4, pady=4)
        
        # ═══════════ API CONFIGURATION ═══════════
        self._create_api_section(sidebar_scroll)
        
        # ═══════════ MODEL & PROMPT ═══════════
        self._create_prompt_section(sidebar_scroll)
        
        # ═══════════ NOTIFICATION SETTINGS ═══════════
        self._create_notification_section(sidebar_scroll)
    
    def _create_api_section(self, parent):
        """Create API configuration section"""
        section = self._create_section(parent, "API CONFIGURATION", THEME.NEON_CYAN)
        
        # Gemini API
        gemini_group = ctk.CTkFrame(section, fg_color="transparent")
        gemini_group.pack(fill="x", pady=(0, 12))
        
        NeonLabel(gemini_group, text="Gemini API Key", variant="caption").pack(anchor="w")
        
        gemini_row = ctk.CTkFrame(gemini_group, fg_color="transparent")
        gemini_row.pack(fill="x", pady=(4, 0))
        
        self.api_entry = NeonEntry(gemini_row, placeholder_text="Enter API key...", 
                                    show="•", accent_color=THEME.NEON_CYAN)
        self.api_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        if self.api_key:
            self.api_entry.insert(0, self.api_key)
        
        self.api_show_btn = NeonButton(gemini_row, text="Show", width=60, height=40,
                                        neon_color=THEME.NEON_CYAN, variant="outline",
                                        command=self.toggle_api_visibility)
        self.api_show_btn.pack(side="right")
        
        # Model selector
        model_group = ctk.CTkFrame(section, fg_color="transparent")
        model_group.pack(fill="x", pady=(0, 12))
        
        NeonLabel(model_group, text="Model", variant="caption").pack(anchor="w")
        
        self.model_selector = NeonComboBox(
            model_group,
            values=["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-pro", 
                    "gemini-3-pro", "gemini-3-flash", "gemini-3.5-flash"],
            command=self.on_model_changed,
            accent_color=THEME.NEON_CYAN
        )
        self.model_selector.pack(fill="x", pady=(4, 0))
        self.model_selector.set(self.gemini_model)
        
        # Separator
        self._create_separator(section)
        
        # Azure Speech API (optional)
        azure_group = ctk.CTkFrame(section, fg_color="transparent")
        azure_group.pack(fill="x", pady=(0, 12))
        
        azure_header = ctk.CTkFrame(azure_group, fg_color="transparent")
        azure_header.pack(fill="x")
        NeonLabel(azure_header, text="Azure Speech", variant="caption").pack(side="left")
        ctk.CTkLabel(azure_header, text="Optional", font=ctk.CTkFont(size=10),
                     text_color=THEME.TEXT_DIM).pack(side="right")
        
        self.azure_entry = NeonEntry(azure_group, placeholder_text="Azure API key...",
                                      show="•", accent_color=THEME.NEON_PURPLE)
        self.azure_entry.pack(fill="x", pady=(4, 4))
        
        if self.azure_api_key:
            self.azure_entry.insert(0, self.azure_api_key)
        
        self.azure_region_selector = NeonComboBox(
            azure_group,
            values=["southeastasia", "eastasia", "eastus", "westus", "westeurope"],
            accent_color=THEME.NEON_PURPLE
        )
        self.azure_region_selector.pack(fill="x")
        self.azure_region_selector.set(self.azure_region)
        
        # Separator
        self._create_separator(section)
        
        # CloudConvert API (optional)
        cloud_group = ctk.CTkFrame(section, fg_color="transparent")
        cloud_group.pack(fill="x", pady=(0, 12))
        
        cloud_header = ctk.CTkFrame(cloud_group, fg_color="transparent")
        cloud_header.pack(fill="x")
        NeonLabel(cloud_header, text="CloudConvert", variant="caption").pack(side="left")
        ctk.CTkLabel(cloud_header, text="Optional", font=ctk.CTkFont(size=10),
                     text_color=THEME.TEXT_DIM).pack(side="right")
        
        self.cloudconvert_entry = NeonEntry(cloud_group, placeholder_text="CloudConvert token...",
                                             show="•", accent_color=THEME.NEON_ORANGE)
        self.cloudconvert_entry.pack(fill="x", pady=(4, 0))
        
        if self.cloudconvert_api_key:
            self.cloudconvert_entry.insert(0, self.cloudconvert_api_key)
        
        # Save button
        NeonButton(section, text="Save Credentials", neon_color=THEME.NEON_GREEN,
                   command=self.save_all_api_keys, height=36).pack(fill="x", pady=(8, 0))
    
    def _create_prompt_section(self, parent):
        """Create prompt configuration section"""
        section = self._create_section(parent, "PROMPT TEMPLATE", THEME.NEON_MAGENTA)
        
        # Template selector
        NeonLabel(section, text="Quick Templates", variant="caption").pack(anchor="w")
        
        self.prompt_selector = NeonComboBox(
            section,
            values=["Custom", "Answer Questions", "Code Analysis", 
                    "Translate to Vietnamese", "Math Solver", "Text Extraction",
                    "General Analysis"],
            command=self.on_prompt_changed,
            accent_color=THEME.NEON_MAGENTA
        )
        self.prompt_selector.pack(fill="x", pady=(4, 12))
        self.prompt_selector.set("Answer Questions")
        
        # Custom prompt editor
        NeonLabel(section, text="Custom Prompt", variant="caption").pack(anchor="w")
        
        self.prompt_text = NeonTextbox(section, height=100, accent_color=THEME.NEON_MAGENTA)
        self.prompt_text.pack(fill="x", pady=(4, 0))
        
        # Load default prompt
        self.load_default_prompt()
    
    def _create_notification_section(self, parent):
        """Create notification settings section"""
        section = self._create_section(parent, "NOTIFICATION", THEME.NEON_ORANGE)
        
        # Theme selector
        theme_row = ctk.CTkFrame(section, fg_color="transparent")
        theme_row.pack(fill="x", pady=(0, 12))
        
        theme_col = ctk.CTkFrame(theme_row, fg_color="transparent")
        theme_col.pack(side="left", fill="x", expand=True, padx=(0, 8))
        NeonLabel(theme_col, text="Theme", variant="caption").pack(anchor="w")
        
        self.notif_theme_selector = NeonComboBox(
            theme_col, values=["Light", "Dark"],
            command=self.on_notification_theme_changed,
            accent_color=THEME.NEON_ORANGE
        )
        self.notif_theme_selector.pack(fill="x", pady=(4, 0))
        self.notif_theme_selector.set("Dark" if self.notification_theme == "dark" else "Light")
        
        # Duration selector
        duration_col = ctk.CTkFrame(theme_row, fg_color="transparent")
        duration_col.pack(side="right", fill="x", expand=True)
        NeonLabel(duration_col, text="Duration", variant="caption").pack(anchor="w")
        
        self.notif_duration_selector = NeonComboBox(
            duration_col, values=["1s", "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s", "10s"],
            command=self.on_notification_duration_changed,
            accent_color=THEME.NEON_ORANGE
        )
        self.notif_duration_selector.pack(fill="x", pady=(4, 0))
        self.notif_duration_selector.set(f"{self.notification_duration}s")
    
    def _create_content_area(self, parent):
        """Create the main content area with tabs"""
        content = GlassFrame(parent, glow_color=THEME.GLASS_BORDER)
        content.pack(side="right", fill="both", expand=True)
        
        # Custom styled tabview
        self.tabview = ctk.CTkTabview(content, fg_color="transparent",
                                       segmented_button_fg_color=THEME.BG_SURFACE,
                                       segmented_button_selected_color=THEME.NEON_CYAN,
                                       segmented_button_selected_hover_color=THEME.NEON_CYAN,
                                       segmented_button_unselected_color=THEME.BG_PANEL,
                                       segmented_button_unselected_hover_color=THEME.BG_INPUT,
                                       text_color=THEME.TEXT_PRIMARY,
                                       text_color_disabled=THEME.TEXT_DIM)
        self.tabview.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Tab 1: Image Analysis
        self.image_tab = self.tabview.add("Image Analysis")
        self._create_image_tab(self.image_tab)
        
        # Tab 2: Audio Transcription
        self.audio_tab = self.tabview.add("Audio")
        self._create_audio_tab(self.audio_tab)
        
        # Tab 3: File Conversion
        self.convert_tab = self.tabview.add("Convert")
        self._create_convert_tab(self.convert_tab)
    
    def _create_image_tab(self, parent):
        """Create image analysis tab content"""
        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))
        
        NeonLabel(header, text="Analysis Results", variant="subtitle").pack(side="left")
        
        NeonButton(header, text="Clear", width=80, neon_color=THEME.NEON_RED,
                   variant="outline", command=self.clear_output).pack(side="right")
        
        # Output textbox
        self.output_text = NeonTextbox(parent, accent_color=THEME.NEON_GREEN)
        self.output_text.pack(fill="both", expand=True)
    
    def _create_audio_tab(self, parent):
        """Create audio transcription tab content"""
        # Control buttons
        controls = ctk.CTkFrame(parent, fg_color="transparent")
        controls.pack(fill="x", pady=(0, 12))
        
        NeonButton(controls, text="Start Recording", neon_color=THEME.NEON_GREEN,
                   command=self.start_recording).pack(side="left", padx=(0, 8))
        
        NeonButton(controls, text="Stop Recording", neon_color=THEME.NEON_RED,
                   variant="outline", command=self.stop_recording).pack(side="left", padx=(0, 8))
        
        NeonButton(controls, text="Upload File", neon_color=THEME.NEON_CYAN,
                   variant="outline", command=self.upload_audio_file).pack(side="left", padx=(0, 8))
        
        NeonButton(controls, text="Realtime", neon_color=THEME.NEON_PURPLE,
                   variant="ghost", command=self.transcribe_realtime).pack(side="left")
        
        # Output
        self.audio_output_text = NeonTextbox(parent, accent_color=THEME.NEON_PURPLE)
        self.audio_output_text.pack(fill="both", expand=True)
    
    def _create_convert_tab(self, parent):
        """Create file conversion tab content"""
        # File selection row
        file_row = ctk.CTkFrame(parent, fg_color="transparent")
        file_row.pack(fill="x", pady=(0, 12))
        
        NeonButton(file_row, text="Browse File", neon_color=THEME.NEON_CYAN,
                   command=self.select_file_to_convert).pack(side="left", padx=(0, 12))
        
        self.selected_file_label = NeonLabel(file_row, text="No file selected", variant="caption")
        self.selected_file_label.pack(side="left", fill="x", expand=True)
        
        # Format selection row
        format_row = ctk.CTkFrame(parent, fg_color="transparent")
        format_row.pack(fill="x", pady=(0, 12))
        
        # Category
        cat_col = ctk.CTkFrame(format_row, fg_color="transparent")
        cat_col.pack(side="left", padx=(0, 12))
        NeonLabel(cat_col, text="Category", variant="caption").pack(anchor="w")
        self.category_selector = NeonComboBox(
            cat_col, values=["Audio", "Image", "Document", "Video"],
            command=self.update_format_options, width=120
        )
        self.category_selector.pack(pady=(4, 0))
        self.category_selector.set("Audio")
        
        # Output format
        fmt_col = ctk.CTkFrame(format_row, fg_color="transparent")
        fmt_col.pack(side="left", padx=(0, 12))
        NeonLabel(fmt_col, text="Output Format", variant="caption").pack(anchor="w")
        self.output_format_selector = NeonComboBox(
            fmt_col, values=["mp3", "wav", "m4a", "aac", "ogg", "flac"], width=120
        )
        self.output_format_selector.pack(pady=(4, 0))
        self.output_format_selector.set("mp3")
        
        # Convert button
        NeonButton(format_row, text="Convert", neon_color=THEME.NEON_GREEN,
                   command=self.start_conversion, height=36).pack(side="left", padx=(12, 0), pady=(18, 0))
        
        # Output log
        self.convert_output_text = NeonTextbox(parent, accent_color=THEME.NEON_ORANGE)
        self.convert_output_text.pack(fill="both", expand=True, pady=(12, 0))
    
    def _create_action_bar(self):
        """Create the bottom action bar"""
        action_bar = GlassFrame(self, glow_color=THEME.NEON_GREEN)
        action_bar.pack(fill="x", padx=16, pady=(0, 16))
        
        inner = ctk.CTkFrame(action_bar, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)
        
        # Main action button
        self.start_button = NeonButton(
            inner, text="START CAPTURE", neon_color=THEME.NEON_GREEN,
            height=42, command=self.toggle_listening,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_button.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Secondary actions
        NeonButton(inner, text="Minimize", neon_color=THEME.TEXT_SECONDARY,
                   variant="outline", height=42, width=100,
                   command=self.minimize_to_tray).pack(side="right")
    
    # ══════════════════════════════════════════════════════════════════════════
    # UI HELPER METHODS
    # ══════════════════════════════════════════════════════════════════════════
    
    def _create_section(self, parent, title, accent_color):
        """Create a collapsible section with title"""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=(0, 20))
        
        # Section header
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))
        
        # Accent line
        ctk.CTkFrame(header, fg_color=accent_color, width=3, height=16,
                     corner_radius=2).pack(side="left", padx=(0, 10))
        
        NeonLabel(header, text=title, variant="section").pack(side="left")
        
        return section
    
    def _create_separator(self, parent):
        """Create a subtle separator line"""
        ctk.CTkFrame(parent, fg_color=THEME.GLASS_BORDER, height=1).pack(fill="x", pady=12)
    
    # ══════════════════════════════════════════════════════════════════════════
    # BUSINESS LOGIC (Preserved from original)
    # ══════════════════════════════════════════════════════════════════════════
    
    def toggle_api_visibility(self):
        """Toggle API key visibility"""
        if self.api_entry.cget("show") == "•":
            self.api_entry.configure(show="")
            self.api_show_btn.configure(text="Hide")
        else:
            self.api_entry.configure(show="•")
            self.api_show_btn.configure(text="Show")
    
    def save_all_api_keys(self):
        """Save all API keys"""
        gemini_key = self.api_entry.get().strip()
        azure_key = self.azure_entry.get().strip()
        azure_region = self.azure_region_selector.get().strip()
        cloudconvert_key = self.cloudconvert_entry.get().strip()
        
        if not gemini_key:
            messagebox.showwarning("Warning", "Gemini API Key is required!")
            return
        
        self.api_key = gemini_key
        self.azure_api_key = azure_key
        self.azure_region = azure_region
        self.cloudconvert_api_key = cloudconvert_key
        
        self.save_config()
        
        msg = "Credentials saved:\n• Gemini API Key"
        if azure_key:
            msg += f"\n• Azure Speech ({azure_region})"
        if cloudconvert_key:
            msg += "\n• CloudConvert"
        
        messagebox.showinfo("Success", msg)
        self.log_output(f"\n{msg}\n")
    
    def on_model_changed(self, choice):
        """Handle model change"""
        self.gemini_model = choice
        self.save_config()
        
        if self.is_running and self.api_key:
            try:
                self.model = genai.GenerativeModel(self.gemini_model)
                self.log_output(f"Model switched to: {choice}\n")
            except Exception as e:
                self.log_output(f"Error switching model: {e}\n")
        else:
            self.log_output(f"Model set to: {choice}\n")
    
    def on_prompt_changed(self, choice):
        """Handle prompt template change"""
        templates = {
            "Answer Questions": """You are an AI assistant specialized in answering questions from screenshots.

TASK: Analyze the screenshot and answer any questions shown.

RULES:
1. Multiple choice: Answer with letter (A/B/C/D) + content (NO explanation)
2. Short answer: Direct, concise answer
3. Multiple questions: Number each answer
4. Multiple images: Analyze in order

OUTPUT FORMAT:
- NO repeating the question
- Maximum brevity
- Use bullet points when appropriate""",
            
            "Code Analysis": """You are a code analysis expert.

Analyze the code in the screenshot and provide:
1. Language detection
2. Purpose/functionality
3. Issues/bugs found
4. Optimization suggestions
5. Security concerns if any

Be concise and technical.""",
            
            "Translate to Vietnamese": """Translate all text in the image to Vietnamese.

Rules:
- Maintain original formatting
- Technical terms: keep English in brackets
- Natural, fluent translation
- No explanations needed""",
            
            "Math Solver": """You are a math problem solver.

Solve any math problems shown in the image:
1. Show step-by-step solution
2. Box the final answer
3. Explain key formulas used
4. For graphs: describe the solution visually""",
            
            "Text Extraction": """Extract all text from the image (OCR).

Output:
- Preserve original structure
- Maintain formatting (headers, lists, etc.)
- Include any visible numbers/dates
- Note any unclear/unreadable parts""",
            
            "General Analysis": """Analyze this screenshot intelligently.

Auto-detect content type and provide appropriate response:
- Questions → Answer them
- Code → Analyze and suggest improvements  
- Text → Summarize or extract
- Charts → Explain data insights
- UI → Provide UX feedback

Be concise and actionable."""
        }
        
        if choice != "Custom":
            self.prompt_text.delete("1.0", "end")
            self.prompt_text.insert("1.0", templates.get(choice, ""))
    
    def on_notification_theme_changed(self, selection):
        """Handle notification theme change"""
        self.notification_theme = "dark" if "Dark" in selection else "white"
        self.save_config()
        self.log_output(f"Notification theme: {self.notification_theme}\n")
    
    def on_notification_duration_changed(self, selection):
        """Handle notification duration change"""
        try:
            duration = int(selection.replace("s", ""))
            self.notification_duration = max(1, min(10, duration))
            self.save_config()
            self.log_output(f"Notification duration: {self.notification_duration}s\n")
        except ValueError:
            pass
    
    def load_default_prompt(self):
        """Load default prompt"""
        if hasattr(self, 'current_prompt') and self.current_prompt:
            self.prompt_text.insert("1.0", self.current_prompt)
        else:
            self.on_prompt_changed("Answer Questions")
    
    def toggle_listening(self):
        """Toggle capture mode"""
        if not self.is_running:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        """Start capture mode"""
        self.api_key = self.api_entry.get().strip()
        if not self.api_key:
            messagebox.showerror("Error", "Please enter Gemini API Key!")
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.gemini_model)
            self.log_output(f"Connected to {self.gemini_model}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Gemini API error:\n{str(e)}")
            return
        
        self.current_prompt = self.prompt_text.get("1.0", "end-1c").strip()
        if not self.current_prompt:
            messagebox.showerror("Error", "Please enter a prompt!")
            return
        
        self.is_running = True
        
        # Try stealth mode first
        try:
            self.keyboard_hook = KeyboardHookManager(callback=self.on_prtsc_pressed)
            self.keyboard_hook.start()
            self.stealth_mode = True
            self.log_output("Stealth Mode: ACTIVE\n")
        except RuntimeError as e:
            self.keyboard_hook = None
            self.stealth_mode = False
            
            if _import_pynput():
                self.log_output("Stealth Mode: UNAVAILABLE (Admin required)\n")
                self.log_output("Fallback Mode: Standard keyboard listener\n")
                self.pynput_listener = pynput_keyboard.Listener(on_press=self._on_key_press_fallback)
                self.pynput_listener.start()
            else:
                self.is_running = False
                self.log_output(f"Error: {str(e)}\n")
                messagebox.showerror("Error", f"{str(e)}\n\nRun as Administrator for Stealth Mode.")
                return
        
        # Update UI
        self.start_button.configure(
            text="DISENGAGE STEALTH MODE",
            fg_color=THEME.NEON_RED,
            hover_color="#CC0044"
        )
        
        self.status_dot.configure(fg_color=THEME.STATUS_ONLINE)
        self.status_label.configure(text="ACTIVE", text_color=THEME.STATUS_ONLINE)
        
        self.log_output("Ready! Press PrtSc to capture.\n")
        self.log_output("=" * 50 + "\n\n")
    
    def stop_listening(self):
        """Stop capture mode"""
        self.is_running = False
        
        if self.keyboard_hook:
            self.keyboard_hook.stop()
            self.keyboard_hook = None
        
        if self.pynput_listener:
            self.pynput_listener.stop()
            self.pynput_listener = None
        
        self.stealth_mode = False
        
        # Cancel batch timer
        if self._batch_timer:
            self.after_cancel(self._batch_timer)
            self._batch_timer = None
        
        # Clear batch
        with self._batch_lock:
            for img in self._screenshot_batch:
                try:
                    img.close()
                except:
                    pass
            self._screenshot_batch.clear()
        
        # Clear pending results
        while not self._pending_results.empty():
            try:
                self._pending_results.get_nowait()
            except:
                break
        
        # Update UI
        self.start_button.configure(
            text="ENGAGE STEALTH MODE",
            fg_color=THEME.NEON_GREEN,
            hover_color="#00CC70"
        )
        
        self.status_dot.configure(fg_color=THEME.STATUS_OFFLINE)
        self.status_label.configure(text="OFFLINE", text_color=THEME.STATUS_OFFLINE)
        
        self.log_output("\nCapture stopped.\n")
        self.log_output("=" * 50 + "\n\n")
    
    def on_prtsc_pressed(self):
        """Callback when PrtSc is pressed"""
        self._screenshot_request_queue.put("capture")
    
    def _on_key_press_fallback(self, key):
        """Fallback key handler"""
        try:
            if key == pynput_keyboard.Key.print_screen:
                self._screenshot_request_queue.put("capture")
        except AttributeError:
            pass
    
    def _poll_screenshot_requests(self):
        """Poll screenshot request queue"""
        try:
            while True:
                try:
                    request = self._screenshot_request_queue.get_nowait()
                    if request == "capture":
                        self._do_capture_screenshot()
                except queue.Empty:
                    break
        except Exception as e:
            print(f"[Screenshot Poll] Error: {e}")
        finally:
            self.after(50, self._poll_screenshot_requests)
    
    def _do_capture_screenshot(self):
        """Capture screenshot and manage timer"""
        with self._batch_lock:
            if len(self._screenshot_batch) >= self.MAX_BATCH_SIZE:
                self.log_output(f"Max batch size ({self.MAX_BATCH_SIZE}) reached.\n")
                return
            
            try:
                screenshot = ImageGrab.grab()
                self._screenshot_batch.append(screenshot)
                count = len(self._screenshot_batch)
                self.log_output(f"Captured #{count}/{self.MAX_BATCH_SIZE} (5s timer...)\n")
            except Exception as e:
                self.log_output(f"Capture error: {e}\n")
                return
            
            if self._batch_timer:
                self.after_cancel(self._batch_timer)
                self._batch_timer = None
            
            self._batch_timer = self.after(self.BATCH_DELAY_MS, self._process_batch)
    
    def _process_batch(self):
        """Process batch after timeout"""
        with self._batch_lock:
            if not self._screenshot_batch:
                return
            
            screenshots = self._screenshot_batch.copy()
            self._screenshot_batch.clear()
            self._batch_timer = None
        
        threading.Thread(target=self._process_screenshots_batch, args=(screenshots,), daemon=True).start()
    
    def _process_screenshots_batch(self, screenshots: list):
        """Process screenshots with Gemini"""
        if self.is_processing:
            self.log_output("Still processing previous batch...\n")
            with self._batch_lock:
                self._screenshot_batch = screenshots + self._screenshot_batch
            return
        
        self.is_processing = True
        num_images = len(screenshots)
        
        try:
            self.log_output(f"\nSending {num_images} image(s) to {self.gemini_model}...\n")
            
            content = [self.current_prompt]
            for i, img in enumerate(screenshots):
                content.append(img)
                self.log_output(f"  Image {i+1}/{num_images} ready\n")
            
            response = self.model.generate_content(content)
            result = response.text
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_output(f"\n[{timestamp}] Result ({num_images} images):\n")
            self.log_output("-" * 50 + "\n")
            self.log_output(f"{result}\n")
            self.log_output("-" * 50 + "\n\n")
            
            self.history.append({
                "timestamp": datetime.now().isoformat(),
                "model": self.gemini_model,
                "prompt": self.current_prompt,
                "result": result,
                "num_images": num_images
            })
            
            preview = result[:200] + "..." if len(result) > 200 else result
            self._pending_results.put({
                'title': f"Analysis Complete ({num_images} images)",
                'message': f"[{timestamp}] {self.gemini_model}\n\n{preview}",
                'notification_type': 'success'
            })
            
        except Exception as e:
            self.log_output(f"Error: {str(e)}\n")
            self._show_hud_notification(
                title="Analysis Error",
                message=str(e),
                notification_type="error"
            )
        finally:
            self.is_processing = False
            for img in screenshots:
                try:
                    img.close()
                except:
                    pass
    
    def _poll_notifications(self):
        """Poll notification queue"""
        try:
            while True:
                try:
                    notif_data = self._notification_queue.get_nowait()
                    self._do_show_notification(notif_data)
                except queue.Empty:
                    break
        except Exception as e:
            print(f"[HUD] Poll error: {e}")
        finally:
            self.after(100, self._poll_notifications)
    
    def _poll_double_click(self):
        """Poll for double-click detection"""
        try:
            if not self.is_running:
                self._click_count = 0
                self._right_click_count = 0
                self._left_button_was_pressed = False
                self._right_button_was_pressed = False
                return
            
            current_time = time.time()
            
            # Left mouse button
            left_pressed = bool(ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000)
            
            if self._left_button_was_pressed and not left_pressed:
                self._click_count += 1
                
                if self._click_count == 1:
                    self._first_click_time = current_time
                elif self._click_count >= 2:
                    time_since_first = current_time - getattr(self, '_first_click_time', 0)
                    if time_since_first <= self.DOUBLE_CLICK_THRESHOLD:
                        self._on_double_click_left_detected()
                    self._click_count = 0
            
            if self._click_count == 1:
                time_since_first = current_time - getattr(self, '_first_click_time', 0)
                if time_since_first > self.DOUBLE_CLICK_THRESHOLD:
                    self._click_count = 0
            
            self._left_button_was_pressed = left_pressed
            
            # Right mouse button
            right_pressed = bool(ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000)
            
            if self._right_button_was_pressed and not right_pressed:
                self._right_click_count += 1
                
                if self._right_click_count == 1:
                    self._first_right_click_time = current_time
                elif self._right_click_count >= 2:
                    time_since_first = current_time - getattr(self, '_first_right_click_time', 0)
                    if time_since_first <= self.DOUBLE_CLICK_THRESHOLD:
                        self._on_double_click_right_detected()
                    self._right_click_count = 0
            
            if self._right_click_count == 1:
                time_since_first = current_time - getattr(self, '_first_right_click_time', 0)
                if time_since_first > self.DOUBLE_CLICK_THRESHOLD:
                    self._right_click_count = 0
            
            self._right_button_was_pressed = right_pressed
            
        except Exception as e:
            print(f"[DoubleClick] Poll error: {e}")
        finally:
            self.after(30, self._poll_double_click)
    
    def _on_double_click_left_detected(self):
        """Handle double-click left - show pending results"""
        print("[DoubleClick LEFT] Detected!")
        
        try:
            result = self._pending_results.get_nowait()
            self._show_hud_notification(
                title=result['title'],
                message=result['message'],
                notification_type=result['notification_type']
            )
            return
        except queue.Empty:
            pass
        
        if self._notification_history:
            last_notif = self._notification_history[-1]
            self._show_hud_notification(
                title=last_notif['title'],
                message=last_notif['message'],
                notification_type=last_notif['notification_type']
            )
    
    def _on_double_click_right_detected(self):
        """Handle double-click right - hide notification"""
        print("[DoubleClick RIGHT] Detected!")
        
        if self._current_notification:
            try:
                if self._current_notification_data:
                    self._add_to_notification_history(self._current_notification_data)
                
                try:
                    self._current_notification.destroy()
                except:
                    pass
                self._current_notification = None
                self._current_notification_data = None
            except Exception as e:
                print(f"[DoubleClick RIGHT] Error: {e}")
    
    def _add_to_notification_history(self, data):
        """Add notification to history"""
        self._notification_history.append({
            'title': data.get('title', ''),
            'message': data.get('message', ''),
            'notification_type': data.get('notification_type', 'info'),
            'timestamp': datetime.now().isoformat()
        })
        if len(self._notification_history) > self.MAX_NOTIFICATION_HISTORY:
            self._notification_history.pop(0)
    
    def _do_show_notification(self, data):
        """Show notification"""
        try:
            if self._current_notification:
                try:
                    if self._current_notification_data and self._current_notification_data != data:
                        self._add_to_notification_history(self._current_notification_data)
                    self._current_notification.destroy()
                except:
                    pass
                finally:
                    self._current_notification = None
                    self._current_notification_data = None
            
            theme = getattr(self, 'notification_theme', 'dark')
            duration = getattr(self, 'notification_duration', 3) * 1000
            
            notif = HUDNotification(
                parent=self,
                title=data['title'],
                message=data['message'],
                notification_type=data['notification_type'],
                duration_ms=duration,
                width=600,
                position="bottom-right",
                click_through=True,
                fade_in=False,
                color_theme=theme
            )
            
            self._current_notification = notif
            self._current_notification_data = data
            
            def on_notification_closed():
                if self._current_notification == notif and self._current_notification_data:
                    self._add_to_notification_history(self._current_notification_data)
                    self._current_notification = None
                    self._current_notification_data = None
            
            self.after(duration + 500, on_notification_closed)
            
        except Exception as e:
            print(f"[HUD] Error: {e}")
    
    def _show_hud_notification(self, title, message, notification_type="info"):
        """Queue a HUD notification"""
        self._notification_queue.put({
            'title': title,
            'message': message,
            'notification_type': notification_type
        })
    
    def log_output(self, message):
        """Log to output textbox"""
        try:
            if hasattr(self, 'tabview'):
                current_tab = self.tabview.get()
                if current_tab == "Audio" and hasattr(self, 'audio_output_text'):
                    self.audio_output_text.insert("end", message)
                    self.audio_output_text.see("end")
                    return
        except:
            pass
        
        if hasattr(self, 'output_text'):
            self.output_text.insert("end", message)
            self.output_text.see("end")
    
    def log_convert_output(self, message):
        """Log to convert output textbox"""
        if hasattr(self, 'convert_output_text'):
            self.convert_output_text.insert("end", message)
            self.convert_output_text.see("end")
    
    def clear_output(self):
        """Clear output textbox"""
        self.output_text.delete("1.0", "end")
    
    def minimize_to_tray(self):
        """Minimize to system tray"""
        self.withdraw()
        image = Image.new('RGB', (64, 64), color=THEME.NEON_CYAN)
        menu = (item('Show', self.show_window), item('Exit', self.quit_app))
        icon = pystray.Icon("snapcapai", image, "SnapCapAI", menu)
        threading.Thread(target=icon.run, daemon=True).start()
    
    def show_window(self, icon=None, item=None):
        """Show window from tray"""
        if icon:
            icon.stop()
        self.deiconify()
    
    def quit_app(self, icon=None, item=None):
        """Quit application"""
        if icon:
            icon.stop()
        self.stop_listening()
        self.destroy()
    
    def on_closing(self):
        """Handle window close"""
        if messagebox.askokcancel("Quit", "Exit SnapCapAI?"):
            try:
                current_width = self.winfo_width()
                current_height = self.winfo_height()
                
                config = {}
                if os.path.exists("config.json"):
                    with open("config.json", 'r', encoding='utf-8') as f:
                        config = json.load(f)
                
                config['window_width'] = current_width
                config['window_height'] = current_height
                
                with open("config.json", 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Error saving config: {e}")
            
            if self.is_recording and hasattr(self, 'audio_handler'):
                self.audio_handler.stop_recording()
            
            self.quit_app()
    
    def load_config(self):
        """Load configuration"""
        config_file = "config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.api_key = config.get('api_key', '')
                    self.azure_api_key = config.get('azure_api_key', '')
                    self.azure_region = config.get('azure_region', 'southeastasia')
                    self.cloudconvert_api_key = config.get('cloudconvert_api_key', '')
                    self.gemini_model = config.get('gemini_model', 'gemini-2.5-flash')
                    self.current_prompt = config.get('prompt', '')
                    self.window_width = config.get('window_width', 1400)
                    self.window_height = config.get('window_height', 900)
                    self.notification_theme = config.get('notification_theme', 'dark')
                    self.notification_duration = config.get('notification_duration', 3)
                print(f"Loaded config from {config_file}")
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration"""
        config = {
            'api_key': self.api_key,
            'azure_api_key': self.azure_api_key,
            'azure_region': self.azure_region,
            'cloudconvert_api_key': self.cloudconvert_api_key,
            'gemini_model': self.gemini_model,
            'prompt': self.prompt_text.get("1.0", "end-1c").strip() if hasattr(self, 'prompt_text') else '',
            'window_width': getattr(self, 'window_width', 1400),
            'window_height': getattr(self, 'window_height', 900),
            'notification_theme': getattr(self, 'notification_theme', 'dark'),
            'notification_duration': getattr(self, 'notification_duration', 3)
        }
        try:
            with SafeFileWriter("config.json") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print("Saved config")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    # ══════════════════════════════════════════════════════════════════════════
    # AUDIO & CONVERSION METHODS
    # ══════════════════════════════════════════════════════════════════════════
    
    def _init_audio_handler(self) -> bool:
        """Initialize audio handler"""
        try:
            self.azure_api_key = self.azure_entry.get().strip()
            self.azure_region = self.azure_region_selector.get().strip()
            
            if not self.azure_api_key:
                self.log_output("Azure API Key required!\n")
                return False
            
            self.audio_handler = AudioHandler(self.azure_api_key, self.azure_region, self.temp_folder)
            is_valid, msg = self.audio_handler.validate_azure_credentials()
            self.log_output(f"{msg}\n")
            return is_valid
        except Exception as e:
            self.log_output(f"Error initializing audio handler: {e}\n")
            return False
    
    def start_recording(self):
        """Start audio recording"""
        if self.is_recording:
            self.log_output("Already recording...\n")
            return
        
        if not self._init_audio_handler():
            return
        
        self.is_recording = True
        success, msg = self.audio_handler.start_recording()
        self.log_output(f"{msg}\n")
    
    def stop_recording(self):
        """Stop audio recording"""
        if not self.is_recording:
            self.log_output("Not recording!\n")
            return
        
        self.is_recording = False
        success, msg, file_path = self.audio_handler.stop_recording()
        self.log_output(f"{msg}\n")
        
        if success and file_path:
            threading.Thread(target=self._transcribe_file_thread, args=(file_path,), daemon=True).start()
    
    def upload_audio_file(self):
        """Upload audio file for transcription"""
        if not self._init_audio_handler():
            return
        
        file_path = filedialog.askopenfilename(
            title="Select audio file",
            filetypes=[("Audio files", "*.wav *.mp3 *.m4a *.flac"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        self.log_output(f"Selected: {file_path}\n")
        threading.Thread(target=self._transcribe_file_thread, args=(file_path,), daemon=True).start()
    
    def _transcribe_file_thread(self, file_path):
        """Transcribe audio file"""
        try:
            self.log_output("Transcribing...\n")
            success, result = self.audio_handler.transcribe_audio_file(file_path)
            
            if success:
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.log_output(f"\n[{timestamp}] Transcription:\n")
                self.log_output("-" * 50 + "\n")
                self.log_output(f"{result}\n")
                self.log_output("-" * 50 + "\n\n")
            else:
                self.log_output(f"{result}\n")
        except Exception as e:
            self.log_output(f"Error: {e}\n")
    
    def transcribe_realtime(self):
        """Real-time transcription"""
        if not self._init_audio_handler():
            return
        
        def callback(result):
            self.log_output(f"Realtime: {result}\n")
        
        self.log_output("Starting realtime transcription (30s)...\n")
        threading.Thread(target=self.audio_handler.transcribe_audio_realtime, args=("vi-VN", callback), daemon=True).start()
    
    def _init_cloudconvert_handler(self) -> bool:
        """Initialize CloudConvert handler"""
        try:
            api_key = self.cloudconvert_entry.get().strip()
            if not api_key:
                self.log_convert_output("CloudConvert API Key required!\n")
                return False
            
            self.cloudconvert_handler = CloudConvertHandler(api_key)
            is_valid, msg = self.cloudconvert_handler.validate_credentials()
            self.log_convert_output(f"{msg}\n")
            return is_valid
        except Exception as e:
            self.log_convert_output(f"Error: {e}\n")
            return False
    
    def update_format_options(self, selected_category=None):
        """Update format options based on category"""
        if not hasattr(self, 'universal_converter') or self.universal_converter is None:
            self.universal_converter = UniversalConverter("")
        
        category = selected_category or self.category_selector.get()
        category_map = {"Audio": "audio", "Image": "image", "Document": "document", "Video": "video"}
        
        category_key = category_map.get(category, "audio")
        formats = self.universal_converter.get_supported_formats(category_key)
        format_list = formats.get(category_key, ["mp3"])
        
        self.output_format_selector.configure(values=format_list)
        if format_list:
            self.output_format_selector.set(format_list[0])
        
        self.log_convert_output(f"Category: {category} → {len(format_list)} formats\n")
    
    def select_file_to_convert(self):
        """Select file for conversion"""
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Select file to convert",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.m4a *.aac *.ogg *.flac *.wma *.opus"),
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff *.svg"),
                ("Document files", "*.pdf *.doc *.docx *.xls *.xlsx *.ppt *.pptx *.txt"),
                ("Video files", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.selected_convert_file = file_path
            filename = os.path.basename(file_path)
            self.selected_file_label.configure(text=filename)
            self.log_convert_output(f"Selected: {filename}\n")
    
    def start_conversion(self):
        """Start file conversion"""
        if not self.selected_convert_file:
            messagebox.showwarning("Warning", "Please select a file first!")
            return
        
        if not self._init_cloudconvert_handler():
            return
        
        output_format = self.output_format_selector.get()
        self.log_convert_output(f"Converting to {output_format}...\n")
        
        threading.Thread(target=self._convert_file_thread, args=(self.selected_convert_file, output_format), daemon=True).start()
    
    def _convert_file_thread(self, file_path, output_format):
        """Convert file in background"""
        try:
            file_base = os.path.splitext(os.path.basename(file_path))[0]
            category = self.category_selector.get().lower()
            output_folder = os.path.join(self.temp_folder, category)
            os.makedirs(output_folder, exist_ok=True)
            output_file = os.path.join(output_folder, f"{file_base}_converted.{output_format}")
            
            self.log_convert_output("Uploading to CloudConvert...\n")
            
            success, result = self.cloudconvert_handler.convert_file(file_path, output_format, output_file)
            
            if success:
                timestamp = datetime.now().strftime("%H:%M:%S")
                file_size = os.path.getsize(output_file) / (1024 * 1024)
                
                self.log_convert_output(f"\n[{timestamp}] Conversion complete!\n")
                self.log_convert_output(f"Output: {os.path.basename(output_file)}\n")
                self.log_convert_output(f"Size: {file_size:.2f} MB\n")
                self.log_convert_output("-" * 50 + "\n\n")
            else:
                self.log_convert_output(f"Error: {result}\n")
                
        except Exception as e:
            self.log_convert_output(f"Conversion error: {e}\n")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point with auto-elevation"""
    if not is_admin():
        print("Not running as Administrator")
        print("Requesting admin privileges for Stealth Mode...")
        
        if run_as_admin():
            print("Elevated successfully. Restarting...")
            sys.exit(0)
        else:
            print("Failed to elevate. Running in Fallback Mode...")
    else:
        print("Running with Administrator privileges")
        print("Stealth Mode available")
    
    app = ScreenCaptureGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
