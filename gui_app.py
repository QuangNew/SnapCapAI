"""
SnapCapAI - AI-Powered Screen Capture & Analysis
Giao diện đồ họa cho chương trình phân tích ảnh với Gemini AI + Audio Transcription
"""

import os
import io
import json
import shutil
import subprocess
import threading
import customtkinter as ctk
from datetime import datetime
from PIL import ImageGrab, Image, ImageTk
from pynput import keyboard
import google.generativeai as genai
from tkinter import scrolledtext, messagebox, filedialog, simpledialog
import pystray
from pystray import MenuItem as item
from audio_handler import AudioHandler
from cloudconvert_handler import CloudConvertHandler
from universal_converter import UniversalConverter
from winotify import Notification, audio

# Cấu hình theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ScreenCaptureGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Khởi tạo các thuộc tính config mặc định TRƯỚC khi load
        self.api_key = ""
        self.azure_api_key = ""
        self.azure_region = "southeastasia"
        self.cloudconvert_api_key = ""
        self.gemini_model = "gemini-2.0-flash"
        self.current_prompt = ""
        self.window_width = 1280
        self.window_height = 800
        
        # Load config first để lấy window size và API keys
        self.load_config()
        
        # Lấy kích thước window từ config (16:10 ratio)
        window_width = getattr(self, 'window_width', 1280)
        window_height = getattr(self, 'window_height', 800)
        
        # Cấu hình cửa sổ chính
        self.title("🤖 SnapCapAI - AI Analyzer")
        self.geometry(f"{window_width}x{window_height}")
        self.minsize(800, 600)
        
        # Biến trạng thái
        self.is_running = False
        self.is_processing = False
        self.is_recording = False
        self.listener = None
        self.history = []
        self.selected_convert_file = None
        
        # Khởi tạo temp folder
        self.temp_folder = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(self.temp_folder, exist_ok=True)
        
        # Khởi tạo handlers
        self.audio_handler = None
        self.cloudconvert_handler = None
        self.universal_converter = None
        
        # Tạo giao diện
        self.create_widgets()
        
        # Protocol đóng cửa sổ
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        """Tạo các widget cho giao diện"""
        
        # ===== HEADER =====
        header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Title and credit container
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(side="left")
        
        title_label = ctk.CTkLabel(
            title_container,
            text="🤖 SnapCapAI - AI Analyzer",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(anchor="w")
        
        credit_label = ctk.CTkLabel(
            title_container,
            text="By QuangNew",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        )
        credit_label.pack(anchor="w", pady=(2, 0))
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            header_frame,
            text="⭕ Stopped",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.status_label.pack(side="right")
        
        # ===== NOTIFICATION BAR =====
        self.notification_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#2B2B2B", height=0)
        self.notification_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.notification_frame.pack_forget()  # Ẩn ban đầu
        
        self.notification_label = ctk.CTkLabel(
            self.notification_frame,
            text="",
            font=ctk.CTkFont(size=13),
            wraplength=1200,
            justify="left"
        )
        self.notification_label.pack(padx=15, pady=10, fill="x")
        
        # ===== MAIN CONTAINER =====
        main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left Panel - Configuration
        left_panel = ctk.CTkFrame(main_container, width=400)
        left_panel.pack(side="left", fill="both", padx=(0, 10), expand=False)
        left_panel.pack_propagate(False)
        
        # Right Panel - Tabbed Interface
        right_panel = ctk.CTkFrame(main_container)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Tạo Tabview
        self.tabview = ctk.CTkTabview(right_panel)
        self.tabview.pack(fill="both", expand=True)
        
        # Tab 1: Image Analysis
        self.image_tab = self.tabview.add("📸 Image Analysis")
        self.create_output_section(self.image_tab)
        
        # Tab 2: Audio Transcription
        self.audio_tab = self.tabview.add("🎤 Audio Transcription")
        self.create_audio_section(self.audio_tab)
        
        # Tab 3: File Conversion
        self.convert_tab = self.tabview.add("🔄 File Conversion")
        self.create_convert_section(self.convert_tab)
        
        # ===== LEFT PANEL CONTENT =====
        self.create_config_section(left_panel)
        
        # ===== CONTROL BUTTONS =====
        control_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        control_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        self.start_button = ctk.CTkButton(
            control_frame,
            text="▶️ Start Listening",
            command=self.toggle_listening,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color="#2CC985",
            hover_color="#25A866"
        )
        self.start_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        minimize_button = ctk.CTkButton(
            control_frame,
            text="🔽 Minimize to Tray",
            command=self.minimize_to_tray,
            font=ctk.CTkFont(size=14),
            height=50,
            fg_color="#5E5E5E",
            hover_color="#4A4A4A"
        )
        minimize_button.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
    def create_config_section(self, parent):
        """Tạo phần cấu hình API keys với nút thu gọn"""
        
        # ==== API CONFIGURATION HEADER với Toggle Button ====
        config_header = ctk.CTkFrame(parent, fg_color="transparent")
        config_header.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            config_header,
            text="⚙️ API Configuration",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Toggle Button
        self.api_toggle_button = ctk.CTkButton(
            config_header,
            text="▼",
            command=self.toggle_api_section,
            width=30,
            height=30,
            fg_color="#5E5E5E",
            hover_color="#4A4A4A",
            font=ctk.CTkFont(size=16)
        )
        self.api_toggle_button.pack(side="right")
        
        # Container cho tất cả API configs (có thể ẩn/hiện)
        self.api_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.api_container.pack(fill="x", padx=15, pady=(5, 10))
        
        # ===== ALL APIs trong 1 Frame duy nhất =====
        all_apis_frame = ctk.CTkFrame(self.api_container)
        all_apis_frame.pack(fill="x", pady=(0, 5))
        
        # --- Gemini API ---
        ctk.CTkLabel(
            all_apis_frame,
            text="🔑 Gemini API",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 3))
        
        gemini_entry_frame = ctk.CTkFrame(all_apis_frame, fg_color="transparent")
        gemini_entry_frame.pack(fill="x", padx=10, pady=(0, 3))
        
        self.api_entry = ctk.CTkEntry(
            gemini_entry_frame,
            placeholder_text="Gemini API key...",
            show="*",
            height=28
        )
        self.api_entry.pack(side="left", fill="x", expand=True, padx=(0, 3))
        if self.api_key:
            self.api_entry.delete(0, "end")
            self.api_entry.insert(0, self.api_key)
        
        ctk.CTkButton(
            gemini_entry_frame,
            text="👁️",
            command=self.toggle_api_visibility,
            width=35,
            height=28,
            fg_color="#5E5E5E"
        ).pack(side="left")
        
        self.model_selector = ctk.CTkComboBox(
            all_apis_frame,
            values=["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-pro"],
            command=self.on_model_changed,
            height=26,
            font=ctk.CTkFont(size=11)
        )
        self.model_selector.pack(fill="x", padx=10, pady=(0, 8))
        self.model_selector.set(self.gemini_model)
        
        # Separator
        ctk.CTkFrame(all_apis_frame, height=1, fg_color="#3E3E3E").pack(fill="x", padx=10, pady=3)
        
        # --- Azure Speech API ---
        ctk.CTkLabel(
            all_apis_frame,
            text="🎤 Azure Speech (Optional)",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(5, 3))
        
        azure_entry_frame = ctk.CTkFrame(all_apis_frame, fg_color="transparent")
        azure_entry_frame.pack(fill="x", padx=10, pady=(0, 3))
        
        self.azure_entry = ctk.CTkEntry(
            azure_entry_frame,
            placeholder_text="Azure API key...",
            show="*",
            height=28
        )
        self.azure_entry.pack(side="left", fill="x", expand=True, padx=(0, 3))
        if self.azure_api_key:
            self.azure_entry.delete(0, "end")
            self.azure_entry.insert(0, self.azure_api_key)
        
        ctk.CTkButton(
            azure_entry_frame,
            text="👁️",
            command=self.toggle_azure_visibility,
            width=35,
            height=28,
            fg_color="#5E5E5E"
        ).pack(side="left")
        
        self.azure_region_selector = ctk.CTkComboBox(
            all_apis_frame,
            values=[
                "southeastasia", "eastasia", "eastus", 
                "westus", "westus2", "westeurope", "northeurope"
            ],
            height=26,
            font=ctk.CTkFont(size=11)
        )
        self.azure_region_selector.pack(fill="x", padx=10, pady=(0, 8))
        self.azure_region_selector.set(self.azure_region)
        
        # Separator
        ctk.CTkFrame(all_apis_frame, height=1, fg_color="#3E3E3E").pack(fill="x", padx=10, pady=3)
        
        # --- CloudConvert API ---
        ctk.CTkLabel(
            all_apis_frame,
            text="🔄 CloudConvert (Optional)",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(5, 3))
        
        cloudconvert_entry_frame = ctk.CTkFrame(all_apis_frame, fg_color="transparent")
        cloudconvert_entry_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.cloudconvert_entry = ctk.CTkEntry(
            cloudconvert_entry_frame,
            placeholder_text="CloudConvert API token...",
            show="*",
            height=28
        )
        self.cloudconvert_entry.pack(side="left", fill="x", expand=True, padx=(0, 3))
        if self.cloudconvert_api_key:
            self.cloudconvert_entry.delete(0, "end")
            self.cloudconvert_entry.insert(0, self.cloudconvert_api_key)
        
        ctk.CTkButton(
            cloudconvert_entry_frame,
            text="👁️",
            command=self.toggle_cloudconvert_visibility,
            width=35,
            height=28,
            fg_color="#5E5E5E"
        ).pack(side="left")
        
        # ===== SAVE ALL Button =====
        ctk.CTkButton(
            self.api_container,
            text="💾 Save All API Keys",
            command=self.save_all_api_keys,
            height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2CC985",
            hover_color="#25A866"
        ).pack(fill="x", padx=0, pady=(5, 0))
        
        # Track API section state
        self.api_section_visible = True
        
        # Prompt Templates Section (lưu reference để pack api_container before nó)
        self.prompt_frame = ctk.CTkFrame(parent)
        self.prompt_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            self.prompt_frame,
            text="📝 Prompt Template",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.prompt_selector = ctk.CTkComboBox(
            self.prompt_frame,
            values=[
                "Custom",
                "Chỉ trả lời câu hỏi",
                "Code Analysis",
                "Translate to Vietnamese",
                "Math Solver",
                "Text Extraction"
            ],
            command=self.on_prompt_changed
        )
        self.prompt_selector.pack(fill="x", padx=10, pady=(0, 10))
        self.prompt_selector.set("Chỉ trả lời câu hỏi")
        
        # Custom Prompt Editor (với scrollbar)
        ctk.CTkLabel(
            self.prompt_frame,
            text="✏️ Custom Prompt",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Textbox với scrollbar tự động
        self.prompt_text = ctk.CTkTextbox(
            self.prompt_frame,
            height=150,
            font=ctk.CTkFont(size=12),
            wrap="word"  # Word wrap để tránh scroll ngang
        )
        self.prompt_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Load prompt mặc định
        self.load_default_prompt()
        
    def create_output_section(self, parent):
        """Tạo phần hiển thị kết quả"""
        
        # Output Header
        output_header = ctk.CTkFrame(parent, height=40, fg_color="transparent")
        output_header.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            output_header,
            text="📊 Analysis Results",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            output_header,
            text="🗑️ Clear",
            command=self.clear_output,
            width=80,
            height=30,
            fg_color="#E74C3C",
            hover_color="#C0392B"
        ).pack(side="right")
        
        # Output Text Area
        self.output_text = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        self.output_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
    def create_audio_section(self, parent):
        """Tạo phần Audio Transcription (không có Convert button)"""
        
        # Audio Header
        audio_header = ctk.CTkFrame(parent, fg_color="transparent")
        audio_header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            audio_header,
            text="🎤 Audio Transcription",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Audio Control Buttons (without Convert)
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(10, 10))
        
        ctk.CTkButton(
            button_frame,
            text="🎤 Start Recording",
            command=self.start_recording,
            height=40,
            fg_color="#2CC985",
            hover_color="#25A866"
        ).pack(side="left", padx=(0, 5), fill="x", expand=True)
        
        ctk.CTkButton(
            button_frame,
            text="⏹️ Stop Recording",
            command=self.stop_recording,
            height=40,
            fg_color="#E74C3C",
            hover_color="#C0392B"
        ).pack(side="left", padx=(0, 5), fill="x", expand=True)
        
        ctk.CTkButton(
            button_frame,
            text="📂 Upload File",
            command=self.upload_audio_file,
            height=40,
            fg_color="#3498DB",
            hover_color="#2980B9"
        ).pack(side="left", padx=(0, 5), fill="x", expand=True)
        
        ctk.CTkButton(
            button_frame,
            text="🎙️ Realtime",
            command=self.transcribe_realtime,
            height=40,
            fg_color="#9B59B6",
            hover_color="#8E44AD"
        ).pack(side="left", padx=(0, 5), fill="x", expand=True)
        
        ctk.CTkButton(
            button_frame,
            text="📂 STT Folder",
            command=self.open_stt_output_folder,
            height=40,
            fg_color="#F39C12",
            hover_color="#E67E22"
        ).pack(side="left", fill="x", expand=True)
        
        # Audio Output Text Area
        self.audio_output_text = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        self.audio_output_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Override log_output to use audio_output_text when in audio tab
        self._original_output_text = self.output_text
    
    def create_convert_section(self, parent):
        """Tạo phần File Conversion với UI compact"""
        
        # Main Control Frame - compact horizontal layout
        control_frame = ctk.CTkFrame(parent, fg_color="#2B2B2B", corner_radius=8)
        control_frame.pack(fill="x", padx=15, pady=(10, 10))
        
        row_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        row_frame.pack(fill="x", padx=10, pady=10)
        
        # Column 1: File Selection
        col1 = ctk.CTkFrame(row_frame, fg_color="transparent")
        col1.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        ctk.CTkLabel(col1, text="📁 File:", font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w")
        self.selected_file_label = ctk.CTkLabel(
            col1, text="No file selected", font=ctk.CTkFont(size=9),
            text_color="#888888", anchor="w"
        )
        self.selected_file_label.pack(fill="x", pady=(2, 5))
        ctk.CTkButton(
            col1, text="Browse", command=self.select_file_to_convert,
            height=32, font=ctk.CTkFont(size=11),
            fg_color="#3498DB", hover_color="#2980B9"
        ).pack(fill="x")
        
        # Column 2: Category
        col2 = ctk.CTkFrame(row_frame, fg_color="transparent", width=150)
        col2.pack(side="left", padx=5)
        col2.pack_propagate(False)
        
        ctk.CTkLabel(col2, text="Category:", font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w")
        self.category_selector = ctk.CTkComboBox(
            col2, values=["Audio", "Image", "Document", "Video"],
            height=32, font=ctk.CTkFont(size=11), command=self.update_format_options
        )
        self.category_selector.pack(fill="x", pady=(2, 0))
        self.category_selector.set("Audio")
        
        # Column 3: Format
        col3 = ctk.CTkFrame(row_frame, fg_color="transparent", width=130)
        col3.pack(side="left", padx=5)
        col3.pack_propagate(False)
        
        ctk.CTkLabel(col3, text="Format:", font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w")
        self.output_format_selector = ctk.CTkComboBox(
            col3, values=["mp3", "wav", "m4a", "aac", "ogg", "flac"],
            height=32, font=ctk.CTkFont(size=11)
        )
        self.output_format_selector.pack(fill="x", pady=(2, 0))
        self.output_format_selector.set("mp3")
        
        # Column 4: Actions
        col4 = ctk.CTkFrame(row_frame, fg_color="transparent", width=140)
        col4.pack(side="left", padx=(5, 0))
        col4.pack_propagate(False)
        
        ctk.CTkButton(
            col4, text="✨ Convert", command=self.start_conversion,
            height=35, font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2CC985", hover_color="#25A866"
        ).pack(fill="x", pady=(17, 3))
        
        ctk.CTkButton(
            col4, text="📂 Folder", command=self.open_convert_output_folder,
            height=28, font=ctk.CTkFont(size=10),
            fg_color="#4A90E2", hover_color="#357ABD"
        ).pack(fill="x")
        
        # Conversion Log - MAXIMIZED
        log_frame = ctk.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=8)
        log_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.pack(fill="x", padx=10, pady=(8, 5))
        
        ctk.CTkLabel(log_header, text="📋 Log", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        ctk.CTkButton(
            log_header, text="Clear", command=lambda: self.convert_output_text.delete("1.0", "end"),
            height=24, width=60, font=ctk.CTkFont(size=10),
            fg_color="#3B3B3B", hover_color="#4B4B4B"
        ).pack(side="right")
        
        self.convert_output_text = ctk.CTkTextbox(log_frame, font=ctk.CTkFont(size=10), wrap="word")
        self.convert_output_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Welcome message
        self.convert_output_text.insert("1.0", "🎉 Universal Converter | 49+ formats | 4 categories\n📂 Output: temp/{category}/\n\n")
        
    def toggle_api_visibility(self):
        """Hiện/ẩn API key"""
        if self.api_entry.cget("show") == "*":
            self.api_entry.configure(show="")
        else:
            self.api_entry.configure(show="*")
    
    def toggle_azure_visibility(self):
        """Hiện/ẩn Azure API key"""
        if self.azure_entry.cget("show") == "*":
            self.azure_entry.configure(show="")
        else:
            self.azure_entry.configure(show="*")
    
    def toggle_api_section(self):
        """Thu gọn/Mở rộng phần API Configuration"""
        if self.api_section_visible:
            # Ẩn container
            self.api_container.pack_forget()
            self.api_toggle_button.configure(text="▶")
            self.api_section_visible = False
        else:
            # Hiện container (pack before prompt_frame để giữ đúng thứ tự)
            self.api_container.pack(fill="x", padx=15, pady=(5, 10), before=self.prompt_frame)
            self.api_toggle_button.configure(text="▼")
            self.api_section_visible = True
            
    def save_api_key(self):
        """Lưu API key"""
        self.api_key = self.api_entry.get().strip()
        if self.api_key:
            self.save_config()
            messagebox.showinfo("Success", "Gemini API Key đã được lưu!")
        else:
            messagebox.showwarning("Warning", "Vui lòng nhập API Key!")
    
    def save_azure_key(self):
        """Lưu Azure API key"""
        self.azure_api_key = self.azure_entry.get().strip()
        if self.azure_api_key:
            self.save_config()
            messagebox.showinfo("Success", "Azure API Key đã được lưu!")
        else:
            messagebox.showwarning("Warning", "Vui lòng nhập Azure API Key!")
    
    def save_cloudconvert_key(self):
        """Lưu CloudConvert API key"""
        self.cloudconvert_api_key = self.cloudconvert_entry.get().strip()
        if self.cloudconvert_api_key:
            self.save_config()
            messagebox.showinfo("Success", "CloudConvert API Key đã được lưu!")
        else:
            messagebox.showwarning("Warning", "Vui lòng nhập CloudConvert API Key!")
    
    def toggle_cloudconvert_visibility(self):
        """Hiện/ẩn CloudConvert API key"""
        if self.cloudconvert_entry.cget("show") == "*":
            self.cloudconvert_entry.configure(show="")
        else:
            self.cloudconvert_entry.configure(show="*")
    
    def save_all_api_keys(self):
        """Lưu tất cả API keys cùng lúc"""
        # Get all API keys
        gemini_key = self.api_entry.get().strip()
        azure_key = self.azure_entry.get().strip()
        azure_region = self.azure_region_selector.get().strip()
        cloudconvert_key = self.cloudconvert_entry.get().strip()
        
        # Validate required keys
        if not gemini_key:
            messagebox.showwarning("Warning", "Vui lòng nhập Gemini API Key!")
            return
        
        # Save to instance variables
        self.api_key = gemini_key
        self.azure_api_key = azure_key
        self.azure_region = azure_region
        self.cloudconvert_api_key = cloudconvert_key
        
        # Save to config file
        self.save_config()
        
        # Show success message
        msg = "✅ Đã lưu thành công:\n"
        msg += f"• Gemini API Key\n"
        if azure_key:
            msg += f"• Azure Speech API Key\n"
            msg += f"• Azure Region: {azure_region}\n"
        if cloudconvert_key:
            msg += f"• CloudConvert API Key\n"
        
        messagebox.showinfo("Success", msg)
        self.log_output(f"\n{msg}\n")
    
    def on_model_changed(self, choice):
        """Xử lý khi thay đổi model"""
        self.gemini_model = choice
        self.save_config()
        self.log_output(f"✅ Đã thay đổi model thành: {choice}\n")
            
    def on_prompt_changed(self, choice):
        """Xử lý khi thay đổi prompt template"""
        templates = {
            "Chỉ trả lời câu hỏi": "Chỉ quan tâm đến các câu hỏi trong ảnh, trả lời trọng tâm đáp án, ngắn gọn, không cần phân tích hay bất kỳ điều gì khác.",
            "Code Analysis": """Hãy phân tích đoạn code trong ảnh:
1. Ngôn ngữ lập trình
2. Chức năng chính của code
3. Phát hiện lỗi hoặc bug tiềm ẩn
4. Đề xuất cải tiến code""",
            "Translate to Vietnamese": "Hãy dịch toàn bộ văn bản trong ảnh sang tiếng Việt. Giữ nguyên định dạng và cấu trúc gốc.",
            "Math Solver": """Phân tích và giải bài toán trong ảnh:
1. Xác định loại bài toán
2. Giải chi tiết từng bước
3. Kiểm tra lại kết quả
4. Đưa ra đáp án cuối cùng""",
            "Text Extraction": "Trích xuất toàn bộ văn bản có trong ảnh. Giữ nguyên định dạng, xuống dòng và cấu trúc."
        }
        
        if choice != "Custom":
            self.prompt_text.delete("1.0", "end")
            self.prompt_text.insert("1.0", templates.get(choice, ""))
            
    def load_default_prompt(self):
        """Load prompt mặc định"""
        default_prompt = "Chỉ quan tâm đến các câu hỏi trong ảnh, trả lời trọng tâm đáp án, ngắn gọn, không cần phân tích hay bất kỳ điều gì khác."
        self.prompt_text.insert("1.0", default_prompt)
        
    def toggle_listening(self):
        """Bật/tắt chế độ lắng nghe"""
        if not self.is_running:
            self.start_listening()
        else:
            self.stop_listening()
            
    def start_listening(self):
        """Bắt đầu lắng nghe phím PrtSc"""
        # Kiểm tra API key
        self.api_key = self.api_entry.get().strip()
        if not self.api_key:
            messagebox.showerror("Error", "Vui lòng nhập Gemini API Key!")
            return
            
        # Cấu hình Gemini
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.gemini_model)
            self.log_output(f"✅ Đã kết nối với {self.gemini_model}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Lỗi kết nối Gemini API:\n{str(e)}")
            return
            
        # Lấy prompt
        self.current_prompt = self.prompt_text.get("1.0", "end-1c").strip()
        if not self.current_prompt:
            messagebox.showerror("Error", "Vui lòng nhập prompt!")
            return
            
        # Bắt đầu listener
        self.is_running = True
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()
        
        # Cập nhật UI
        self.start_button.configure(
            text="⏹️ Stop Listening",
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        self.status_label.configure(text="🟢 Running", text_color="#2CC985")
        
        self.log_output("🚀 Đã bắt đầu lắng nghe phím PrtSc!\n")
        self.log_output(f"📝 Prompt: {self.current_prompt[:50]}...\n")
        self.log_output("=" * 60 + "\n\n")
        
    def stop_listening(self):
        """Dừng lắng nghe"""
        self.is_running = False
        if self.listener:
            self.listener.stop()
            self.listener = None
            
        # Cập nhật UI
        self.start_button.configure(
            text="▶️ Start Listening",
            fg_color="#2CC985",
            hover_color="#25A866"
        )
        self.status_label.configure(text="⭕ Stopped", text_color="gray")
        
        self.log_output("\n⏹️ Đã dừng lắng nghe!\n")
        self.log_output("=" * 60 + "\n\n")
        
    def on_key_press(self, key):
        """Xử lý sự kiện nhấn phím"""
        try:
            if key == keyboard.Key.print_screen:
                self.log_output("🎯 Phát hiện nhấn PrtSc!\n")
                threading.Thread(target=self.process_screenshot, daemon=True).start()
        except AttributeError:
            pass
            
    def process_screenshot(self):
        """Xử lý chụp màn hình và phân tích"""
        if self.is_processing:
            self.log_output("⚠️ Đang xử lý ảnh trước đó...\n")
            return
            
        self.is_processing = True
        
        try:
            # Chụp màn hình
            self.log_output("📸 Đang chụp màn hình...\n")
            screenshot = ImageGrab.grab()
            
            # Gửi đến Gemini
            self.log_output(f"🤖 Đang gửi đến {self.gemini_model}...\n")
            response = self.model.generate_content([
                self.current_prompt,
                screenshot
            ])
            
            result = response.text
            
            # Hiển thị kết quả
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_output(f"\n✅ [{timestamp}] Kết quả:\n")
            self.log_output("-" * 60 + "\n")
            self.log_output(f"{result}\n")
            self.log_output("-" * 60 + "\n\n")
            
            # Lưu vào lịch sử
            self.history.append({
                "timestamp": datetime.now().isoformat(),
                "model": self.gemini_model,
                "prompt": self.current_prompt,
                "result": result
            })
            
            # Hiển thị Windows Toast Notification (gọi trực tiếp từ thread)
            preview = result[:200] + "..." if len(result) > 200 else result
            self.show_system_notification(
                title="✅ Phân tích hoàn tất!",
                message=f"[{timestamp}] {self.gemini_model}\n\n{preview}",
                timeout=5
            )
            
        except Exception as e:
            error_msg = f"❌ Lỗi: {str(e)}"
            self.log_output(f"{error_msg}\n")
            # Hiển thị thông báo lỗi (gọi trực tiếp từ thread)
            self.show_system_notification(
                title="❌ Lỗi phân tích",
                message=str(e),
                timeout=8
            )
        finally:
            self.is_processing = False
            
    def log_output(self, message):
        """Ghi log vào output text (auto-detect tab)"""
        # Ghi vào tab audio nếu hiện tại đang ở tab audio
        try:
            if hasattr(self, 'tabview') and hasattr(self, 'audio_tab'):
                current_tab = self.tabview.get()
                if current_tab == "🎤 Audio Transcription" and hasattr(self, 'audio_output_text'):
                    self.audio_output_text.insert("end", message)
                    self.audio_output_text.see("end")
                    return
        except:
            pass
        
        # Ghi vào tab image (mặc định)
        if hasattr(self, 'output_text'):
            self.output_text.insert("end", message)
            self.output_text.see("end")
        
    def clear_output(self):
        """Xóa output"""
        self.output_text.delete("1.0", "end")
    
    def show_notification(self, message, notification_type="info", duration=5000):
        """
        Hiển thị thông báo trên cửa sổ
        
        Args:
            message: Nội dung thông báo
            notification_type: Loại thông báo ("success", "error", "info", "warning")
            duration: Thời gian hiển thị (ms), 0 = không tự động ẩn
        """
        # Màu sắc theo loại thông báo
        colors = {
            "success": ("#1B5E20", "#4CAF50"),  # bg, text
            "error": ("#B71C1C", "#EF5350"),
            "info": ("#0D47A1", "#42A5F5"),
            "warning": ("#E65100", "#FF9800")
        }
        
        bg_color, text_color = colors.get(notification_type, colors["info"])
        
        # Cập nhật nội dung và màu sắc
        self.notification_label.configure(text=message, text_color=text_color)
        self.notification_frame.configure(fg_color=bg_color)
        
        # Hiển thị notification
        self.notification_frame.pack(fill="x", padx=20, pady=(0, 10), before=self.children[list(self.children.keys())[2]])
        
        # Tự động ẩn sau duration (nếu > 0)
        if duration > 0:
            self.after(duration, self.hide_notification)
    
    def hide_notification(self):
        """Ẩn thông báo"""
        self.notification_frame.pack_forget()
    
    def show_system_notification(self, title, message, timeout=10):
        """
        Hiển thị Windows Toast Notification
        
        Args:
            title: Tiêu đề thông báo
            message: Nội dung thông báo
            timeout: Thời gian hiển thị (giây) - winotify sử dụng 'short' hoặc 'long'
        """
        try:
            # Tạo notification
            toast = Notification(
                app_id="SnapCapAI",
                title=title,
                msg=message,
                duration="long" if timeout > 5 else "short"
            )
            
            # Thêm âm thanh
            toast.set_audio(audio.Default, loop=False)
            
            # Hiển thị trực tiếp (không dùng thread vì đã trong thread rồi)
            toast.show()
            
        except Exception as e:
            print(f"Lỗi hiển thị system notification: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: Hiển thị trên window nếu system notification thất bại
            self.show_notification(f"{title}: {message}", "info", duration=5000)
        
    def minimize_to_tray(self):
        """Thu nhỏ xuống system tray"""
        self.withdraw()
        
        # Tạo icon
        image = Image.new('RGB', (64, 64), color='#1E3A8A')
        
        menu = (
            item('Show', self.show_window),
            item('Exit', self.quit_app)
        )
        
        icon = pystray.Icon("snapcapai", image, "SnapCapAI", menu)
        
        threading.Thread(target=icon.run, daemon=True).start()
        
    def show_window(self, icon=None, item=None):
        """Hiện lại cửa sổ"""
        if icon:
            icon.stop()
        self.deiconify()
        
    def quit_app(self, icon=None, item=None):
        """Thoát ứng dụng"""
        if icon:
            icon.stop()
        self.stop_listening()
        self.destroy()
        
    def on_closing(self):
        """Xử lý khi đóng cửa sổ"""
        if messagebox.askokcancel("Quit", "Bạn có muốn thoát chương trình?"):
            try:
                # Lưu kích thước cửa sổ hiện tại
                current_width = self.winfo_width()
                current_height = self.winfo_height()
                
                # Đọc config hiện tại
                config = {}
                if os.path.exists("config.json"):
                    with open("config.json", 'r', encoding='utf-8') as f:
                        config = json.load(f)
                
                # Cập nhật kích thước cửa sổ
                config['window_width'] = current_width
                config['window_height'] = current_height
                
                # Lưu config
                with open("config.json", 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Lỗi lưu cấu hình cửa sổ: {e}")
            
            # Dừng ghi âm nếu đang chạy
            if self.is_recording and hasattr(self, 'audio_handler'):
                self.audio_handler.stop_recording()
            
            # Xóa toàn bộ file trong folder temp
            self.cleanup_temp_folder()
            
            self.quit_app()
    
    def cleanup_temp_folder(self):
        """Xóa tất cả file trong folder temp"""
        try:
            if os.path.exists(self.temp_folder):
                # Xóa tất cả file trong folder
                for filename in os.listdir(self.temp_folder):
                    file_path = os.path.join(self.temp_folder, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                            print(f"🗑️ Đã xóa: {filename}")
                    except Exception as e:
                        print(f"❌ Lỗi xóa {filename}: {e}")
                print(f"✅ Đã dọn dẹp folder temp")
        except Exception as e:
            print(f"❌ Lỗi cleanup temp folder: {e}")
            
    def load_config(self):
        """Load cấu hình từ file"""
        config_file = "config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.api_key = config.get('api_key', '')
                    self.azure_api_key = config.get('azure_api_key', '')
                    self.azure_region = config.get('azure_region', 'southeastasia')
                    self.cloudconvert_api_key = config.get('cloudconvert_api_key', '')
                    self.gemini_model = config.get('gemini_model', 'gemini-2.0-flash')
                    self.current_prompt = config.get('prompt', '')
                    self.window_width = config.get('window_width', 1280)
                    self.window_height = config.get('window_height', 800)
                print(f"✅ Loaded config from {config_file}")
            except json.JSONDecodeError as e:
                print(f"❌ Lỗi parse JSON: {e}")
                print(f"   File config.json có thể bị hỏng, sẽ sử dụng cấu hình mặc định")
            except Exception as e:
                print(f"❌ Lỗi load config: {e}")
        else:
            print(f"⚠️ File {config_file} không tồn tại, sẽ tạo mới khi lưu config")
                
    def save_config(self):
        """Lưu cấu hình vào file"""
        config = {
            'api_key': self.api_key,
            'azure_api_key': self.azure_api_key,
            'azure_region': self.azure_region,
            'cloudconvert_api_key': self.cloudconvert_api_key,
            'gemini_model': self.gemini_model,
            'prompt': self.prompt_text.get("1.0", "end-1c").strip() if hasattr(self, 'prompt_text') else '',
            'window_width': getattr(self, 'window_width', 1280),
            'window_height': getattr(self, 'window_height', 800)
        }
        try:
            with open("config.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved config to config.json")
        except Exception as e:
            print(f"❌ Lỗi save config: {e}")
            messagebox.showerror("Error", f"Không thể lưu config:\n{str(e)}")
    
    # ===== AUDIO METHODS =====
    
    def _init_cloudconvert_handler(self) -> bool:
        """Khởi tạo CloudConvert Handler"""
        try:
            api_key = self.cloudconvert_entry.get().strip()
            if not api_key:
                self.log_output("❌ Vui lòng nhập CloudConvert API Key!\n")
                return False
            
            self.cloudconvert_handler = CloudConvertHandler(api_key)
            is_valid, msg = self.cloudconvert_handler.validate_credentials()
            self.log_output(f"{msg}\n")
            return is_valid
        except Exception as e:
            self.log_output(f"❌ Lỗi khởi tạo CloudConvert: {str(e)}\n")
            return False
    
    def _init_audio_handler(self) -> bool:
        """Khởi tạo Audio Handler"""
        try:
            self.azure_api_key = self.azure_entry.get().strip()
            self.azure_region = self.azure_region_selector.get().strip()
            
            if not self.azure_api_key:
                self.log_output("❌ Vui lòng nhập Azure API Key!\n")
                return False
            
            if not self.azure_region:
                self.log_output("❌ Vui lòng chọn Azure Region!\n")
                return False
            
            # Tạo AudioHandler với region và temp folder
            self.audio_handler = AudioHandler(self.azure_api_key, self.azure_region, self.temp_folder)
            is_valid, msg = self.audio_handler.validate_azure_credentials()
            self.log_output(f"{msg}\n")
            self.log_output(f"📍 Region: {self.azure_region}\n")
            return is_valid
        except Exception as e:
            self.log_output(f"❌ Lỗi khởi tạo Audio Handler: {str(e)}\n")
            return False
    
    def start_recording(self):
        """Bắt đầu ghi âm"""
        if self.is_recording:
            self.log_output("⚠️ Đang ghi âm...\n")
            return
        
        if not self._init_audio_handler():
            return
        
        self.is_recording = True
        success, msg = self.audio_handler.start_recording()
        self.log_output(f"{msg}\n")
    
    def stop_recording(self):
        """Dừng ghi âm"""
        if not self.is_recording:
            self.log_output("❌ Không có quá trình ghi âm!\n")
            return
        
        self.is_recording = False
        success, msg, file_path = self.audio_handler.stop_recording()
        self.log_output(f"{msg}\n")
        
        if success and file_path:
            # Tự động chuyển đổi sau khi ghi xong
            threading.Thread(target=self._transcribe_file_thread, args=(file_path,), daemon=True).start()
    
    def upload_audio_file(self):
        """Upload file âm thanh"""
        if not self._init_audio_handler():
            return
        
        file_path = filedialog.askopenfilename(
            title="Chọn file âm thanh",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.m4a *.flac"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        self.log_output(f"📂 Đã chọn file: {file_path}\n")
        threading.Thread(target=self._transcribe_file_thread, args=(file_path,), daemon=True).start()
    
    def _transcribe_file_thread(self, file_path):
        """Chuyên đổi file âm thanh (chạy trong thread)"""
        try:
            self.log_output("🔄 Đang chuyển đổi âm thanh sang text...\n")
            success, result = self.audio_handler.transcribe_audio_file(file_path)
            
            if success:
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.log_output(f"\n✅ [{timestamp}] Kết quả chuyển đổi:\n")
                self.log_output("-" * 60 + "\n")
                self.log_output(f"{result}\n")
                self.log_output("-" * 60 + "\n\n")
                
                # Lưu vào folder speechtotext_output trong temp
                stt_folder = os.path.join(os.path.dirname(__file__), "temp", "speechtotext_output")
                os.makedirs(stt_folder, exist_ok=True)
                
                # Tạo tên file từ timestamp
                timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_file = os.path.join(stt_folder, f"{base_name}_{timestamp_file}.txt")
                
                # Lưu transcript ra file
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"Transcription Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Source File: {file_path}\n")
                    f.write("-" * 60 + "\n\n")
                    f.write(result)
                
                self.log_output(f"💾 Saved to: {output_file}\n\n")
                
                # Lưu vào lịch sử
                self.history.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "audio",
                    "file": file_path,
                    "result": result,
                    "output_file": output_file
                })
                
                # Hỏi mở folder - dùng after() để chạy trong main thread
                def show_dialog():
                    result_dialog = messagebox.askquestion(
                        "Transcription Complete",
                        f"✅ Transcription saved!\n\n"
                        f"File: {os.path.basename(output_file)}\n"
                        f"Location: {stt_folder}\n\n"
                        f"Open output folder?",
                        icon='info'
                    )
                    
                    if result_dialog == 'yes':
                        self.open_folder(stt_folder)
                
                self.after(0, show_dialog)
                    
            else:
                self.log_output(f"{result}\n")
        except Exception as e:
            self.log_output(f"❌ Lỗi: {str(e)}\n")
    
    def transcribe_realtime(self):
        """Chuyển đổi âm thanh realtime từ microphone"""
        if not self._init_audio_handler():
            return
        
        def callback(result):
            self.log_output(f"🎤 Kết quả: {result}\n")
        
        self.log_output("🎤 Bắt đầu lắng nghe từ microphone (30s)...\n")
        threading.Thread(
            target=self.audio_handler.transcribe_audio_realtime,
            args=("vi-VN", callback),
            daemon=True
        ).start()
    
    def update_format_options(self, selected_category=None):
        """Cập nhật format options dựa vào category được chọn"""
        # Khởi tạo UniversalConverter nếu chưa có
        if not hasattr(self, 'universal_converter') or self.universal_converter is None:
            self.universal_converter = UniversalConverter("")
        
        category = selected_category or self.category_selector.get()
        category_map = {
            "Audio": "audio",
            "Image": "image", 
            "Document": "document",
            "Video": "video"
        }
        
        category_key = category_map.get(category, "audio")
        formats = self.universal_converter.get_supported_formats(category_key)
        format_list = formats.get(category_key, ["mp3"])
        
        # Cập nhật danh sách format và set format đầu tiên
        self.output_format_selector.configure(values=format_list)
        if format_list:
            self.output_format_selector.set(format_list[0])
        
        self.log_convert_output(f"📂 Category: {category} → {len(format_list)} formats available\n")
    
    def select_file_to_convert(self):
        """Chọn file để convert - hỗ trợ nhiều loại file"""
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Chọn file để chuyển đổi",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.m4a *.aac *.ogg *.flac *.wma *.opus *.alac *.aiff"),
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff *.svg *.ico *.heic"),
                ("Document files", "*.pdf *.doc *.docx *.xls *.xlsx *.ppt *.pptx *.txt *.rtf *.odt"),
                ("Video files", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.mpeg *.mpg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            # Lưu file path và hiển thị tên file
            self.selected_convert_file = file_path
            file_name = os.path.basename(file_path)
            self.selected_file_label.configure(text=f"✅ {file_name}", text_color="#2CC985")
            
            # Auto-detect category và cập nhật dropdown
            if not hasattr(self, 'universal_converter'):
                self.universal_converter = UniversalConverter("")
            
            ext = os.path.splitext(file_path)[1]
            category = self.universal_converter.get_category(ext)
            
            category_display = {
                "audio": "Audio",
                "image": "Image",
                "document": "Document",
                "video": "Video"
            }
            
            if category in category_display:
                self.category_selector.set(category_display[category])
                self.update_format_options(category_display[category])
        else:
            self.selected_convert_file = None
            self.selected_file_label.configure(text="No file selected", text_color="#888888")
    
    def log_convert_output(self, message: str):
        """Ghi log vào conversion output area"""
        if hasattr(self, 'convert_output_text'):
            self.convert_output_text.insert("end", message)
            self.convert_output_text.see("end")
    
    def start_conversion(self):
        """Bắt đầu convert file - Universal Converter"""
        if not hasattr(self, 'selected_convert_file') or not self.selected_convert_file:
            messagebox.showwarning("No File", "Vui lòng chọn file trước!")
            return
        
        # Khởi tạo Universal Converter
        api_key = self.cloudconvert_entry.get().strip()
        if not api_key:
            self.log_convert_output("❌ Vui lòng nhập CloudConvert API Key!\n")
            return
        
        self.universal_converter = UniversalConverter(api_key)
        is_valid, msg = self.universal_converter.validate_credentials()
        
        if not is_valid:
            self.log_convert_output(f"{msg}\n")
            return
        
        # Lấy format từ dropdown
        output_format = self.output_format_selector.get().strip().lower()
        file_path = self.selected_convert_file
        
        # Log vào convert output area
        file_name = os.path.basename(file_path)
        self.log_convert_output(f"📂 Selected: {file_name}\n")
        self.log_convert_output(f"🎯 Format: {output_format}\n")
        self.log_convert_output(f"⏳ Starting conversion...\n")
        self.log_convert_output(f"{'-'*50}\n")
        
        # Chạy trong thread
        threading.Thread(
            target=self._convert_file_thread_universal,
            args=(file_path, output_format),
            daemon=True
        ).start()
    
    def _convert_file_thread_universal(self, file_path, output_format):
        """Thread để convert file bằng Universal Converter"""
        try:
            self.log_convert_output(f"📤 Uploading to CloudConvert...\n")
            
            # Convert bằng Universal Converter
            success, message, output_file = self.universal_converter.convert_file(
                file_path,
                output_format
            )
            
            if success:
                timestamp = datetime.now().strftime("%H:%M:%S")
                file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
                
                self.log_convert_output(f"\n✅ [{timestamp}] {message}\n")
                self.log_convert_output(f"📁 Output: {os.path.basename(output_file)}\n")
                self.log_convert_output(f"📂 Location: {os.path.dirname(output_file)}\n")
                self.log_convert_output(f"� Size: {file_size:.2f} MB\n")
                self.log_convert_output(f"{'-'*50}\n\n")
                
                # Show success message và mở file location
                def show_dialog():
                    result = messagebox.askyesno(
                        "Conversion Complete",
                        f"✅ File converted successfully!\n\n"
                        f"Output: {os.path.basename(output_file)}\n"
                        f"Size: {file_size:.2f} MB\n\n"
                        f"Open file location?",
                        icon='info'
                    )
                    
                    if result:
                        # Mở file location và select file đó
                        subprocess.run(['explorer', '/select,', output_file], check=False)
                
                self.after(0, show_dialog)
            else:
                self.log_convert_output(f"\n{message}\n")
                self.log_convert_output(f"{'-'*50}\n\n")
                
        except Exception as e:
            self.log_convert_output(f"❌ Error: {str(e)}\n")
            self.log_convert_output(f"{'-'*50}\n\n")
    
    def convert_file(self):
        """Chuyển đổi format file âm thanh (OLD - giữ lại để tương thích)"""
        if not self._init_cloudconvert_handler():
            return
        
        # Hiển thị hộp thoại chọn file (với parent để không bị che)
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Chọn file âm thanh để chuyển đổi",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.m4a *.aac *.ogg *.flac *.wma *.opus *.alac *.aiff"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            self.log_output("❌ Không có file nào được chọn.\n")
            return
        
        # Hiển thị hộp thoại chọn format đầu ra
        supported_formats = ["mp3", "wav", "m4a", "aac", "ogg", "flac", "wma", "opus", "alac", "aiff"]
        output_format = simpledialog.askstring(
            "Chọn format đầu ra",
            f"Nhập format output:\n\n{', '.join(supported_formats)}\n\n(mặc định: mp3)",
            parent=self
        )
        
        if not output_format:
            return
        
        output_format = output_format.strip().lower()
        if not output_format:
            output_format = "mp3"
        
        if output_format not in supported_formats:
            self.log_output(f"❌ Format '{output_format}' không được hỗ trợ!\n")
            self.log_output(f"Các format hỗ trợ: {', '.join(supported_formats)}\n")
            return
        
        # Tạo tên file output
        file_name = os.path.basename(file_path)
        file_base = os.path.splitext(file_name)[0]
        output_file = os.path.join(os.path.dirname(file_path), f"{file_base}_converted.{output_format}")
        
        self.log_output(f"📂 Chuyển đổi: {file_name} → .{output_format}\n")
        self.log_output(f"🔄 Đang xử lý...\n")
        
        # Chạy trong thread để không block UI
        threading.Thread(
            target=self._convert_file_thread,
            args=(file_path, output_format, output_file),
            daemon=True
        ).start()
    
    def _convert_file_thread(self, file_path, output_format, output_file):
        """Chuyển đổi file âm thanh (chạy trong thread)"""
        try:
            self.log_convert_output(f"📤 Uploading file to CloudConvert...\n")
            
            success, result = self.cloudconvert_handler.convert_file(
                file_path,
                output_format,
                output_file
            )
            
            if success:
                timestamp = datetime.now().strftime("%H:%M:%S")
                file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
                output_folder = os.path.dirname(output_file)
                
                self.log_convert_output(f"\n✅ [{timestamp}] Conversion successful!\n")
                self.log_convert_output(f"📁 Output: {os.path.basename(output_file)}\n")
                self.log_convert_output(f"📂 Location: {output_folder}\n")
                self.log_convert_output(f"💾 Size: {file_size:.2f} MB\n")
                self.log_convert_output(f"{'-'*50}\n\n")
                
                # Show success message - dùng after() để chạy trong main thread
                def show_dialog():
                    result = messagebox.askquestion(
                        "Conversion Complete",
                        f"✅ File converted successfully!\n\n"
                        f"Output: {os.path.basename(output_file)}\n"
                        f"Location: {output_folder}\n"
                        f"Size: {file_size:.2f} MB\n\n"
                        f"Open output folder?",
                        icon='info'
                    )
                    
                    if result == 'yes':
                        self.open_folder(output_folder)
                
                self.after(0, show_dialog)
                    
            else:
                self.log_convert_output(f"\n❌ Error: {result}\n")
                self.log_convert_output(f"{'-'*50}\n\n")
        except Exception as e:
            self.log_convert_output(f"\n❌ Conversion error: {str(e)}\n")
            self.log_convert_output(f"{'-'*50}\n\n")
    
    def open_folder(self, folder_path):
        """Mở folder trong Windows Explorer"""
        try:
            if os.path.exists(folder_path):
                os.startfile(folder_path)
            else:
                messagebox.showwarning("Folder Not Found", f"Folder không tồn tại:\n{folder_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Không thể mở folder:\n{str(e)}")
    
    def open_convert_output_folder(self):
        """Mở folder temp với subfolders"""
        temp_base = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(temp_base, exist_ok=True)
        self.open_folder(temp_base)
    
    def open_stt_output_folder(self):
        """Mở folder speechtotext_output trong temp"""
        stt_folder = os.path.join(os.path.dirname(__file__), "temp", "speechtotext_output")
        os.makedirs(stt_folder, exist_ok=True)
        self.open_folder(stt_folder)


def main():
    """Hàm main"""
    app = ScreenCaptureGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
