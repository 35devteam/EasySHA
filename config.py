
# config.py
from dataclasses import dataclass
from pathlib import Path


class Config:
    """应用配置"""
    # 监控的下载文件夹
    download_folders: list = ["D:\\do"]
    
    # 支持的文件扩展名
    supported_extensions: list = None
    
    # 应用图标（可以是本地路径或网络图片）
    app_icon: str = "https://cdn-icons-png.flaticon.com/512/1006/1006772.png"
    
    # 验证成功时的音效
    success_sound: str = "ms-winsoundevent:Notification.Looping.Alarm"
    
    def __post_init__(self):
        if self.download_folders is None:
            # 默认监控用户的下载文件夹
            self.download_folders = [str(Path.home() / "Downloads")]
        
        if self.supported_extensions is None:
            # 常见需要校验的文件类型
            self.supported_extensions = [
                '.iso', '.exe', '.msi', '.zip', '.rar', '.7z',
                '.tar', '.gz', '.bz2', '.xz', '.dmg', '.img',
                '.apk', '.ova', '.vhd', '.bin'
            ]