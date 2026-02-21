# EasySha 🔐

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Windows 11](https://img.shields.io/badge/platform-Windows%2011%2B-success)](https://www.microsoft.com/windows)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

EasySha 是一个轻量级的 Windows 工具，自动监控下载文件并计算 SHA256 校验和，通过 Win11 通知气泡显示，支持剪贴板自动比对。



## ✨ 特性

- 🚀 **自动监控** - 监控下载文件夹，新文件自动计算哈希
- 📋 **剪贴板比对** - 复制哈希值自动比对，成功有音效反馈
- 🔔 **Win11 通知** - 原生 Toast 通知，带交互按钮
- 🖥️ **系统托盘** - 后台运行，右键菜单可配置
- 🎨 **状态反馈** - 托盘图标变色（蓝/黄/绿/红）


## 📦 安装

### 方法1：直接运行（Python）
```bash
# 克隆仓库
git clone https://github.com/35devteam/EasySha.git
cd EasySha

# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
