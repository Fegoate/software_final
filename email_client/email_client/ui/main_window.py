"""
邮件客户端主窗口模块

【功能概述】
这是邮件客户端的核心界面文件，实现了以下主要功能：
1. 邮件列表展示：显示收件箱、已发送等各个文件夹的邮件
2. 邮件内容查看：显示邮件的详细内容、附件等信息
3. 邮件操作：写邮件、转发、删除、搜索等功能
4. 文件夹管理：切换不同邮件文件夹，管理自定义文件夹
5. 通讯录管理：管理联系人信息
6. 账户管理：登录、切换邮箱账户

【界面布局】
- 顶部：工具栏（写邮件、刷新、删除等快捷按钮）
- 左侧：文件夹选择、搜索框、邮件列表
- 右侧：邮件详情（主题、发件人、时间、正文、附件）
- 底部：状态栏（显示操作结果和邮件计数）
"""

# os模块：用于文件路径操作，如获取附件保存路径
import os

# PyQt5.QtWidgets：【Qt图形界面组件库】，提供各种UI控件
from PyQt5.QtWidgets import (
    QMainWindow,        # 【主窗口类】：应用程序的主窗口，包含菜单栏、工具栏、状态栏等
    QWidget,            # 【基础组件类】：所有UI组件的基类
    QVBoxLayout,        # 【垂直布局】：将组件垂直排列
    QHBoxLayout,        # 【水平布局】：将组件水平排列
    QSplitter,          # 【分割器】：可调整大小的分隔条，用于分割左右面板
    QListWidget,        # 【列表控件】：用于显示邮件列表
    QListWidgetItem,    # 【列表项】：列表中的单个条目
    QTextEdit,          # 【文本编辑框】：用于显示邮件正文内容
    QToolBar,           # 【工具栏】：显示快捷操作按钮
    QAction,            # 【动作】：菜单或工具栏的可执行操作
    QLineEdit,          # 【单行输入框】：用于搜索关键词输入
    QLabel,             # 【标签】：用于显示文本信息
    QStatusBar,         # 【状态栏】：显示程序运行状态
    QMessageBox,        # 【消息框】：显示提示、警告、错误信息
    QProgressDialog,    # 【进度对话框】：显示耗时操作的进度
    QApplication,       # 【应用程序类】：Qt应用程序的核心类
    QComboBox,          # 【下拉框】：用于文件夹选择、排序方式选择
    QTreeWidget,        # 【树形控件】：用于层级数据显示（本文件未实际使用）
    QTreeWidgetItem,    # 【树形项】：树形控件的节点（本文件未实际使用）
    QMenu,              # 【菜单】：右键菜单
    QFileDialog,        # 【文件对话框】：保存附件时选择路径
    QGroupBox,          # 【分组框】：将相关控件分组显示
    QPushButton,        # 【按钮】：用于触发操作
    QFrame              # 【框架】：用于创建带边框的区域
)

# PyQt5.QtCore：【Qt核心功能模块】
from PyQt5.QtCore import (
    Qt,                 # 【Qt常量】：提供各种枚举常量，如对齐方式、窗口标志等
    QThread,            # 【线程类】：用于多线程操作（本文件未实际使用）
    pyqtSignal          # 【信号】：Qt的信号机制，用于组件间通信（本文件未实际使用）
)

# PyQt5.QtGui：【Qt图形界面功能】
from PyQt5.QtGui import (
    QFont,              # 【字体类】：设置文本字体、大小、粗细
    QIcon               # 【图标类】：设置窗口或按钮图标（本文件未实际使用）
)

# sys模块：用于操作Python解释器
import sys
# 将当前文件的上级目录添加到模块搜索路径，使程序能找到core、models等自定义模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入自定义模块
from models.email_model import Email, EmailAccount              # 邮件和账户的【数据模型】
from core.email_receiver import EmailReceiver                   # 【邮件接收器】：从服务器获取邮件
from core.email_sender import EmailSender                       # 【邮件发送器】：向服务器发送邮件
from core.email_manager import EmailManager                     # 【邮件管理器】：管理本地邮件数据
from core.contact_manager import ContactManager                 # 【联系人管理器】：管理通讯录
from ui.login_dialog import LoginDialog                         # 【登录对话框】：账户登录界面
from ui.compose_dialog import ComposeDialog                     # 【写邮件对话框】：撰写新邮件界面
from ui.contact_dialog import ContactManagerDialog              # 【通讯录对话框】：管理联系人界面
from ui.folder_dialog import FolderManagerDialog                # 【文件夹管理对话框】：管理邮件文件夹界面


class MainWindow(QMainWindow):
    """
    邮件客户端主窗口类

    【类的作用】
    这是整个邮件客户端的核心类，继承自QMainWindow（Qt的主窗口类）。
    它负责：
    1. 创建和管理整个应用程序的界面
    2. 处理用户的各种操作（点击、搜索、删除等）
    3. 与邮件服务器通信（收发邮件）
    4. 管理本地数据（邮件列表、联系人等）

    【使用方法】
    在main.py中创建实例并显示：
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())

    【类属性】
    FOLDER_NAME_MAP: 邮件文件夹的英文名到中文名的映射字典
    """

    # 【类常量】文件夹名称中英文映射
    # 用途：将服务器返回的英文文件夹名转换为用户友好的中文名
    # 例如：将"INBOX"显示为"收件箱"
    FOLDER_NAME_MAP = {
        "INBOX": "收件箱",                  # 收件箱（邮件服务器标准名称）
        "Sent Messages": "已发送",          # 已发送邮件
        "Deleted Messages": "已删除",       # 已删除邮件
        "Drafts": "草稿箱",                 # 草稿箱
        "Junk": "垃圾邮件",                 # 垃圾邮件
        "Spam": "垃圾邮件",                 # 垃圾邮件（另一种叫法）
        "Trash": "已删除",                  # 已删除（另一种叫法）
        "Sent": "已发送",                   # 已发送（另一种叫法）
    }

    def __init__(self):
        """
        【构造方法】初始化主窗口

        功能：
        1. 初始化各种管理器（邮件管理器、联系人管理器等）
        2. 设置初始状态变量
        3. 创建用户界面
        4. 显示登录对话框

        参数：无
        返回值：无
        """
        # 调用父类（QMainWindow）的构造方法，这是继承中的标准做法
        super().__init__()

        # 【实例变量】初始化各种属性
        self.account: EmailAccount = None           # 当前登录的邮箱账户（包含邮箱地址、密码、服务器地址等）
        self.receiver: EmailReceiver = None         # 【邮件接收器】：负责从服务器接收邮件
        self.sender: EmailSender = None             # 【邮件发送器】：负责向服务器发送邮件
        self.manager = EmailManager()               # 【邮件管理器】：管理本地的邮件数据（增删改查）
        self.contact_manager = ContactManager()     # 【联系人管理器】：管理通讯录
        self.current_email: Email = None            # 当前选中的邮件（用户点击列表中的邮件后保存在这里）
        self.current_folder = "INBOX"               # 当前查看的文件夹（默认是收件箱）
        self.sort_key = "date"                      # 排序字段（可选：date日期、sender发件人、subject主题）
        self.sort_reverse = True                    # 排序顺序（True=降序，False=升序）
        self.folder_display_map = {}                # 【文件夹映射字典】：显示名称 -> 真实名称（如："收件箱" -> "INBOX"）

        # 初始化用户界面（创建所有按钮、列表、输入框等组件）
        self.init_ui()

        # 显示登录对话框（让用户输入邮箱账号和密码）
        self.show_login()

    def init_ui(self):
        """
        【初始化用户界面】创建整个窗口的所有组件

        功能：
        1. 设置窗口基本属性（标题、大小）
        2. 创建菜单栏和工具栏
        3. 创建左侧面板（文件夹选择、搜索、邮件列表）
        4. 创建右侧面板（邮件详情显示）
        5. 创建状态栏

        参数：无
        返回值：无

        【界面结构】
        MainWindow
        ├── 菜单栏 (MenuBar)
        ├── 工具栏 (ToolBar)
        ├── 中心部件 (CentralWidget)
        │   ├── 左侧面板
        │   │   ├── 文件夹选择下拉框
        │   │   ├── 搜索功能区
        │   │   ├── 排序选项
        │   │   └── 邮件列表
        │   └── 右侧面板
        │       ├── 邮件头信息（主题、发件人、时间）
        │       ├── 附件区域
        │       └── 邮件正文
        └── 状态栏 (StatusBar)
        """
        # 设置窗口标题（显示在窗口顶部标题栏）
        self.setWindowTitle("邮件客户端")

        # 设置窗口最小尺寸为1000x650像素，防止窗口被缩得太小导致界面混乱
        self.setMinimumSize(1000, 650)

        # 【创建中心部件】QMainWindow必须有一个中心部件来承载其他组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 【主布局】使用垂直布局管理器，将组件从上到下排列
        layout = QVBoxLayout(central_widget)
        # 【UI优化】使用设计系统的间距（基于8px基础单位）
        layout.setContentsMargins(0, 0, 0, 0)  # 去除外边距，让内容贴边
        layout.setSpacing(0)  # 去除间距

        # 创建工具栏（包含写邮件、刷新、删除等按钮）
        self.create_toolbar()

        # 创建菜单栏（包含文件、邮件、工具等菜单）
        self.create_menubar()

        # 【主分割器】使用水平分割器将窗口分为左右两部分，用户可以拖动调整大小
        # Qt.Horizontal表示水平方向的分割（左右分割）
        main_splitter = QSplitter(Qt.Horizontal)

        # ========== 【左侧面板】创建文件夹选择、搜索、排序和邮件列表 ==========
        left_panel = QWidget()
        # 【UI优化】设置左侧面板背景色
        left_panel.setStyleSheet("background-color: #FFFFFF;")
        # 左侧面板使用垂直布局，从上到下依次排列各个组件
        left_layout = QVBoxLayout(left_panel)
        # 【UI优化】使用设计系统的间距
        left_layout.setContentsMargins(16, 16, 16, 16)  # 基于8px的间距
        left_layout.setSpacing(12)                       # 组件间距12px

        # --- 文件夹选择区域 ---
        folder_layout = QHBoxLayout()  # 水平布局：标签在左，下拉框在右
        folder_layout.addWidget(QLabel("邮件夹:"))
        # 【文件夹下拉框】用于切换收件箱、已发送、草稿箱等不同文件夹
        self.folder_combo = QComboBox()
        # 【信号连接】当下拉框的选项改变时，调用on_folder_changed方法
        # currentTextChanged是Qt的信号，会自动传递新选中的文本
        self.folder_combo.currentTextChanged.connect(self.on_folder_changed)
        folder_layout.addWidget(self.folder_combo)
        left_layout.addLayout(folder_layout)

        # --- 搜索功能区 ---
        # 使用QGroupBox创建一个带标题和边框的分组
        search_group = QGroupBox("搜索")
        search_layout = QVBoxLayout()

        # 搜索类型选择（全部、发件人、主题、内容）
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("搜索范围:"))
        self.search_type = QComboBox()
        # addItems一次性添加多个选项
        self.search_type.addItems(["全部", "发件人", "主题", "内容"])
        type_layout.addWidget(self.search_type)
        search_layout.addLayout(type_layout)

        # 搜索输入框和按钮
        input_layout = QHBoxLayout()
        # 【搜索输入框】用户输入关键词的地方
        self.search_edit = QLineEdit()
        # setPlaceholderText设置占位符文本（灰色提示文字）
        self.search_edit.setPlaceholderText("输入关键词...")
        # 【信号连接】按回车键时触发搜索
        self.search_edit.returnPressed.connect(self.on_search)
        input_layout.addWidget(self.search_edit)

        # 搜索按钮
        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self.on_search)  # 点击按钮时触发搜索
        input_layout.addWidget(self.search_btn)

        # 清除搜索按钮
        self.clear_search_btn = QPushButton("清除")
        self.clear_search_btn.clicked.connect(self.on_clear_search)  # 清除搜索关键词并显示所有邮件
        input_layout.addWidget(self.clear_search_btn)

        search_layout.addLayout(input_layout)
        search_group.setLayout(search_layout)
        left_layout.addWidget(search_group)

        # --- 排序选项区 ---
        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel("排序:"))
        # 【排序方式下拉框】可选按日期、发件人或主题排序
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["按日期", "按发件人", "按主题"])
        # 当排序方式改变时，调用on_sort_changed方法重新排序邮件列表
        self.sort_combo.currentTextChanged.connect(self.on_sort_changed)
        sort_layout.addWidget(self.sort_combo)

        # 【排序顺序按钮】切换升序/降序
        self.sort_order_btn = QPushButton("降序")
        self.sort_order_btn.clicked.connect(self.toggle_sort_order)
        sort_layout.addWidget(self.sort_order_btn)
        left_layout.addLayout(sort_layout)

        # --- 邮件列表 ---
        # 【邮件列表控件】显示所有邮件的列表（每个邮件显示发件人、主题、时间）
        self.email_list = QListWidget()
        # 【信号连接】单击邮件时，在右侧显示邮件详情
        self.email_list.itemClicked.connect(self.on_email_selected)
        # 【信号连接】双击邮件时，如果是草稿则打开编辑
        self.email_list.itemDoubleClicked.connect(self.on_email_double_clicked)
        # 设置【右键菜单策略】为自定义菜单
        self.email_list.setContextMenuPolicy(Qt.CustomContextMenu)
        # 【信号连接】右键点击时显示上下文菜单（转发、删除等选项）
        self.email_list.customContextMenuRequested.connect(self.show_email_context_menu)
        left_layout.addWidget(self.email_list)

        # 将左侧面板添加到主分割器
        main_splitter.addWidget(left_panel)

        # ========== 【右侧面板】创建邮件详情显示区域 ==========
        right_panel = QWidget()
        # 【UI优化】设置右侧面板背景色
        right_panel.setStyleSheet("background-color: #F5F7FA;")
        right_layout = QVBoxLayout(right_panel)
        # 【UI优化】使用设计系统的间距
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)

        # --- 邮件头信息区域 ---
        # 【QFrame】创建一个带边框和样式的框架，用于显示邮件头信息
        self.header_widget = QFrame()
        self.header_widget.setFrameShape(QFrame.StyledPanel)
        # 【UI优化】使用设计系统的卡片样式
        self.header_widget.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;           /* 面板背景色 */
                border: 1px solid #E5E6EB;          /* 设计系统边框色 */
                border-radius: 8px;                  /* 卡片圆角 */
            }
        """)
        header_layout = QVBoxLayout(self.header_widget)
        # 【UI优化】调整内边距
        header_layout.setContentsMargins(16, 16, 16, 16)
        header_layout.setSpacing(8)

        # 【主题标签】显示邮件主题，使用标题字号
        self.subject_label = QLabel()
        # 【UI优化】使用设计系统的标题字号16px
        self.subject_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.subject_label.setStyleSheet("color: #1F2329; font-size: 16px; font-weight: 600;")
        self.subject_label.setWordWrap(True)
        header_layout.addWidget(self.subject_label)

        # 【发件人标签】显示发件人姓名和邮箱地址
        self.sender_label = QLabel()
        # 【UI优化】使用次级文字色
        self.sender_label.setStyleSheet("color: #4E5969; font-size: 13px;")
        header_layout.addWidget(self.sender_label)

        # 【时间标签】显示邮件发送时间
        self.date_label = QLabel()
        # 【UI优化】使用三级文字色
        self.date_label.setStyleSheet("color: #86909C; font-size: 12px;")
        header_layout.addWidget(self.date_label)

        # 【收件人标签】显示收件人邮箱地址
        self.recipient_label = QLabel()
        # 【UI优化】使用三级文字色
        self.recipient_label.setStyleSheet("color: #86909C; font-size: 12px;")

        right_layout.addWidget(self.header_widget)

        # --- 附件区域 ---
        # 【附件框架】只有当邮件有附件时才显示（默认隐藏）
        self.attachments_widget = QFrame()
        self.attachments_widget.setFrameShape(QFrame.StyledPanel)
        # 【UI优化】使用设计系统的警告色（#FAAD14）作为附件提示
        self.attachments_widget.setStyleSheet("""
            QFrame {
                background-color: #FFFBE6;           /* 浅黄警告背景 */
                border: 1px solid #FAAD14;           /* 警告色边框 */
                border-radius: 6px;                  /* 按钮圆角 */
            }
        """)
        attachments_layout = QVBoxLayout(self.attachments_widget)
        # 【UI优化】调整内边距
        attachments_layout.setContentsMargins(12, 8, 12, 8)
        attachments_layout.setSpacing(8)

        # 【UI优化】附件标签样式
        self.attachments_label = QLabel("附件:")
        self.attachments_label.setStyleSheet("color: #D48806; font-size: 13px; font-weight: 500;")
        attachments_layout.addWidget(self.attachments_label)

        # 【附件列表】显示所有附件的文件名和大小
        self.attachments_list = QListWidget()
        # 【UI优化】调整附件列表样式
        self.attachments_list.setMaximumHeight(80)
        self.attachments_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
            }
            QListWidget::item {
                padding: 4px 8px;
                color: #1F2329;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: rgba(212, 136, 6, 0.1);
            }
        """)
        self.attachments_list.itemDoubleClicked.connect(self.on_save_attachment)
        attachments_layout.addWidget(self.attachments_list)

        # 默认隐藏附件区域，只有邮件有附件时才显示
        self.attachments_widget.hide()
        right_layout.addWidget(self.attachments_widget)

        # --- 邮件正文区域 ---
        # 【文本编辑框】用于显示邮件正文内容
        self.content_view = QTextEdit()
        self.content_view.setReadOnly(True)
        # 【UI优化】使用设计系统的正文字号和卡片样式
        self.content_view.setFont(QFont("Microsoft YaHei", 10))
        self.content_view.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #E5E6EB;
                border-radius: 8px;
                padding: 16px;
                font-size: 13px;
                color: #1F2329;
                line-height: 1.6;
            }
        """)
        right_layout.addWidget(self.content_view)

        # 将右侧面板添加到主分割器
        main_splitter.addWidget(right_panel)
        # 【UI优化】调整分割器初始大小，左侧280像素（接近设计系统260px），右侧自适应
        main_splitter.setSizes([280, 720])

        # 将主分割器添加到主布局
        layout.addWidget(main_splitter)

        # ========== 【状态栏】显示程序运行状态和邮件计数 ==========
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        # 显示初始提示信息
        self.status_bar.showMessage("请先登录邮箱")

        # 【邮件计数标签】显示当前文件夹的邮件数量
        # addPermanentWidget将组件固定在状态栏右侧（不会被临时消息覆盖）
        self.count_label = QLabel()
        self.status_bar.addPermanentWidget(self.count_label)

    def create_menubar(self):
        """
        【创建菜单栏】在窗口顶部创建菜单（文件、邮件、工具）

        功能：
        1. 文件菜单：写邮件、切换账户、退出
        2. 邮件菜单：刷新、转发、删除
        3. 工具菜单：通信簿、邮件夹管理

        【Qt菜单系统】
        - QMenuBar: 菜单栏（包含多个菜单）
        - QMenu: 单个菜单（如"文件"菜单）
        - QAction: 菜单项（如"写邮件"）

        参数：无
        返回值：无
        """
        # 获取主窗口的菜单栏（QMainWindow自带menuBar）
        menubar = self.menuBar()

        # ========== 【文件菜单】 ==========
        file_menu = menubar.addMenu("文件")

        # 写邮件菜单项
        compose_action = QAction("写邮件", self)
        # 设置快捷键为Ctrl+N（用户按Ctrl+N即可快速写邮件）
        compose_action.setShortcut("Ctrl+N")
        # 【信号连接】点击菜单项时调用on_compose方法
        compose_action.triggered.connect(self.on_compose)
        file_menu.addAction(compose_action)

        # 添加分隔线，将菜单项分组显示
        file_menu.addSeparator()

        # 切换账户菜单项
        switch_action = QAction("切换账户", self)
        switch_action.triggered.connect(self.show_login)
        file_menu.addAction(switch_action)

        # 退出程序菜单项
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        # self.close是QMainWindow的方法，关闭主窗口
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ========== 【邮件菜单】 ==========
        mail_menu = menubar.addMenu("邮件")

        # 刷新邮件列表菜单项
        refresh_action = QAction("刷新", self)
        refresh_action.setShortcut("F5")  # 快捷键F5
        refresh_action.triggered.connect(self.on_refresh)
        mail_menu.addAction(refresh_action)

        # 转发邮件菜单项
        forward_action = QAction("转发", self)
        forward_action.triggered.connect(self.on_forward)
        mail_menu.addAction(forward_action)

        # 删除邮件菜单项
        delete_action = QAction("删除", self)
        delete_action.setShortcut("Delete")  # 快捷键Delete
        delete_action.triggered.connect(self.on_delete)
        mail_menu.addAction(delete_action)

        # ========== 【工具菜单】 ==========
        tools_menu = menubar.addMenu("工具")

        # 打开通信簿菜单项
        contacts_action = QAction("通信簿", self)
        contacts_action.triggered.connect(self.on_contacts)
        tools_menu.addAction(contacts_action)

        # 邮件夹管理菜单项
        folders_action = QAction("邮件夹管理", self)
        folders_action.triggered.connect(self.on_folders)
        tools_menu.addAction(folders_action)

    def create_toolbar(self):
        """
        【创建工具栏】在窗口顶部创建快捷操作按钮

        功能：提供常用操作的快捷按钮，方便用户快速访问
        包括：写邮件、刷新、转发、删除、通信簿、邮件夹、切换账户

        【工具栏特点】
        - 比菜单更直观，一键可达
        - 可以显示图标和文字（本程序只显示文字）
        - 固定在窗口顶部，不可移动

        参数：无
        返回值：无
        """
        # 创建工具栏对象
        toolbar = QToolBar()
        # setMovable(False)禁止用户拖动工具栏位置
        toolbar.setMovable(False)
        # 设置工具栏按钮样式：文字显示在图标旁边（本程序未设置图标，所以只显示文字）
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        # 将工具栏添加到主窗口
        self.addToolBar(toolbar)

        # 【写邮件按钮】
        self.compose_action = QAction("写邮件", self)
        self.compose_action.triggered.connect(self.on_compose)
        toolbar.addAction(self.compose_action)

        # 添加分隔符，将按钮分组
        toolbar.addSeparator()

        # 【刷新按钮】刷新邮件列表
        self.refresh_action = QAction("刷新", self)
        self.refresh_action.triggered.connect(self.on_refresh)
        toolbar.addAction(self.refresh_action)

        toolbar.addSeparator()

        # 【转发按钮】转发当前选中的邮件
        self.forward_action = QAction("转发", self)
        self.forward_action.triggered.connect(self.on_forward)
        toolbar.addAction(self.forward_action)

        # 【删除按钮】删除当前选中的邮件
        self.delete_action = QAction("删除", self)
        self.delete_action.triggered.connect(self.on_delete)
        toolbar.addAction(self.delete_action)

        toolbar.addSeparator()

        # 【通信簿按钮】打开联系人管理界面
        self.contacts_action = QAction("通信簿", self)
        self.contacts_action.triggered.connect(self.on_contacts)
        toolbar.addAction(self.contacts_action)

        # 【邮件夹管理按钮】管理邮件文件夹
        self.folders_action = QAction("邮件夹", self)
        self.folders_action.triggered.connect(self.on_folders)
        toolbar.addAction(self.folders_action)

        toolbar.addSeparator()

        # 【切换账户按钮】登录其他邮箱账户
        self.switch_action = QAction("切换账户", self)
        self.switch_action.triggered.connect(self.show_login)
        toolbar.addAction(self.switch_action)

    def show_login(self):
        """
        【显示登录对话框】让用户输入邮箱账号和密码

        功能：
        1. 弹出登录对话框，让用户输入邮箱信息
        2. 如果用户点击"确定"，保存账户信息并连接服务器
        3. 如果用户点击"取消"且当前没有登录账户，则退出程序

        【对话框返回值】
        - Accepted: 用户点击了"确定"按钮
        - Rejected: 用户点击了"取消"按钮或关闭了对话框

        参数：无
        返回值：无
        """
        # 创建登录对话框（self作为父窗口）
        dialog = LoginDialog(self)

        # exec_()显示对话框并等待用户操作（模态对话框，阻塞其他窗口操作）
        if dialog.exec_() == LoginDialog.Accepted:
            # 用户点击了"确定"，获取输入的账户信息
            self.account = dialog.get_account()
            # 连接邮件服务器
            self.setup_connections()
        elif not self.account:
            # 用户点击了"取消"且没有已登录的账户，退出程序
            QApplication.quit()

    def setup_connections(self):
        """
        【设置邮件服务器连接】登录成功后连接IMAP和SMTP服务器

        功能：
        1. 创建邮件接收器（EmailReceiver），连接IMAP服务器
        2. 创建邮件发送器（EmailSender），准备SMTP服务器连接
        3. 加载邮件文件夹列表
        4. 刷新收件箱邮件

        【IMAP和SMTP】
        - IMAP (Internet Message Access Protocol): 用于接收邮件的协议
        - SMTP (Simple Mail Transfer Protocol): 用于发送邮件的协议

        参数：无
        返回值：无
        """
        # 在状态栏显示"正在连接服务器..."
        self.status_bar.showMessage("正在连接服务器...")
        # processEvents()让界面立即刷新，否则状态栏文字不会立即显示
        QApplication.processEvents()

        # 【创建邮件接收器】传入账户信息
        self.receiver = EmailReceiver(self.account)
        # 尝试连接IMAP服务器
        success, msg = self.receiver.connect()

        # 如果连接失败
        if not success:
            # 显示错误消息框
            QMessageBox.critical(self, "连接失败", msg)
            self.status_bar.showMessage("连接失败")
            # 重新显示登录对话框，让用户重新输入账号密码
            self.show_login()
            return

        # 【创建邮件发送器】传入账户信息（此时不连接，发送时才连接）
        self.sender = EmailSender(self.account)

        # 更新窗口标题，显示当前登录的邮箱地址
        self.setWindowTitle(f"邮件客户端 - {self.account.email}")
        self.status_bar.showMessage("已连接")

        # 从服务器加载文件夹列表（收件箱、已发送、草稿箱等）
        self.load_folders()

        # 获取收件箱的邮件列表
        self.on_refresh()

    def get_display_folder_name(self, folder: str) -> str:
        """
        【获取文件夹的中文显示名称】将英文文件夹名转换为中文

        例如：
        - "INBOX" -> "收件箱"
        - "Sent Messages" -> "已发送"
        - "MyFolder" -> "MyFolder"（没有映射则返回原名）

        参数：
            folder: 服务器返回的英文文件夹名

        返回值：
            中文显示名称，如果没有映射则返回原名
        """
        # get()方法：如果folder在字典中，返回对应的中文名；否则返回folder本身
        return self.FOLDER_NAME_MAP.get(folder, folder)

    def get_real_folder_name(self, display_name: str) -> str:
        """
        【从显示名称获取真实文件夹名】将中文名转换回英文（反向映射）

        例如：
        - "收件箱" -> "INBOX"
        - "已发送" -> "Sent Messages"

        参数：
            display_name: 显示给用户的中文名称

        返回值：
            服务器使用的真实文件夹名
        """
        # 遍历映射字典，查找中文名对应的英文名
        for real, display in self.FOLDER_NAME_MAP.items():
            if display == display_name:
                return real
        # 如果没找到映射，返回原名
        return display_name

    def load_folders(self):
        """
        【加载邮件夹列表】从服务器获取所有文件夹并显示在下拉框中

        功能：
        1. 从IMAP服务器获取所有文件夹（收件箱、已发送、草稿箱等）
        2. 将英文文件夹名转换为中文显示
        3. 保存中英文名称的映射关系
        4. 填充到文件夹下拉框

        参数：无
        返回值：无
        """
        if not self.receiver:
            return

        # 【阻止信号发送】在批量操作时，暂时禁止下拉框发送信号，避免触发多次刷新
        self.folder_combo.blockSignals(True)
        # 清空下拉框内容
        self.folder_combo.clear()

        # 从服务器获取所有文件夹列表（返回英文名称列表）
        folders = self.receiver.get_folders()

        # 保存显示名称到真实名称的映射字典（用于切换文件夹时查找真实名称）
        self.folder_display_map = {}
        for folder in folders:
            # 将英文名转换为中文显示名
            display_name = self.get_display_folder_name(folder)
            # 添加到下拉框
            self.folder_combo.addItem(display_name)
            # 保存映射关系
            self.folder_display_map[display_name] = folder

        # 【恢复信号发送】重新启用下拉框信号
        self.folder_combo.blockSignals(False)

    def on_folder_changed(self, display_name: str):
        """
        【文件夹切换事件】当用户在下拉框中选择不同文件夹时调用

        功能：
        1. 获取用户选择的文件夹的真实名称
        2. 更新当前文件夹
        3. 刷新邮件列表

        参数：
            display_name: 用户选择的文件夹显示名称（中文）

        返回值：无
        """
        if display_name:
            # 从显示名称获取真实文件夹名（如："收件箱" -> "INBOX"）
            real_folder = self.folder_display_map.get(display_name, display_name)
            # 更新当前文件夹
            self.current_folder = real_folder
            # 刷新邮件列表（从服务器获取该文件夹的邮件）
            self.on_refresh()

    def on_refresh(self):
        """刷新邮件列表"""
        if not self.receiver:
            return

        progress = QProgressDialog("正在获取邮件...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        QApplication.processEvents()

        try:
            emails = self.receiver.fetch_emails(folder=self.current_folder, limit=50)
            self.manager.set_emails(emails)
            self.apply_sort()
            self.status_bar.showMessage(f"已获取 {len(emails)} 封邮件")
        except Exception as e:
            QMessageBox.warning(self, "获取失败", f"获取邮件失败: {str(e)}")
        finally:
            progress.close()

    def apply_sort(self):
        """应用排序"""
        emails = self.manager.get_all_emails()

        if self.sort_key == "date":
            emails.sort(key=lambda x: x.date, reverse=self.sort_reverse)
        elif self.sort_key == "sender":
            emails.sort(key=lambda x: x.sender_name.lower(), reverse=self.sort_reverse)
        elif self.sort_key == "subject":
            emails.sort(key=lambda x: x.subject.lower(), reverse=self.sort_reverse)

        self.update_email_list(emails)

    def on_sort_changed(self, sort_text: str):
        """排序方式改变"""
        if "日期" in sort_text:
            self.sort_key = "date"
        elif "发件人" in sort_text:
            self.sort_key = "sender"
        elif "主题" in sort_text:
            self.sort_key = "subject"
        self.apply_sort()

    def toggle_sort_order(self):
        """切换排序顺序"""
        self.sort_reverse = not self.sort_reverse
        self.sort_order_btn.setText("降序" if self.sort_reverse else "升序")
        self.apply_sort()

    def update_email_list(self, emails: list):
        """更新邮件列表显示"""
        self.email_list.clear()
        self.count_label.setText(f"共 {len(emails)} 封邮件")

        for email in emails:
            item = QListWidgetItem()

            # 显示附件标记
            attachment_mark = " [附件]" if email.has_attachments() else ""
            display_text = f"{email.sender_name}\n{email.subject}{attachment_mark}\n{email.get_date_str()}"
            item.setText(display_text)
            item.setData(Qt.UserRole, email.uid)

            if not email.is_read:
                font = item.font()
                font.setBold(True)
                item.setFont(font)

            self.email_list.addItem(item)

        # 清空内容显示
        self.clear_email_view()

    def clear_email_view(self):
        """清空邮件视图"""
        self.subject_label.clear()
        self.sender_label.clear()
        self.date_label.clear()
        self.recipient_label.clear()
        self.content_view.clear()
        self.attachments_widget.hide()
        self.attachments_list.clear()
        self.current_email = None

    def on_email_selected(self, item: QListWidgetItem):
        """选择邮件时显示内容"""
        uid = item.data(Qt.UserRole)
        email = self.manager.get_email_by_uid(uid)

        if email:
            self.current_email = email

            # 显示邮件头
            self.subject_label.setText(email.subject)
            self.sender_label.setText(f"发件人: {email.sender_name} <{email.sender}>")
            self.date_label.setText(f"时间: {email.get_date_str()}")
            self.recipient_label.setText(f"收件人: {email.recipient}")

            # 显示邮件内容
            self.content_view.setPlainText(email.content)

            # 显示附件
            if email.has_attachments():
                self.attachments_widget.show()
                self.attachments_list.clear()
                for att in email.attachments:
                    item = QListWidgetItem(f"{att.filename} ({att.get_size_str()})")
                    item.setData(Qt.UserRole, att)
                    self.attachments_list.addItem(item)
            else:
                self.attachments_widget.hide()

            # 标记为已读
            if not email.is_read:
                self.manager.mark_as_read(uid)
                if self.receiver:
                    self.receiver.mark_as_read(uid)

                font = item.font()
                font.setBold(False)
                item.setFont(font)

    def on_email_double_clicked(self, item: QListWidgetItem):
        """双击邮件 - 如果在草稿箱则打开编辑"""
        if self.current_folder == "Drafts":
            # 在草稿箱双击，打开继续编辑
            uid = item.data(Qt.UserRole)
            email = self.manager.get_email_by_uid(uid)

            if email:
                # 构建草稿数据
                draft_data = {
                    'to': email.recipient,
                    'cc': '',
                    'bcc': '',
                    'subject': email.subject,
                    'content': email.content,
                    'attachments': []
                }

                # 删除原草稿
                if self.receiver:
                    self.receiver.delete_email(uid)
                self.manager.remove_email(uid)

                # 打开编辑对话框
                self.on_compose(draft_data)

                # 刷新列表
                self.on_refresh()

    def on_save_attachment(self, item: QListWidgetItem):
        """保存附件"""
        attachment = item.data(Qt.UserRole)
        if not attachment:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存附件",
            attachment.filename,
            "所有文件 (*.*)"
        )

        if file_path:
            try:
                with open(file_path, 'wb') as f:
                    f.write(attachment.data)
                QMessageBox.information(self, "成功", f"附件已保存到:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "保存失败", f"保存附件失败: {str(e)}")

    def show_email_context_menu(self, pos):
        """显示邮件右键菜单"""
        item = self.email_list.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)

        forward_action = menu.addAction("转发")
        forward_action.triggered.connect(self.on_forward)

        delete_action = menu.addAction("删除")
        delete_action.triggered.connect(self.on_delete)

        menu.exec_(self.email_list.mapToGlobal(pos))

    def on_compose(self, draft_data: dict = None):
        """写邮件"""
        if not self.sender:
            QMessageBox.warning(self, "提示", "请先登录邮箱")
            return

        dialog = ComposeDialog(self, contact_manager=self.contact_manager, draft_data=draft_data)
        if dialog.exec_() == ComposeDialog.Accepted:
            email_data = dialog.get_email_data()
            if email_data.get('is_draft'):
                self.save_draft(email_data)
            else:
                self.send_email(email_data)

    def on_forward(self):
        """转发邮件"""
        if not self.current_email:
            QMessageBox.information(self, "提示", "请先选择要转发的邮件")
            return

        if not self.sender:
            QMessageBox.warning(self, "提示", "请先登录邮箱")
            return

        dialog = ComposeDialog(self, forward_email=self.current_email,
                               contact_manager=self.contact_manager)
        if dialog.exec_() == ComposeDialog.Accepted:
            email_data = dialog.get_email_data()
            if email_data.get('is_draft'):
                self.save_draft(email_data)
            else:
                self.send_email(email_data)

    def save_draft(self, email_data: dict):
        """保存草稿到服务器"""
        if not self.receiver:
            QMessageBox.warning(self, "提示", "请先登录邮箱")
            return

        self.status_bar.showMessage("正在保存草稿...")
        QApplication.processEvents()

        try:
            import imaplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.mime.base import MIMEBase
            from email import encoders
            from datetime import datetime
            import time

            # 创建邮件
            msg = MIMEMultipart()
            msg['Subject'] = email_data.get('subject', '(无主题)')
            msg['To'] = email_data.get('to', '')
            msg['From'] = self.account.email
            if email_data.get('cc'):
                msg['Cc'] = email_data['cc']
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0800')

            # 添加正文
            msg.attach(MIMEText(email_data.get('content', ''), 'plain', 'utf-8'))

            # 添加附件
            for file_path in email_data.get('attachments', []):
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 'attachment',
                                       filename=os.path.basename(file_path))
                        msg.attach(part)

            # 获取草稿箱的原始名称
            drafts_folder = self.receiver.get_raw_folder_name("Drafts")

            # 保存到草稿箱
            self.receiver.connection.append(
                drafts_folder,
                '\\Draft',
                imaplib.Time2Internaldate(time.time()),
                msg.as_bytes()
            )

            QMessageBox.information(self, "成功", "草稿保存成功！")
            self.status_bar.showMessage("草稿已保存")

            # 如果当前在草稿箱，刷新列表
            if self.current_folder == "Drafts":
                self.on_refresh()

        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"保存草稿失败: {str(e)}")
            self.status_bar.showMessage("保存草稿失败")

    def send_email(self, email_data: dict):
        """发送邮件"""
        self.status_bar.showMessage("正在发送...")
        QApplication.processEvents()

        success, msg = self.sender.send_email(
            to=email_data['to'],
            subject=email_data['subject'],
            content=email_data['content'],
            attachments=email_data.get('attachments'),
            cc=email_data.get('cc', ''),
            bcc=email_data.get('bcc', ''),
            is_forward=email_data.get('is_forward', False),
            original_sender=email_data.get('original_sender', '')
        )

        if success:
            QMessageBox.information(self, "成功", "邮件发送成功！")
            self.status_bar.showMessage("发送成功")
        else:
            QMessageBox.warning(self, "发送失败", msg)
            self.status_bar.showMessage("发送失败")

    def on_delete(self):
        """删除邮件（移动到已删除文件夹）"""
        if not self.current_email:
            QMessageBox.information(self, "提示", "请先选择要删除的邮件")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除这封邮件吗？\n\n主题: {self.current_email.subject}",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            uid = self.current_email.uid

            if self.receiver:
                # 如果已经在已删除文件夹中，则永久删除
                if self.current_folder == "Deleted Messages":
                    success, msg = self.receiver.delete_email(uid)
                    if not success:
                        QMessageBox.warning(self, "删除失败", msg)
                        return
                    self.status_bar.showMessage("邮件已永久删除")
                else:
                    # 移动到已删除文件夹
                    success, msg = self.receiver.move_email(uid, "Deleted Messages")
                    if not success:
                        QMessageBox.warning(self, "删除失败", msg)
                        return
                    self.status_bar.showMessage("邮件已移动到已删除")

            self.manager.remove_email(uid)
            self.apply_sort()

    def on_search(self):
        """搜索邮件"""
        keyword = self.search_edit.text().strip()
        if not keyword:
            self.apply_sort()
            return

        search_type = self.search_type.currentText()

        if search_type == "发件人":
            results = self.manager.search_by_sender(keyword)
        elif search_type == "主题":
            results = self.manager.search_by_subject(keyword)
        else:
            results = self.manager.search_emails(keyword)

        self.update_email_list(results)
        self.status_bar.showMessage(f"找到 {len(results)} 封匹配的邮件")

    def on_clear_search(self):
        """清除搜索"""
        self.search_edit.clear()
        self.apply_sort()
        self.status_bar.showMessage("")

    def on_contacts(self):
        """打开通信簿"""
        dialog = ContactManagerDialog(self)
        dialog.exec_()
        self.contact_manager = dialog.get_contact_manager()

    def on_folders(self):
        """打开邮件夹管理"""
        dialog = FolderManagerDialog(self, self.receiver)
        dialog.exec_()
        self.load_folders()

    def closeEvent(self, event):
        """关闭窗口时断开连接"""
        if self.receiver:
            self.receiver.disconnect()
        if self.sender:
            self.sender.disconnect()
        event.accept()
