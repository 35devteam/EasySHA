
# core/tray.py
import pystray
from PIL import Image, ImageDraw
import threading
import os
import sys
from pathlib import Path
import webbrowser

class SystemTray:
    """系统托盘图标管理"""
    
    def __init__(self, app):
        self.app = app
        self.icon = None
        self.icon_image = self._create_default_icon()
        
    def _create_default_icon(self):
        """创建一个默认的托盘图标（绿色盾牌）"""
        # 创建一个 64x64 的图像
        image = Image.new('RGB', (64, 64), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 画一个简单的盾牌图标
        # 外框
        draw.rectangle([8, 8, 56, 56], outline=(0, 120, 212), width=3)
        # 内填充
        draw.rectangle([12, 12, 52, 52], fill=(0, 120, 212, 30))
        # 打勾符号
        draw.line([20, 32, 28, 40, 44, 24], fill=(0, 200, 0), width=4)
        
        return image
    
    def _create_menu(self):
        """创建托盘右键菜单"""
        return pystray.Menu(
            pystray.MenuItem(
                "📁 监控的文件夹",
                self._show_monitored_folders,
                enabled=False  # 只作为标题，不可点击
            ),
            pystray.MenuItem(
                f"   {self.app.config.download_folders[0]}",
                self._open_download_folder
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "📊 状态",
                self._show_status,
                enabled=False
            ),
            pystray.MenuItem(
                f"   🟢 运行中",
                None,
                enabled=False
            ),
            pystray.MenuItem(
                f"   📄 最后文件: {self._get_last_file_status()}",
                None,
                enabled=False
            ),
            pystray.MenuItem(
                f"   🔍 待验证: {'有' if self.app.pending_verification else '无'}",
                None,
                enabled=False
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "⚙️ 设置",
                pystray.Menu(
                    pystray.MenuItem(
                        "🔔 启用通知",
                        self._toggle_notifications,
                        checked=lambda item: self.app.notifications_enabled
                    ),
                    pystray.MenuItem(
                        "🔊 启用音效",
                        self._toggle_sound,
                        checked=lambda item: self.app.sound_enabled
                    ),
                    pystray.MenuItem(
                        "📋 开机启动",
                        self._toggle_autostart,
                        checked=lambda item: self._check_autostart()
                    )
                )
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "🌐 关于",
                self._show_about
            ),
            pystray.MenuItem(
                "🚪 退出",
                self._quit_app
            )
        )
    
    def _get_last_file_status(self):
        """获取最后文件的状态"""
        if self.app.current_file:
            name = Path(self.app.current_file['name']).name
            if len(name) > 20:
                name = name[:17] + "..."
            return name
        return "无"
    
    def _show_monitored_folders(self):
        """显示监控的文件夹（菜单项，不可点击）"""
        pass
    
    def _open_download_folder(self):
        """打开下载文件夹"""
        folder = self.app.config.download_folders[0]
        if os.path.exists(folder):
            os.startfile(folder)
    
    def _show_status(self):
        """显示状态（菜单项，不可点击）"""
        pass
    
    def _toggle_notifications(self, icon, item):
        """切换通知开关"""
        self.app.notifications_enabled = not self.app.notifications_enabled
        if self.app.notifications_enabled:
            self._show_notification("🔔 通知已启用", "EasySha 将显示通知")
        else:
            self._show_notification("🔕 通知已禁用", "EasySha 将不会显示通知")
    
    def _toggle_sound(self, icon, item):
        """切换音效开关"""
        self.app.sound_enabled = not self.app.sound_enabled
        status = "已启用" if self.app.sound_enabled else "已禁用"
        self._show_notification("🔊 音效", f"验证成功音效 {status}")
    
    def _toggle_autostart(self, icon, item):
        """切换开机启动"""
        if self._check_autostart():
            self._remove_from_autostart()
            self._show_notification("⚙️ 开机启动", "已从开机启动中移除")
        else:
            self._add_to_autostart()
            self._show_notification("⚙️ 开机启动", "已添加到开机启动")
    
    def _check_autostart(self) -> bool:
        """检查是否已设置开机启动"""
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, "EasySha")
                return True
        except FileNotFoundError:
            return False
    
    def _add_to_autostart(self):
        """添加到开机启动"""
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                # 获取当前脚本的路径
                script_path = sys.argv[0]
                if script_path.endswith('.py'):
                    # 如果是 Python 脚本，使用 pythonw.exe 后台运行
                    pythonw = sys.executable.replace('python.exe', 'pythonw.exe')
                    command = f'"{pythonw}" "{script_path}"'
                else:
                    # 如果是 exe，直接运行
                    command = f'"{script_path}"'
                
                winreg.SetValueEx(key, "EasySha", 0, winreg.REG_SZ, command)
        except Exception as e:
            self._show_notification("❌ 错误", f"无法设置开机启动: {e}")
    
    def _remove_from_autostart(self):
        """从开机启动中移除"""
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, "EasySha")
        except FileNotFoundError:
            pass
    
    def _show_about(self):
        """显示关于信息"""
        from win11toast import toast
        toast(
            "📋 EasySha v1.0",
            "自动文件校验工具\n\n"
            "• 自动监控下载文件夹\n"
            "• 自动计算 SHA256\n"
            "• 剪贴板自动比对\n"
            "• Win11 原生通知\n\n"
            "Made with ❤️ by You",
            buttons=[
                {
                    'activationType': 'protocol',
                    'arguments': 'https://github.com/',
                    'content': '🌐 GitHub'
                },
                {
                    'activationType': 'protocol',
                    'arguments': 'https://github.com/issues',
                    'content': '🐛 反馈'
                }
            ],
            duration='long'
        )
    
    def _show_notification(self, title, message):
        """显示简短通知"""
        if self.app.notifications_enabled:
            from win11toast import toast
            toast(title, message, duration='short')
    
    def _quit_app(self):
        """退出应用"""
        if self.icon:
            self.icon.stop()
        self.app.shutdown()
    
    def update_icon_state(self, status: str = "normal"):
        """更新图标状态（可根据状态改变图标颜色）"""
        if status == "verifying":
            # 待验证状态 - 黄色
            image = Image.new('RGB', (64, 64), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)
            draw.rectangle([8, 8, 56, 56], outline=(255, 140, 0), width=3)
            draw.rectangle([12, 12, 52, 52], fill=(255, 140, 0, 30))
            draw.line([20, 32, 28, 40, 44, 24], fill=(255, 140, 0), width=4)
        elif status == "success":
            # 验证成功 - 绿色
            image = Image.new('RGB', (64, 64), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)
            draw.rectangle([8, 8, 56, 56], outline=(0, 200, 0), width=3)
            draw.rectangle([12, 12, 52, 52], fill=(0, 200, 0, 30))
            draw.line([20, 32, 28, 40, 44, 24], fill=(0, 200, 0), width=4)
        elif status == "error":
            # 验证失败 - 红色
            image = Image.new('RGB', (64, 64), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)
            draw.rectangle([8, 8, 56, 56], outline=(200, 0, 0), width=3)
            draw.rectangle([12, 12, 52, 52], fill=(200, 0, 0, 30))
            draw.line([20, 32, 44, 44], fill=(200, 0, 0), width=4)
            draw.line([44, 32, 20, 44], fill=(200, 0, 0), width=4)
        else:
            # 正常状态 - 蓝色
            image = self._create_default_icon()
        
        if self.icon:
            self.icon.icon = image
    
    def run(self):
        """在独立线程中运行托盘图标"""
        def setup(icon):
            self.icon = icon
            icon.visible = True
        
        # 创建托盘图标
        self.icon = pystray.Icon(
            "EasySha",
            self.icon_image,
            "EasySha - 自动文件校验",
            self._create_menu()
        )
        
        # 在独立线程中运行
        threading.Thread(target=self.icon.run, daemon=True).start()