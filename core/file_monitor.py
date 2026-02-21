
# core/file_monitor.py
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Callable, List

class DownloadHandler(FileSystemEventHandler):
    """处理下载文件夹的事件"""
    
    def __init__(self, on_file_complete: Callable):
        self.on_file_complete = on_file_complete
        self.processing_files = set()
    
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_file(event.src_path)
    
    def _handle_file(self, file_path: str):
        """处理新文件/修改的文件"""
        # 检查文件是否存在且稳定（大小不再变化）
        path = Path(file_path)
        for i in (".tmp", ".crdownload",".part"):
            if file_path.find(i) != -1:
                return

        if not path.exists() or  file_path in self.processing_files:
            return
        
        self.processing_files.add(file_path)
        
        try:
            self.on_file_complete(file_path)
        finally:
            self.processing_files.remove(file_path)

class FileMonitor:
    """监控下载文件夹"""
    
    def __init__(self, folders: List[str], supported_extensions: List[str]):
        self.folders = folders
        self.supported_extensions = supported_extensions
        self.observer = Observer()
        self.handler = None
    
    def start(self, on_file_detected: Callable):
        """开始监控文件夹"""
        self.handler = DownloadHandler(on_file_detected)
        
        for folder in self.folders:
            folder_path = Path(folder)
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
            
            self.observer.schedule(self.handler, str(folder_path), recursive=False)
            print(f"监控文件夹: {folder}")
        
        self.observer.start()
    
    def stop(self):
        """停止监控"""
        self.observer.stop()
        self.observer.join()
    
    def _should_monitor(self, file_path: str) -> bool:
        """检查文件类型是否需要监控"""
        return any(file_path.lower().endswith(ext) for ext in self.supported_extensions)