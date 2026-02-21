# core/notifier.py
from win11toast import toast
from typing import Dict, Optional, Callable, Any

class NotificationService:
    """封装 win11toast 的同步通知服务"""
    
    def __init__(self, app_name: str = "EasySha", app_icon: str = None):
        self.app_name = app_name
        self.app_icon = app_icon
        self.current_file = None
        self.callback_handler = None  # 用于处理按钮回调
    
    def set_callback_handler(self, handler):
        """设置按钮回调处理器"""
        self.callback_handler = handler
    
    def show_file_detected(self, file_name: str, file_size: str, hashes: Dict[str, str]):
        """显示新文件检测到的通知"""
        self.current_file = {
            'name': file_name,
            'hashes': hashes
        }
        
        title = f"📁 新文件: {file_name}"
        content = f"大小: {file_size}\nSHA256: {hashes['sha256'][:16]}..."
        
        toast(
            title,
            content,
            icon=self.app_icon,
            buttons=[
                {
                    'activationType': 'protocol', 
                    'arguments': 'http:copy', 
                    'content': '📋 复制哈希'
                },
                {
                    'activationType': 'protocol', 
                    'arguments': 'http:verify', 
                    'content': '✅ 等待验证'
                },
                {
                    'activationType': 'protocol', 
                    'arguments': 'http:ignore', 
                    'content': '🗑️ 忽略'
                }
            ],
            on_click=self.callback_handler,  # 直接绑定回调
            duration='long'
        )
    
    def show_verification_success(self, file_name: str):
        """显示验证成功通知"""
        toast(
            "✅ 验证成功！",
            f"文件 {file_name} 的哈希值与剪贴板完全匹配",
            icon=self.app_icon,
            buttons=[
                {
                    'activationType': 'protocol',
                    'arguments': 'http:open_folder',
                    'content': '📂 打开文件夹'
                },
                {
                    'activationType': 'protocol',
                    'arguments': 'http:dismiss',
                    'content': '关闭'
                }
            ],
            on_click=self.callback_handler,
            audio='ms-winsoundevent:Notification.Looping.Alarm',
            duration='long'
        )
    
    def show_verification_failed(self, file_name: str, expected: str, actual: str):
        """显示验证失败通知"""
        toast(
            "❌ 验证失败",
            f"文件: {file_name}\n期望: {expected[:16]}...\n实际: {actual[:16]}...",
            icon=self.app_icon,
            buttons=[
                {
                    'activationType': 'protocol',
                    'arguments': 'http:copy_actual',
                    'content': '📋 复制实际值'
                },
                {
                    'activationType': 'protocol',
                    'arguments': 'http:ignore',
                    'content': '忽略'
                }
            ],
            on_click=self.callback_handler,
            duration='long'
        )
    
    def show_clipboard_detected(self, hash_value: str):
        """显示检测到剪贴板中的哈希值"""
    
    def show_ready(self):
        """显示应用就绪通知"""
        toast(
            "🚀 EasySha 已就绪",
            "正在监控下载文件夹，等待文件...",
            icon=self.app_icon,
            on_click=self.callback_handler,
            duration='short'
        )
    
    def show_info(self, title: str, message: str):
        """显示普通信息通知"""
        toast(
            title,
            message,
            icon=self.app_icon,
            on_click=self.callback_handler,
            duration='short'
        )
    
    def set_sound_enabled(self, enabled: bool):
        """设置是否启用音效"""
        self._sound_enabled = enabled