# Compact UI for File Conversion Section
# This is the replacement code for create_convert_section method

import customtkinter as ctk

def create_convert_section(self, parent):
    """Tạo phần File Conversion với UI compact"""
    
    # Main Control Frame - compact
    control_frame = ctk.CTkFrame(parent, fg_color="#2B2B2B", corner_radius=8)
    control_frame.pack(fill="x", padx=15, pady=(10, 10))
    
    # Horizontal layout for all controls
    row_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
    row_frame.pack(fill="x", padx=10, pady=10)
    
    # Column 1: File Selection (35% width)
    col1 = ctk.CTkFrame(row_frame, fg_color="transparent")
    col1.pack(side="left", fill="both", expand=True, padx=(0, 5))
    
    ctk.CTkLabel(col1, text="📁 File:", font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w")
    
    self.selected_file_label = ctk.CTkLabel(
        col1,
        text="No file selected",
        font=ctk.CTkFont(size=9),
        text_color="#888888",
        anchor="w"
    )
    self.selected_file_label.pack(fill="x", pady=(2, 5))
    
    ctk.CTkButton(
        col1,
        text="Browse",
        command=self.select_file_to_convert,
        height=32,
        font=ctk.CTkFont(size=11),
        fg_color="#3498DB",
        hover_color="#2980B9"
    ).pack(fill="x")
    
    # Column 2: Category (20% width)
    col2 = ctk.CTkFrame(row_frame, fg_color="transparent", width=150)
    col2.pack(side="left", padx=5)
    col2.pack_propagate(False)
    
    ctk.CTkLabel(col2, text="Category:", font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w")
    self.category_selector = ctk.CTkComboBox(
        col2,
        values=["Audio", "Image", "Document", "Video"],
        height=32,
        font=ctk.CTkFont(size=11),
        command=self.update_format_options
    )
    self.category_selector.pack(fill="x", pady=(2, 0))
    self.category_selector.set("Audio")
    
    # Column 3: Format (20% width)
    col3 = ctk.CTkFrame(row_frame, fg_color="transparent", width=130)
    col3.pack(side="left", padx=5)
    col3.pack_propagate(False)
    
    ctk.CTkLabel(col3, text="Format:", font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w")
    self.output_format_selector = ctk.CTkComboBox(
        col3,
        values=["mp3", "wav", "m4a", "aac", "ogg", "flac"],
        height=32,
        font=ctk.CTkFont(size=11)
    )
    self.output_format_selector.pack(fill="x", pady=(2, 0))
    self.output_format_selector.set("mp3")
    
    # Column 4: Actions (25% width)
    col4 = ctk.CTkFrame(row_frame, fg_color="transparent", width=140)
    col4.pack(side="left", padx=(5, 0))
    col4.pack_propagate(False)
    
    ctk.CTkButton(
        col4,
        text="✨ Convert",
        command=self.start_conversion,
        height=35,
        font=ctk.CTkFont(size=12, weight="bold"),
        fg_color="#2CC985",
        hover_color="#25A866"
    ).pack(fill="x", pady=(17, 3))
    
    ctk.CTkButton(
        col4,
        text="📂 Folder",
        command=self.open_convert_output_folder,
        height=28,
        font=ctk.CTkFont(size=10),
        fg_color="#4A90E2",
        hover_color="#357ABD"
    ).pack(fill="x")
    
    # Conversion Log/Output Area - tăng không gian
    log_frame = ctk.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=8)
    log_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
    
    # Header with Clear button - compact
    log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
    log_header.pack(fill="x", padx=10, pady=(8, 5))
    
    ctk.CTkLabel(
        log_header,
        text="📋 Conversion Log",
        font=ctk.CTkFont(size=12, weight="bold")
    ).pack(side="left")
    
    ctk.CTkButton(
        log_header,
        text="Clear",
        command=lambda: self.convert_output_text.delete("1.0", "end"),
        height=24,
        width=60,
        font=ctk.CTkFont(size=10),
        fg_color="#3B3B3B",
        hover_color="#4B4B4B"
    ).pack(side="right")
    
    # Log output textbox - full expansion
    self.convert_output_text = ctk.CTkTextbox(
        log_frame,
        font=ctk.CTkFont(size=10),
        wrap="word",
        border_width=0
    )
    self.convert_output_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    # Welcome message - compact
    welcome_msg = """🎉 Universal File Converter
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ 49+ formats | 4 categories
📂 Output: temp/{category}/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    self.convert_output_text.insert("1.0", welcome_msg)
