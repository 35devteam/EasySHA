# main.py
import threading
import sys
from pathlib import Path
from config import Config
from core.hash_calculator import HashCalculator
from core.file_monitor import FileMonitor
from core.clipboard_monitor import ClipboardMonitor
from core.notifier import NotificationService
from core.tray import SystemTray
from handlers.button_handler import ButtonHandler
import time
import os
import signal

class EasyShaApp:
    """主应用类，作为依赖注入容器"""
    
    def __init__(self):
        # 加载配置
        self.config = Config()
        
        # 设置开关
        self.notifications_enabled = True
        self.sound_enabled = True
        
        # 初始化各个模块
        self.hash_calculator = HashCalculator()
        self.notifier = NotificationService(
            app_name="EasySha", 
            app_icon=self.config.app_icon
        )
        self.file_monitor = FileMonitor(
            self.config.download_folders,
            self.config.supported_extensions
        )
        self.clipboard_monitor = ClipboardMonitor()
        
        # 应用状态
        self.current_file = None
        self.pending_verification = None
        
        # 初始化按钮处理器
        self.button_handler = ButtonHandler(self)
        
        # 设置通知回调
        self.notifier.set_callback_handler(self.button_handler.handle_callback)
        self.notifier.set_sound_enabled(self.sound_enabled)
        
        # 初始化系统托盘
        self.tray = SystemTray(self)
        
        # 处理退出信号
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """处理退出信号"""
        print("\n🛑 接收到退出信号")
        self.shutdown()
    
    def on_file_detected(self, file_path: str):
        """当监控到新文件时的回调（从 watchdog 线程调用）"""
        self._handle_file_detected(file_path)
    
    def _handle_file_detected(self, file_path: str):
        """同步处理新文件"""
        print(f"检测到新文件: {file_path}")
        
        # 计算哈希值
        hashes = self.hash_calculator.calculate(file_path)
        if not hashes:
            return
        
        # 获取文件大小
        file_size = Path(file_path).stat().st_size
        size_str = self._format_size(file_size)
        
        # 保存到应用状态
        self.current_file = {
            'path': file_path,
            'name': Path(file_path).name,
            'hashes': hashes,
            'size': size_str
        }
        
        # 更新托盘图标状态（正常）
        self.tray.update_icon_state("normal")
        
        # 如果通知启用，显示通知
        if self.notifications_enabled:
            self.notifier.show_file_detected(
                Path(file_path).name,
                size_str,
                hashes
            )
    
    def on_clipboard_hash(self, hash_value: str):
        """当剪贴板中出现哈希值时的回调（从剪贴板线程调用）"""
        self._handle_clipboard_hash(hash_value)
    
    def _handle_clipboard_hash(self, hash_value: str):
        """同步处理剪贴板哈希"""
        # 显示检测到哈希值
        if self.notifications_enabled:
            self.notifier.show_clipboard_detected(hash_value)
        
        # 如果有待验证的文件，立即进行比对
        if self.pending_verification:
            self._verify_with_pending(hash_value)
    
    def _verify_with_pending(self, clipboard_hash: str):
        """与待验证文件进行比对"""
        file_hash = self.pending_verification['hashes'].get('sha256', '')
        
        if file_hash.lower() == clipboard_hash.lower():
            # 验证成功
            self.tray.update_icon_state("success")
            if self.notifications_enabled:
                self.notifier.show_verification_success(
                    self.pending_verification['name']
                )
        else:
            # 验证失败
            self.tray.update_icon_state("error")
            if self.notifications_enabled:
                self.notifier.show_verification_failed(
                    self.pending_verification['name'],
                    clipboard_hash,
                    file_hash
                )
        
        # 清除待验证状态
        self.pending_verification = None
        
        # 3秒后恢复为正常状态
        def reset_icon():
            time.sleep(3)
            self.tray.update_icon_state("normal")
        
        threading.Thread(target=reset_icon, daemon=True).start()
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def run(self):
        """运行主逻辑"""
        print("🚀 EasySha 启动中...")
        
        # 启动系统托盘（在独立线程中运行，因为 pystray 不是异步的）
        tray_thread = threading.Thread(target=self.tray.run, daemon=True)
        tray_thread.start()
        
        # 显示就绪通知
        if self.notifications_enabled:
            self.notifier.show_ready()
        
        # 启动文件监控（在独立线程中）
        monitor_thread = threading.Thread(
            target=self.file_monitor.start,
            args=(self.on_file_detected,),
            daemon=True
        )
        monitor_thread.start()
        
        # 启动剪贴板监控（在独立线程中）
        clipboard_thread = threading.Thread(
            target=self.clipboard_monitor.start,
            args=(self.on_clipboard_hash,),
            daemon=True
        )
        clipboard_thread.start()
        
        print("✅ EasySha 运行中，托盘图标已显示")
        print(f"监控文件夹: {self.config.download_folders}")
        print("右键点击托盘图标可查看菜单")
        
        try:
            # 保持运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()
    
    def shutdown(self):
        """关闭应用"""
        print("\n🛑 正在关闭 EasySha...")
        self.file_monitor.stop()
        self.clipboard_monitor.stop()
        if self.tray.icon:
            self.tray.icon.stop()
        print("👋 再见！")

def main():
    """同步入口函数"""
    app = EasyShaApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n👋 用户退出")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 如果是 pythonw.exe 运行，重定向输出
    if not sys.stdout:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
    
    main()