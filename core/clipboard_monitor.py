
# core/clipboard_monitor.py
import pyperclip
import time
import re
from typing import Optional, Callable

class ClipboardMonitor:
    """监控剪贴板中的哈希值"""
    
    def __init__(self):
        self.last_content = ""
        self.running = False
        self.callback = None
        # 匹配常见的哈希值格式（十六进制字符串）
        self.hash_pattern = re.compile(r'^[a-fA-F0-9]{32,}$')  # 32位以上十六进制
    
    def start(self, callback):
        """开始监控剪贴板"""
        self.app= callback
        self.running = True
        self.last_content = pyperclip.paste()
        self._monitor()
    
    def stop(self):
        """停止监控"""
        self.running = False
    
    def _monitor(self):
        """监控循环（在独立线程中运行）"""
        while self.running:
            try:

                current = pyperclip.paste()
                if current != self.last_content:
                    self.last_content = current
                    # 检查是否可能是哈希值
                    if self._is_hash(current):
                        self.app(current)
                time.sleep(0.5)  # 每500ms检查一次1ee648ad4961ef19484e063c96784634841990ef45ece1e03dff4fe9d6747d4d
            except Exception as e:
                print(f"剪贴板监控出错: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(1)
    
    def _is_hash(self, text: str) -> bool:
        """判断文本是否可能是哈希值"""
        if not text or not isinstance(text, str):
            return False
        text = text.strip()
        # 常见的哈希长度：MD5=32, SHA1=40, SHA256=64, SHA512=128
        return len(text) in [64] and self.hash_pattern.match(text) is not None