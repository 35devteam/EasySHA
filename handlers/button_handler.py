# handlers/button_handler.py
import subprocess
import pyperclip
from pathlib import Path
from typing import Dict, Any

class ButtonHandler:
    """处理来自 Toast 通知的按钮点击（同步版本）"""
    
    def __init__(self, app):
        self.app = app
    
    def handle_callback(self, args: Dict[str, Any]):
        """
        处理通知回调
        args 格式: {'arguments': 'easysha:copy', 'user_input': {}}
        """
        argument = args.get('arguments', '')
        user_input = args.get('user_input', {})
        
        print(f"收到按钮回调: {argument}")  # 调试用
        
        if argument.startswith('http:'):
            action = argument.replace('http:', '')
            
            # 根据 action 执行相应操作
            handlers = {
                'copy': self._copy_hash,
                'verify': self._start_verification,
                'ignore': self._ignore_file,
                'open_folder': self._open_folder,
                'copy_actual': self._copy_actual,
                'dismiss': self._dismiss
            }
            
            if action in handlers:
                handlers[action]()
            else:
                print(f"未知动作: {action}")
        else:
            #点击
            self.app.tray.update_icon_state("normal")
    
    def _copy_hash(self):
        """复制文件哈希到剪贴板"""
        if self.app.current_file and 'hashes' in self.app.current_file:
            sha256 = self.app.current_file['hashes'].get('sha256', '')
            if sha256:
                pyperclip.copy(sha256)
                self.app.notifier.show_info("✅ 已复制", "SHA256 已复制到剪贴板")
    
    def _start_verification(self):
        """开始验证（等待剪贴板哈希）"""
        self.app.notifier.show_info("🔍 等待验证", "请复制校验和到剪贴板...")
        # 标记当前文件为待验证状态
        self.app.pending_verification = self.app.current_file
        # 更新托盘图标状态
        self.app.tray.update_icon_state("verifying")
    
    def _ignore_file(self):
        """忽略当前文件"""
        self.app.current_file = None
        self.app.pending_verification = None
        self.app.notifier.show_info("🗑️ 已忽略", "文件已从监控列表移除")
        self.app.tray.update_icon_state("normal")
    
    def _open_folder(self):
        """打开文件所在文件夹"""
        if self.app.current_file and 'path' in self.app.current_file:
            folder = Path(self.app.current_file['path']).parent
            if folder.exists():
                subprocess.run(['explorer', str(folder)])
    
    def _copy_actual(self):
        """复制实际哈希值（验证失败时）"""
        if self.app.current_file and 'hashes' in self.app.current_file:
            sha256 = self.app.current_file['hashes'].get('sha256', '')
            if sha256:
                pyperclip.copy(sha256)
                self.app.notifier.show_info("📋 已复制", "实际哈希值已复制到剪贴板")
    
    def _dismiss(self):
        """关闭通知"""
        pass  # 什么都不做，只是关闭