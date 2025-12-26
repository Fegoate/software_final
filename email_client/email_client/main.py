"""
================================================================================
邮件客户端 - 主程序入口文件
================================================================================

这是整个邮件客户端程序的入口文件，程序从这里开始运行。

【文件作用】
- 初始化图形界面应用程序
- 设置程序的整体外观样式（字体、颜色、按钮样式等）
- 创建并显示主窗口

【功能概述】
- 邮件接收/发送（支持附件）
- 多收件人、抄送、密送
- 邮件转发
- 邮件管理（浏览、删除、排序、搜索）
- 通信簿管理（增删改查、导入导出）
- 邮件夹管理

【支持的邮箱】
- QQ邮箱、163/126邮箱、Gmail、Outlook
- 自定义邮箱服务器

【技术说明】
- 使用 PyQt5 框架构建图形界面
- PyQt5 是 Python 最流行的 GUI（图形用户界面）库之一
================================================================================
"""

# ============================================================================
# 导入必要的模块
# ============================================================================

# sys 模块：提供与 Python 解释器交互的功能
# 比如获取命令行参数、退出程序等
import sys

# os 模块：提供与操作系统交互的功能
# 比如获取文件路径、创建目录等
import os

# 将项目根目录添加到 Python 的模块搜索路径中
# 这样可以确保程序能找到我们自己写的模块
# __file__ 是当前文件的路径
# os.path.abspath() 获取绝对路径
# os.path.dirname() 获取目录名
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ============================================================================
# 导入 PyQt5 相关模块
# ============================================================================

# QApplication：Qt 应用程序的核心类，每个程序只能有一个
# 它管理程序的控制流和主要设置
from PyQt5.QtWidgets import QApplication

# Qt：包含各种 Qt 的常量和枚举值
# 比如对齐方式、窗口标志等
from PyQt5.QtCore import Qt

# QFont：用于设置字体的类
# 可以指定字体名称、大小、粗细等
# QIcon：用于设置图标的类
from PyQt5.QtGui import QFont, QIcon

# 导入我们自己写的主窗口类
from ui.main_window import MainWindow


# ============================================================================
# 主函数：程序的入口点
# ============================================================================
def main():
    """
    程序入口函数

    这个函数做了以下事情：
    1. 设置高 DPI（高分辨率屏幕）支持
    2. 创建 Qt 应用程序实例
    3. 设置程序的字体和样式
    4. 创建并显示主窗口
    5. 进入事件循环，等待用户操作
    """

    # ------------------------------------------------------------------------
    # 第一步：启用高 DPI 支持
    # ------------------------------------------------------------------------
    # 现在很多显示器都是高分辨率的（比如 4K 屏幕）
    # 这两行代码让程序在高分辨率屏幕上也能正常显示，不会变得很小

    # 启用高 DPI 缩放：让界面元素自动放大以适应高分辨率屏幕
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    # 启用高 DPI 图片：让图片也能高清显示
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # ------------------------------------------------------------------------
    # 第二步：创建应用程序实例
    # ------------------------------------------------------------------------
    # sys.argv 是命令行参数列表，Qt 需要它来处理一些系统级的参数
    app = QApplication(sys.argv)

    # 设置应用程序的名称，会显示在任务栏等地方
    app.setApplicationName("邮件客户端")

    # ------------------------------------------------------------------------
    # 【UI优化】设置应用程序图标（窗口标题栏和任务栏图标）
    # ------------------------------------------------------------------------
    # 获取图标文件路径（支持打包后的路径）
    if getattr(sys, 'frozen', False):
        # 打包后的路径：PyInstaller 将资源文件解压到 _MEIPASS 临时目录
        base_path = sys._MEIPASS
    else:
        # 开发环境：脚本所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.join(base_path, "app_icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # ------------------------------------------------------------------------
    # 第三步：设置默认字体
    # ------------------------------------------------------------------------
    # 【UI优化】使用设计系统指定的字体族，正文字号13px
    # 字体族优先级：system-ui > PingFang SC > Microsoft YaHei > sans-serif
    font = QFont("Microsoft YaHei", 10)  # 调整为10号字体（约13px）
    app.setFont(font)

    # ------------------------------------------------------------------------
    # 第四步：设置应用样式
    # ------------------------------------------------------------------------
    # "Fusion" 是 Qt 自带的一种现代化界面风格
    # 它在所有操作系统上看起来都一样，比较美观
    app.setStyle("Fusion")

    # ------------------------------------------------------------------------
    # 第五步：设置详细的样式表（CSS 样式）
    # ------------------------------------------------------------------------
    # 【UI优化】基于 Enterprise-Campus Dashboard 设计系统重构样式表
    # 设计系统配色：主色#1677FF，背景#F5F7FA，边框#E5E6EB
    app.setStyleSheet("""
        /* ================================================================
           【UI优化】主窗口样式 - 使用设计系统背景色
           ================================================================ */
        QMainWindow {
            background-color: #F5F7FA;  /* 设计系统主背景色 */
        }

        /* ================================================================
           【UI优化】菜单栏样式 - 简洁的企业级风格
           ================================================================ */
        QMenuBar {
            background-color: #FFFFFF;           /* 面板背景色 */
            border-bottom: 1px solid #E5E6EB;   /* 设计系统边框色 */
            padding: 4px 8px;                    /* 调整内边距 */
            font-size: 13px;                     /* 正文字号 */
        }
        QMenuBar::item {
            padding: 6px 12px;                   /* 菜单项内边距 */
            border-radius: 4px;                  /* 小圆角 */
            color: #1F2329;                      /* 主文字色 */
        }
        QMenuBar::item:selected {
            background-color: rgba(22, 119, 255, 0.1);  /* 主色10%透明度 */
            color: #1677FF;                      /* 主色 */
        }
        /* 下拉菜单样式 */
        QMenu {
            background-color: #FFFFFF;
            border: 1px solid #E5E6EB;
            border-radius: 6px;                  /* 按钮圆角 */
            padding: 4px;
        }
        QMenu::item {
            padding: 8px 16px;
            border-radius: 4px;
            color: #1F2329;
        }
        QMenu::item:selected {
            background-color: rgba(22, 119, 255, 0.1);
            color: #1677FF;
        }

        /* ================================================================
           【UI优化】工具栏样式 - 清爽的操作区域
           ================================================================ */
        QToolBar {
            background-color: #FFFFFF;
            border: none;
            border-bottom: 1px solid #E5E6EB;
            padding: 8px 12px;                   /* 基于8px基础单位 */
            spacing: 8px;
        }
        QToolBar QToolButton {
            background-color: transparent;       /* 透明背景 */
            border: 1px solid #E5E6EB;
            border-radius: 6px;                  /* 按钮圆角 */
            padding: 8px 16px;
            margin: 2px;
            font-weight: 500;
            color: #1F2329;
        }
        QToolBar QToolButton:hover {
            background-color: rgba(22, 119, 255, 0.08);
            border-color: #1677FF;
            color: #1677FF;
        }
        QToolBar QToolButton:pressed {
            background-color: rgba(22, 119, 255, 0.15);
        }
        QToolBar QToolButton::menu-indicator {
            image: none;
            subcontrol-position: right center;
            subcontrol-origin: padding;
            width: 12px;
            padding-right: 4px;
        }

        /* ================================================================
           【UI优化】分组框样式 - 卡片式设计
           ================================================================ */
        QGroupBox {
            font-weight: 500;                    /* 中等粗细 */
            font-size: 14px;                     /* 小节标题字号 */
            border: 1px solid #E5E6EB;
            border-radius: 8px;                  /* 卡片圆角 */
            margin-top: 16px;
            padding: 16px 12px 12px 12px;
            background-color: #FFFFFF;
            /* 【UI优化】卡片阴影 */
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
            color: #1F2329;                      /* 主文字色 */
            background-color: #FFFFFF;
        }

        /* ================================================================
           【UI优化】列表控件样式 - 紧凑型列表
           ================================================================ */
        QListWidget {
            border: 1px solid #E5E6EB;
            border-radius: 8px;                  /* 卡片圆角 */
            background-color: #FFFFFF;
            outline: none;
            padding: 4px;
        }
        QListWidget::item {
            padding: 12px;                       /* 列表项内边距 */
            border-bottom: 1px solid #F0F0F0;   /* 分隔线色 */
            border-radius: 4px;
            margin: 2px 0;
        }
        QListWidget::item:selected {
            background-color: rgba(22, 119, 255, 0.1);
            color: #1677FF;
            border: none;
        }
        QListWidget::item:hover:!selected {
            background-color: #F5F7FA;
        }

        /* ================================================================
           【UI优化】多行文本框样式
           ================================================================ */
        QTextEdit {
            border: 1px solid #E5E6EB;
            border-radius: 6px;                  /* 输入框圆角 */
            background-color: #FFFFFF;
            padding: 12px;
            font-size: 13px;
            color: #1F2329;
        }
        QTextEdit:focus {
            border-color: #1677FF;               /* 主色聚焦边框 */
        }

        /* ================================================================
           【UI优化】单行输入框样式
           ================================================================ */
        QLineEdit {
            border: 1px solid #E5E6EB;
            border-radius: 6px;                  /* 输入框圆角 */
            padding: 8px 12px;
            background-color: #FFFFFF;
            font-size: 13px;
            color: #1F2329;
        }
        QLineEdit:focus {
            border-color: #1677FF;
        }
        QLineEdit:disabled {
            background-color: #F5F7FA;
            color: #C9CDD4;                      /* 禁用文字色 */
        }

        /* ================================================================
           【UI优化】下拉框样式
           ================================================================ */
        QComboBox {
            border: 1px solid #E5E6EB;
            border-radius: 6px;
            padding: 8px 12px;
            background-color: #FFFFFF;
            font-size: 13px;
            color: #1F2329;
            min-height: 20px;
        }
        QComboBox:focus, QComboBox:on {
            border-color: #1677FF;
        }
        QComboBox::drop-down {
            border: none;
            width: 24px;
            padding-right: 8px;
        }
        QComboBox QAbstractItemView {
            border: 1px solid #E5E6EB;
            border-radius: 6px;
            background-color: #FFFFFF;
            selection-background-color: rgba(22, 119, 255, 0.1);
            selection-color: #1677FF;
            padding: 4px;
        }

        /* ================================================================
           【UI优化】按钮样式 - 主色调按钮
           ================================================================ */
        QPushButton {
            background-color: #1677FF;           /* 设计系统主色 */
            color: white;
            border: none;
            border-radius: 6px;                  /* 按钮圆角 */
            padding: 8px 16px;
            font-weight: 500;
            font-size: 13px;
            min-height: 16px;
        }
        QPushButton:hover {
            background-color: #4096FF;           /* 悬停时变亮 */
        }
        QPushButton:pressed {
            background-color: #0958D9;           /* 按下时变深 */
        }
        QPushButton:disabled {
            background-color: #C9CDD4;           /* 禁用色 */
            color: #FFFFFF;
        }
        QPushButton::menu-indicator {
            subcontrol-position: right center;
            subcontrol-origin: padding;
            right: 8px;
            width: 10px;
        }

        /* ================================================================
           【UI优化】表格样式 - 紧凑的数据表格
           ================================================================ */
        QTableWidget {
            border: 1px solid #E5E6EB;
            border-radius: 8px;
            background-color: #FFFFFF;
            gridline-color: #F0F0F0;
            font-size: 13px;
        }
        QTableWidget::item {
            padding: 10px 8px;
            border-bottom: 1px solid #F0F0F0;
            color: #1F2329;
        }
        QTableWidget::item:selected {
            background-color: rgba(22, 119, 255, 0.1);
            color: #1677FF;
        }
        QHeaderView::section {
            background-color: #F5F7FA;
            padding: 10px 8px;
            border: none;
            border-bottom: 1px solid #E5E6EB;
            font-weight: 500;
            font-size: 13px;
            color: #4E5969;                      /* 次级文字色 */
        }

        /* ================================================================
           【UI优化】状态栏样式
           ================================================================ */
        QStatusBar {
            background-color: #FFFFFF;
            border-top: 1px solid #E5E6EB;
            font-size: 12px;                     /* 说明文字字号 */
            color: #86909C;                      /* 三级文字色 */
            padding: 4px 12px;
        }

        /* ================================================================
           【UI优化】对话框样式
           ================================================================ */
        QDialog {
            background-color: #F5F7FA;
        }

        /* ================================================================
           【UI优化】标签样式
           ================================================================ */
        QLabel {
            color: #1F2329;
            font-size: 13px;
        }

        /* ================================================================
           【UI优化】复选框样式
           ================================================================ */
        QCheckBox {
            spacing: 8px;
            font-size: 13px;
            color: #1F2329;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #E5E6EB;
            border-radius: 4px;
            background-color: #FFFFFF;
        }
        QCheckBox::indicator:hover {
            border-color: #1677FF;
        }
        QCheckBox::indicator:checked {
            background-color: #1677FF;
            border-color: #1677FF;
        }

        /* ================================================================
           【UI优化】数字输入框样式
           ================================================================ */
        QSpinBox {
            border: 1px solid #E5E6EB;
            border-radius: 6px;
            padding: 8px 12px;
            background-color: #FFFFFF;
            font-size: 13px;
            color: #1F2329;
        }
        QSpinBox:focus {
            border-color: #1677FF;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            border: none;
            width: 20px;
        }

        /* ================================================================
           【UI优化】分割器样式 - 更细的分隔条
           ================================================================ */
        QSplitter::handle {
            background-color: #E5E6EB;
        }
        QSplitter::handle:horizontal {
            width: 1px;
        }
        QSplitter::handle:vertical {
            height: 1px;
        }
        QSplitter::handle:hover {
            background-color: #1677FF;
        }

        /* ================================================================
           【UI优化】进度对话框样式
           ================================================================ */
        QProgressDialog {
            background-color: #FFFFFF;
        }
        QProgressBar {
            border: none;
            border-radius: 4px;
            background-color: #F0F0F0;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #1677FF;
            border-radius: 4px;
        }

        /* ================================================================
           【UI优化】滚动条样式 - 简约风格
           ================================================================ */
        QScrollBar:vertical {
            background-color: transparent;
            width: 8px;
            margin: 0;
        }
        QScrollBar::handle:vertical {
            background-color: #C9CDD4;
            border-radius: 4px;
            min-height: 40px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #86909C;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0;
        }
        QScrollBar:horizontal {
            background-color: transparent;
            height: 8px;
            margin: 0;
        }
        QScrollBar::handle:horizontal {
            background-color: #C9CDD4;
            border-radius: 4px;
            min-width: 40px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: #86909C;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0;
        }

        /* ================================================================
           【UI优化】消息框样式
           ================================================================ */
        QMessageBox {
            background-color: #FFFFFF;
        }
        QMessageBox QLabel {
            font-size: 13px;
            color: #1F2329;
        }
    """)

    # ------------------------------------------------------------------------
    # 第六步：创建并显示主窗口
    # ------------------------------------------------------------------------
    # 创建主窗口实例
    window = MainWindow()

    # 显示窗口
    # show() 方法会让窗口出现在屏幕上
    window.show()

    # ------------------------------------------------------------------------
    # 第七步：进入事件循环
    # ------------------------------------------------------------------------
    # app.exec_() 启动 Qt 的事件循环
    # 事件循环会持续运行，等待并处理用户的操作（点击、输入等）
    # 当用户关闭窗口时，exec_() 返回，程序结束
    # sys.exit() 确保程序正确退出，返回退出代码
    sys.exit(app.exec_())


# ============================================================================
# 程序入口点
# ============================================================================
# 这是 Python 的标准写法
# 当直接运行这个文件时，__name__ 的值是 "__main__"
# 当这个文件被其他文件导入时，__name__ 的值是模块名
# 这样可以确保只有直接运行时才执行 main() 函数
if __name__ == "__main__":
    main()
