"""
CloudConvert File Conversion Handler
Chuyển đổi file âm thanh/video sử dụng CloudConvert API
"""

import requests
import time
import os


class CloudConvertHandler:
    """Xử lý chuyển đổi file bằng CloudConvert API"""
    
    def __init__(self, api_key: str):
        """
        Khởi tạo CloudConvert Handler
        
        Args:
            api_key: CloudConvert API key
        """
        self.api_key = api_key
        self.base_url = "https://api.cloudconvert.com/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def validate_credentials(self) -> tuple[bool, str]:
        """
        Kiểm tra API credentials
        
        Returns:
            Tuple (is_valid: bool, message: str)
        """
        try:
            if not self.api_key or len(self.api_key) < 10:
                return False, "❌ CloudConvert API Key không hợp lệ"
            
            # Không test API ngay, chỉ check format
            # Test thực tế sẽ được thực hiện khi convert
            if self.api_key.startswith("eyJ"):  # JWT token format
                return True, "✅ CloudConvert API Key đã được thiết lập"
            else:
                return True, "⚠️ CloudConvert API Key đã được thiết lập (chưa xác thực)"
                
        except Exception as e:
            return False, f"❌ Lỗi kiểm tra credentials: {str(e)}"
    
    def convert_file(self, input_file: str, output_format: str, 
                    output_file: str = None) -> tuple[bool, str]:
        """
        Chuyển đổi file
        
        Args:
            input_file: Đường dẫn file input
            output_format: Format output (mp3, wav, m4a, ogg, flac, etc.)
            output_file: Đường dẫn file output (nếu None, auto-generate)
            
        Returns:
            Tuple (success: bool, result_path_or_error: str)
        """
        try:
            # Kiểm tra file input
            if not os.path.exists(input_file):
                return False, f"❌ File không tồn tại: {input_file}"
            
            # Get input format
            input_ext = os.path.splitext(input_file)[1].lstrip('.')
            
            # Generate output file path nếu không được cung cấp
            if output_file is None:
                base_name = os.path.splitext(input_file)[0]
                output_file = f"{base_name}.{output_format}"
            
            print(f"🔄 Đang chuyển đổi {input_ext} → {output_format}...")
            
            # Create conversion task
            task_data = {
                "tasks": {
                    "import-1": {
                        "operation": "import/upload",
                        "file": open(input_file, 'rb')
                    },
                    "convert-1": {
                        "operation": "convert",
                        "input": "import-1",
                        "output_format": output_format
                    },
                    "export-1": {
                        "operation": "export/url",
                        "input": "convert-1"
                    }
                }
            }
            
            # Submit job
            files = {
                'file': open(input_file, 'rb')
            }
            data = {
                'tasks': str(task_data)
            }
            
            # Simplified approach - use direct conversion
            return self._direct_convert(input_file, output_format, output_file)
            
        except Exception as e:
            return False, f"❌ Lỗi chuyển đổi: {str(e)}"
    
    def _direct_convert(self, input_file: str, output_format: str, 
                       output_file: str) -> tuple[bool, str]:
        """
        Chuyển đổi file trực tiếp
        """
        try:
            # Create job
            job_data = {
                "tasks": {
                    "import-file": {
                        "operation": "import/upload",
                    },
                    "convert": {
                        "operation": "convert",
                        "input": ["import-file"],
                        "output_format": output_format
                    },
                    "export-file": {
                        "operation": "export/url",
                        "input": ["convert"]
                    }
                }
            }
            
            # Create job
            response = requests.post(
                f"{self.base_url}/jobs",
                headers=self.headers,
                json=job_data
            )
            
            if response.status_code != 201:
                return False, f"❌ Failed to create job: {response.text}"
            
            job = response.json()
            job_id = job['data']['id']
            
            # Upload file
            upload_task = job['data']['tasks'][0]
            upload_url = upload_task.get('result', {}).get('form', {}).get('url')
            upload_parameters = upload_task.get('result', {}).get('form', {}).get('parameters', {})
            
            if not upload_url:
                # Retry job creation
                return False, "❌ Không thể lấy URL upload"
            
            print(f"📤 Uploading file to: {upload_url}")
            
            # CloudConvert requires specific upload format
            with open(input_file, 'rb') as f:
                # Include all form parameters from CloudConvert
                files = {'file': (os.path.basename(input_file), f)}
                upload_response = requests.post(upload_url, files=files, data=upload_parameters)
            
            print(f"📤 Upload status: {upload_response.status_code}")
            if upload_response.status_code not in [200, 201]:
                error_msg = upload_response.text if upload_response.text else "Unknown error"
                return False, f"❌ Upload failed (status {upload_response.status_code}): {error_msg}"
            
            print(f"✅ Upload complete!")
            
            # Wait for conversion with optimized polling
            print(f"⏳ Converting...")
            
            # Polling strategy: fast at start, slower later
            # First 10 attempts: 0.5s interval (total 5s)
            # Next 20 attempts: 1s interval (total 20s)
            # Last 30 attempts: 2s interval (total 60s)
            # Max total: ~85 seconds
            
            wait_times = [0.5] * 10 + [1.0] * 20 + [2.0] * 30
            
            for attempt, wait_time in enumerate(wait_times):
                status_response = requests.get(
                    f"{self.base_url}/jobs/{job_id}",
                    headers=self.headers
                )
                
                if status_response.status_code != 200:
                    print(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(wait_time)
                    continue
                
                job_status = status_response.json()['data']
                current_status = job_status.get('status')
                
                if current_status == 'finished':
                    # Get export URL
                    export_task = None
                    for task in job_status.get('tasks', []):
                        if task.get('operation') == 'export/url':
                            export_task = task
                            break
                    
                    if not export_task:
                        return False, "❌ Cannot find export task"
                    
                    download_url = export_task.get('result', {}).get('files', [{}])[0].get('url')
                    
                    if download_url:
                        print(f"📥 Downloading result...")
                        file_response = requests.get(download_url, stream=True)
                        
                        if file_response.status_code == 200:
                            with open(output_file, 'wb') as f:
                                for chunk in file_response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            
                            print(f"✅ Conversion successful: {output_file}")
                            return True, output_file
                        else:
                            return False, f"❌ Download failed: {file_response.status_code}"
                    else:
                        return False, "❌ No download URL found"
                
                elif current_status == 'error':
                    error_tasks = [t for t in job_status.get('tasks', []) if t.get('status') == 'error']
                    if error_tasks:
                        error_msg = error_tasks[0].get('message', 'Unknown error')
                        return False, f"❌ Conversion error: {error_msg}"
                    return False, "❌ Conversion failed"
                
                # Show progress for every 5th attempt
                if attempt % 5 == 0:
                    print(f"⏳ Processing... ({attempt + 1}/{len(wait_times)}) - Status: {current_status}")
                
                time.sleep(wait_time)
            
            return False, "❌ Conversion timeout (exceeded 85 seconds)"
            
            return False, "❌ Conversion timeout"
            
        except Exception as e:
            return False, f"❌ Lỗi: {str(e)}"
    
    def get_supported_formats(self) -> list:
        """
        Lấy danh sách format được hỗ trợ
        
        Returns:
            List of supported formats
        """
        supported = [
            "mp3", "wav", "m4a", "aac", "ogg", "flac", "wma",
            "opus", "alac", "aiff", "au", "raw"
        ]
        return supported
