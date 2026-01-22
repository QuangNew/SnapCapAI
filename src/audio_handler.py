"""
Audio Handler Module - Xử lý ghi âm và chuyển đổi âm thanh sang text
"""

import os
import io
import json
import sounddevice as sd
import soundfile as sf
import threading
from datetime import datetime
import azure.cognitiveservices.speech as speechsdk


class AudioHandler:
    """Lớp xử lý âm thanh: ghi âm, upload, chuyển đổi sang text"""
    
    def __init__(self, azure_key: str, azure_region: str = "southeastasia", temp_folder: str = None):
        """
        Khởi tạo Audio Handler
        
        Args:
            azure_key: Azure Cognitive Services API Key
            azure_region: Vùng Azure (mặc định: southeastasia cho Việt Nam/Châu Á)
            temp_folder: Folder lưu file tạm (mặc định: ./temp)
        """
        self.azure_key = azure_key
        self.azure_region = azure_region
        self.is_recording = False
        self.audio_data = None
        self.sample_rate = 16000  # Tần số lấy mẫu
        
        # Tạo folder temp nếu chưa có
        if temp_folder:
            self.temp_folder = temp_folder
        else:
            self.temp_folder = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(self.temp_folder, exist_ok=True)
        self.temp_audio_file = None
        
    def validate_azure_credentials(self) -> tuple[bool, str]:
        """
        Kiểm tra credentials Azure
        
        Returns:
            Tuple (is_valid: bool, message: str)
        """
        try:
            if not self.azure_key:
                return False, "❌ Azure API Key không được để trống"
            if not self.azure_region:
                return False, "❌ Azure Region không được để trống"
            return True, "✅ Azure credentials hợp lệ"
        except Exception as e:
            return False, f"❌ Lỗi kiểm tra credentials: {str(e)}"
    
    def start_recording(self) -> tuple[bool, str]:
        """
        Bắt đầu ghi âm
        
        Returns:
            Tuple (success: bool, message: str)
        """
        try:
            self.is_recording = True
            self.audio_data = []
            print("🎤 Đang ghi âm...")
            
            def audio_callback(indata, frames, time, status):
                """Callback để nhận dữ liệu âm thanh"""
                if status:
                    print(f"⚠️ Audio callback status: {status}")
                self.audio_data.append(indata.copy())
            
            # Tạo stream ghi âm
            self.stream = sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                callback=audio_callback,
                blocksize=4096
            )
            self.stream.start()
            return True, "🎤 Đã bắt đầu ghi âm"
            
        except Exception as e:
            self.is_recording = False
            return False, f"❌ Lỗi ghi âm: {str(e)}"
    
    def stop_recording(self) -> tuple[bool, str, str]:
        """
        Dừng ghi âm
        
        Returns:
            Tuple (success: bool, message: str, file_path: str)
        """
        try:
            if not self.is_recording:
                return False, "❌ Không có quá trình ghi âm nào", ""
            
            self.is_recording = False
            self.stream.stop()
            self.stream.close()
            
            # Lưu file âm thanh vào folder temp
            if self.audio_data:
                import numpy as np
                audio_array = np.concatenate(self.audio_data, axis=0)
                
                # Tạo file trong folder temp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.temp_audio_file = os.path.join(self.temp_folder, f"recorded_{timestamp}.wav")
                
                sf.write(self.temp_audio_file, audio_array, self.sample_rate)
                print(f"✅ Đã lưu file: {self.temp_audio_file}")
                
                return True, f"✅ Đã dừng ghi âm ({len(audio_array)/self.sample_rate:.1f}s)", self.temp_audio_file
            else:
                return False, "❌ Không có dữ liệu âm thanh", ""
                
        except Exception as e:
            self.is_recording = False
            return False, f"❌ Lỗi dừng ghi âm: {str(e)}", ""
    
    def transcribe_audio_file(self, file_path: str, language: str = "vi-VN") -> tuple[bool, str]:
        """
        Chuyển đổi file âm thanh sang text sử dụng Azure
        
        Args:
            file_path: Đường dẫn file âm thanh
            language: Ngôn ngữ (mặc định: vi-VN cho Tiếng Việt)
            
        Returns:
            Tuple (success: bool, transcribed_text: str)
        """
        try:
            # Kiểm tra credentials
            is_valid, msg = self.validate_azure_credentials()
            if not is_valid:
                return False, msg
            
            # Kiểm tra file tồn tại
            if not os.path.exists(file_path):
                return False, f"❌ File không tồn tại: {file_path}"
            
            print(f"🔄 Đang chuyển đổi: {file_path}")
            
            # Cấu hình Azure Speech
            speech_config = speechsdk.SpeechConfig(
                subscription=self.azure_key,
                region=self.azure_region
            )
            speech_config.speech_recognition_language = language
            
            # Tạo recognizer từ file
            audio_config = speechsdk.audio.AudioConfig(filename=file_path)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            
            # Thực hiện nhận dạng
            result = recognizer.recognize_once()
            
            # Xử lý kết quả
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = result.text
                print(f"✅ Chuyển đổi thành công: {len(text)} ký tự")
                return True, text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                return False, "❌ Không tìm thấy lời nói trong file âm thanh"
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                error_msg = f"❌ Lỗi: {cancellation.reason}"
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    error_msg += f"\n{cancellation.error_details}"
                return False, error_msg
                
        except Exception as e:
            return False, f"❌ Lỗi chuyển đổi âm thanh: {str(e)}"
    
    def transcribe_audio_realtime(self, language: str = "vi-VN", callback=None) -> tuple[bool, str]:
        """
        Chuyển đổi âm thanh realtime sử dụng microphone
        
        Args:
            language: Ngôn ngữ (mặc định: vi-VN)
            callback: Hàm callback để xử lý kết quả
            
        Returns:
            Tuple (success: bool, transcribed_text: str)
        """
        try:
            # Kiểm tra credentials
            is_valid, msg = self.validate_azure_credentials()
            if not is_valid:
                return False, msg
            
            print("🎤 Đang lắng nghe từ microphone...")
            
            # Cấu hình Azure Speech
            speech_config = speechsdk.SpeechConfig(
                subscription=self.azure_key,
                region=self.azure_region
            )
            speech_config.speech_recognition_language = language
            
            # Sử dụng microphone mặc định
            audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            
            # Thực hiện nhận dạng
            result = recognizer.recognize_once()
            
            # Xử lý kết quả
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = result.text
                print(f"✅ Nhận dạng thành công: {len(text)} ký tự")
                if callback:
                    callback(text)
                return True, text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                msg = "❌ Không tìm thấy lời nói"
                if callback:
                    callback(msg)
                return False, msg
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                error_msg = f"❌ Lỗi: {cancellation.reason}"
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    error_msg += f"\n{cancellation.error_details}"
                if callback:
                    callback(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"❌ Lỗi nhận dạng realtime: {str(e)}"
            if callback:
                callback(error_msg)
            return False, error_msg
    
    def cleanup(self):
        """Xóa file tạm thời"""
        try:
            if self.temp_audio_file and os.path.exists(self.temp_audio_file):
                os.remove(self.temp_audio_file)
                print(f"🗑️ Đã xóa file tạm: {self.temp_audio_file}")
        except Exception as e:
            print(f"⚠️ Không thể xóa file tạm: {e}")
    
    def __del__(self):
        """Cleanup khi object bị xóa"""
        self.cleanup()
