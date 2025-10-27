"""
Universal File Converter Handler
Hỗ trợ convert: Audio, Image, Document (PDF, Word, Excel)
Sử dụng CloudConvert API
"""

import os
import requests
import time
from typing import Tuple, Dict

class UniversalConverter:
    def __init__(self, api_key: str):
        """
        Khởi tạo Universal Converter
        
        Args:
            api_key: CloudConvert API key
        """
        self.api_key = api_key
        self.base_url = "https://api.cloudconvert.com/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Tạo temp folder structure
        self.temp_base = os.path.join(os.path.dirname(__file__), "temp")
        self.temp_folders = {
            "audio": os.path.join(self.temp_base, "audio"),
            "image": os.path.join(self.temp_base, "image"),
            "document": os.path.join(self.temp_base, "document"),
            "video": os.path.join(self.temp_base, "video")
        }
        
        # Tạo tất cả folders
        for folder in self.temp_folders.values():
            os.makedirs(folder, exist_ok=True)
    
    def get_category(self, file_extension: str) -> str:
        """Xác định category dựa vào extension"""
        ext = file_extension.lower().replace('.', '')
        
        audio_formats = ['mp3', 'wav', 'm4a', 'aac', 'ogg', 'flac', 'wma', 'opus', 'alac', 'aiff']
        image_formats = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff', 'svg', 'ico', 'heic']
        document_formats = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'rtf', 'odt']
        video_formats = ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm', 'mpeg', 'mpg']
        
        if ext in audio_formats:
            return "audio"
        elif ext in image_formats:
            return "image"
        elif ext in document_formats:
            return "document"
        elif ext in video_formats:
            return "video"
        else:
            return "unknown"
    
    def get_output_folder(self, category: str) -> str:
        """Lấy output folder theo category"""
        return self.temp_folders.get(category, self.temp_base)
    
    def validate_credentials(self) -> Tuple[bool, str]:
        """
        Kiểm tra API key có hợp lệ không
        
        Returns:
            Tuple[bool, str]: (valid, message)
        """
        try:
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                username = data.get('data', {}).get('username', 'Unknown')
                return True, f"✅ CloudConvert API connected: {username}"
            else:
                return False, f"❌ Invalid API key: {response.status_code}"
                
        except Exception as e:
            return False, f"❌ Connection error: {str(e)}"
    
    def convert_file(self, input_file: str, output_format: str) -> Tuple[bool, str, str]:
        """
        Convert file sang format khác
        
        Args:
            input_file: Đường dẫn file input
            output_format: Format output (mp3, png, pdf, etc.)
        
        Returns:
            Tuple[bool, str, str]: (success, message, output_file_path)
        """
        try:
            # Xác định category
            input_ext = os.path.splitext(input_file)[1]
            category = self.get_category(input_ext)
            output_category = self.get_category(f".{output_format}")
            
            if category == "unknown":
                return False, f"❌ Unsupported input format: {input_ext}", ""
            
            # Tạo tên file output
            basename = os.path.splitext(os.path.basename(input_file))[0]
            output_folder = self.get_output_folder(output_category)
            output_file = os.path.join(output_folder, f"{basename}.{output_format}")
            
            # Step 1: Create job
            job_data = {
                "tasks": {
                    "import-file": {
                        "operation": "import/upload"
                    },
                    "convert-file": {
                        "operation": "convert",
                        "input": "import-file",
                        "output_format": output_format
                    },
                    "export-file": {
                        "operation": "export/url",
                        "input": "convert-file"
                    }
                }
            }
            
            response = requests.post(
                f"{self.base_url}/jobs",
                headers=self.headers,
                json=job_data,
                timeout=10
            )
            
            if response.status_code != 201:
                return False, f"❌ Failed to create job: {response.text}", ""
            
            job = response.json()
            job_id = job['data']['id']
            
            # Step 2: Upload file
            upload_task = next(t for t in job['data']['tasks'] if t['name'] == 'import-file')
            upload_url = upload_task['result']['form']['url']
            upload_params = upload_task['result']['form']['parameters']
            
            with open(input_file, 'rb') as f:
                files = {'file': f}
                upload_response = requests.post(
                    upload_url,
                    data=upload_params,
                    files=files,
                    timeout=60
                )
            
            if upload_response.status_code not in [200, 201]:
                return False, f"❌ Upload failed: {upload_response.status_code}", ""
            
            # Step 3: Wait for conversion
            max_wait = 300  # 5 minutes
            wait_time = 0
            
            while wait_time < max_wait:
                job_response = requests.get(
                    f"{self.base_url}/jobs/{job_id}",
                    headers=self.headers,
                    timeout=10
                )
                
                if job_response.status_code != 200:
                    return False, f"❌ Failed to check status", ""
                
                job_status = job_response.json()
                status = job_status['data']['status']
                
                if status == 'finished':
                    # Get download URL
                    export_task = next(t for t in job_status['data']['tasks'] if t['name'] == 'export-file')
                    download_url = export_task['result']['files'][0]['url']
                    
                    # Download file
                    download_response = requests.get(download_url, timeout=60)
                    with open(output_file, 'wb') as f:
                        f.write(download_response.content)
                    
                    file_size = os.path.getsize(output_file) / 1024 / 1024  # MB
                    return True, f"✅ Converted successfully! ({file_size:.2f} MB)", output_file
                
                elif status == 'error':
                    error_msg = job_status['data'].get('message', 'Unknown error')
                    return False, f"❌ Conversion failed: {error_msg}", ""
                
                time.sleep(2)
                wait_time += 2
            
            return False, "❌ Conversion timeout (5 minutes)", ""
            
        except Exception as e:
            return False, f"❌ Error: {str(e)}", ""

    def get_supported_formats(self, category: str = None) -> Dict[str, list]:
        """
        Lấy danh sách formats được hỗ trợ
        
        Args:
            category: Loại file (audio, image, document, video)
        
        Returns:
            Dict với key là category và value là list formats
        """
        formats = {
            "audio": [
                "mp3", "wav", "m4a", "aac", "ogg", "flac", 
                "wma", "opus", "alac", "aiff", "amr", "ape"
            ],
            "image": [
                "jpg", "jpeg", "png", "gif", "bmp", "webp",
                "tiff", "svg", "ico", "heic", "avif", "jxl"
            ],
            "document": [
                "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
                "txt", "rtf", "odt", "ods", "odp", "pages", "numbers"
            ],
            "video": [
                "mp4", "avi", "mkv", "mov", "wmv", "flv",
                "webm", "mpeg", "mpg", "3gp", "m4v"
            ]
        }
        
        if category:
            return {category: formats.get(category, [])}
        return formats
