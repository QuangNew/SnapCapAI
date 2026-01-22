"""
Resource Management Utilities
Context managers and utilities for proper resource cleanup.

Prevents memory leaks and ensures proper disposal of:
- Screenshots (PIL Image objects)
- File handles
- Temporary files
- API connections
"""

import os
import tempfile
import shutil
from contextlib import contextmanager
from typing import Optional, Generator
from PIL import Image


@contextmanager
def screenshot_context() -> Generator[Image.Image, None, None]:
    """
    Context manager for screenshot capture with automatic cleanup.
    
    Ensures PIL Image objects are properly closed to prevent memory leaks.
    
    Example:
        with screenshot_context() as screenshot:
            # Use screenshot
            api.analyze(screenshot)
        # Screenshot automatically closed here
    
    Yields:
        PIL.Image: Screenshot image object
    """
    from PIL import ImageGrab
    
    screenshot = None
    try:
        screenshot = ImageGrab.grab()
        yield screenshot
    finally:
        if screenshot:
            try:
                screenshot.close()
            except Exception:
                pass  # Ignore close errors
            finally:
                del screenshot  # Force garbage collection


@contextmanager
def temp_file_context(
    suffix: str = "",
    prefix: str = "snapcapai_",
    dir: Optional[str] = None,
    delete: bool = True
) -> Generator[str, None, None]:
    """
    Context manager for temporary files with automatic cleanup.
    
    Args:
        suffix: File extension (e.g., ".png", ".wav")
        prefix: Filename prefix
        dir: Directory for temp file (default: system temp)
        delete: Whether to delete file on exit
    
    Example:
        with temp_file_context(suffix=".wav") as temp_path:
            # Save audio to temp_path
            save_audio(temp_path)
            # Process file
            transcribe(temp_path)
        # File automatically deleted here
    
    Yields:
        str: Path to temporary file
    """
    temp_path = None
    try:
        fd, temp_path = tempfile.mkstemp(
            suffix=suffix,
            prefix=prefix,
            dir=dir
        )
        # Close file descriptor immediately (we just need the path)
        os.close(fd)
        
        yield temp_path
    
    finally:
        if temp_path and delete and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                print(f"Warning: Could not delete temp file {temp_path}: {e}")


@contextmanager
def temp_directory_context(
    suffix: str = "",
    prefix: str = "snapcapai_",
    dir: Optional[str] = None
) -> Generator[str, None, None]:
    """
    Context manager for temporary directories with automatic cleanup.
    
    Args:
        suffix: Directory name suffix
        prefix: Directory name prefix
        dir: Parent directory (default: system temp)
    
    Example:
        with temp_directory_context() as temp_dir:
            # Use temp_dir
            extract_files(temp_dir)
        # Directory and contents automatically deleted
    
    Yields:
        str: Path to temporary directory
    """
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(
            suffix=suffix,
            prefix=prefix,
            dir=dir
        )
        yield temp_dir
    
    finally:
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Warning: Could not delete temp directory {temp_dir}: {e}")


class SafeFileWriter:
    """
    Safe file writer that uses atomic writes.
    
    Writes to a temporary file first, then atomically renames to target.
    Prevents partial/corrupted files if write fails.
    
    Example:
        with SafeFileWriter("config.json") as f:
            json.dump(data, f)
        # File atomically written
    """
    
    def __init__(self, target_path: str, mode: str = 'w', encoding: str = 'utf-8'):
        """
        Initialize safe file writer.
        
        Args:
            target_path: Final destination path
            mode: File open mode ('w' or 'wb')
            encoding: Text encoding (for text mode)
        """
        self.target_path = target_path
        self.mode = mode
        self.encoding = encoding if 'b' not in mode else None
        self.temp_path = None
        self.file_handle = None
    
    def __enter__(self):
        """Open temporary file for writing."""
        # Create temp file in same directory as target
        # (ensures atomic rename works on same filesystem)
        target_dir = os.path.dirname(self.target_path) or '.'
        target_name = os.path.basename(self.target_path)
        
        fd, self.temp_path = tempfile.mkstemp(
            dir=target_dir,
            prefix=f".{target_name}.",
            suffix=".tmp"
        )
        
        # Open temp file
        if 'b' in self.mode:
            self.file_handle = os.fdopen(fd, self.mode)
        else:
            self.file_handle = os.fdopen(fd, self.mode, encoding=self.encoding)
        
        return self.file_handle
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close file and atomically rename if successful."""
        # Close file handle
        if self.file_handle:
            self.file_handle.close()
        
        # If no exception, atomically rename temp to target
        if exc_type is None and self.temp_path:
            try:
                # Atomic rename (Windows allows overwrite if dest exists)
                os.replace(self.temp_path, self.target_path)
            except Exception as e:
                # Cleanup temp file on rename failure
                if os.path.exists(self.temp_path):
                    os.unlink(self.temp_path)
                raise e
        else:
            # Exception occurred - cleanup temp file
            if self.temp_path and os.path.exists(self.temp_path):
                os.unlink(self.temp_path)
        
        return False  # Don't suppress exceptions


class ResourceTracker:
    """
    Track and cleanup resources automatically.
    
    Useful for long-running applications to prevent resource leaks.
    
    Example:
        tracker = ResourceTracker()
        
        img = Image.open("test.png")
        tracker.track(img, lambda: img.close())
        
        # Later...
        tracker.cleanup()  # Closes all tracked resources
    """
    
    def __init__(self):
        """Initialize resource tracker."""
        self._resources = []
    
    def track(self, resource, cleanup_func):
        """
        Track a resource with its cleanup function.
        
        Args:
            resource: The resource object
            cleanup_func: Function to call to cleanup resource
        """
        self._resources.append((resource, cleanup_func))
    
    def cleanup(self):
        """Cleanup all tracked resources."""
        errors = []
        
        for resource, cleanup_func in reversed(self._resources):
            try:
                cleanup_func()
            except Exception as e:
                errors.append((resource, e))
        
        self._resources.clear()
        
        if errors:
            print(f"Warning: {len(errors)} resource(s) failed to cleanup")
            for resource, error in errors:
                print(f"  - {resource}: {error}")
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on context exit."""
        self.cleanup()
        return False


# Utility functions

def safe_remove(path: str, ignore_errors: bool = True) -> bool:
    """
    Safely remove a file or directory.
    
    Args:
        path: Path to remove
        ignore_errors: If True, suppress exceptions
    
    Returns:
        bool: True if removed successfully, False otherwise
    """
    try:
        if os.path.isfile(path):
            os.unlink(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        return True
    except Exception as e:
        if not ignore_errors:
            raise
        return False


def cleanup_old_temp_files(
    directory: str,
    pattern: str = "snapcapai_*",
    age_hours: int = 24
) -> int:
    """
    Clean up old temporary files.
    
    Args:
        directory: Directory to search
        pattern: File pattern to match (glob)
        age_hours: Remove files older than this many hours
    
    Returns:
        int: Number of files removed
    """
    import glob
    import time
    
    removed = 0
    cutoff_time = time.time() - (age_hours * 3600)
    
    for path in glob.glob(os.path.join(directory, pattern)):
        try:
            if os.path.getmtime(path) < cutoff_time:
                if safe_remove(path):
                    removed += 1
        except Exception:
            pass
    
    return removed


# Demo/Test
if __name__ == "__main__":
    import json
    
    print("=" * 60)
    print("Resource Management Utilities Test")
    print("=" * 60)
    
    # Test 1: Screenshot context
    print("\n1. Testing screenshot_context...")
    with screenshot_context() as screenshot:
        print(f"   Screenshot size: {screenshot.size}")
        print(f"   Screenshot mode: {screenshot.mode}")
    print("   ✓ Screenshot automatically closed")
    
    # Test 2: Temp file context
    print("\n2. Testing temp_file_context...")
    with temp_file_context(suffix=".txt") as temp_path:
        print(f"   Temp file: {temp_path}")
        with open(temp_path, 'w') as f:
            f.write("Test data")
        print(f"   File exists: {os.path.exists(temp_path)}")
    print(f"   File exists after context: {os.path.exists(temp_path)}")
    
    # Test 3: Safe file writer
    print("\n3. Testing SafeFileWriter...")
    test_config = {"api_key": "test123", "model": "gemini-2.0-flash"}
    with SafeFileWriter("test_config.json") as f:
        json.dump(test_config, f, indent=2)
    
    with open("test_config.json") as f:
        loaded = json.load(f)
    print(f"   Written and loaded: {loaded}")
    os.remove("test_config.json")
    
    # Test 4: Resource tracker
    print("\n4. Testing ResourceTracker...")
    with ResourceTracker() as tracker:
        # Simulate resources
        resources = [f"resource_{i}" for i in range(3)]
        for res in resources:
            tracker.track(res, lambda r=res: print(f"   Cleaning up {r}"))
    print("   ✓ All resources cleaned")
    
    print("\n" + "=" * 60)
    print("All tests passed!")
