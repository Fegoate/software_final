"""
【登录对话框模块】

本文件定义了邮箱客户端的登录/配置对话框界面。
主要功能：
1. 提供图形化界面让用户输入邮箱账户信息
2. 支持多种邮箱类型的快速配置（QQ邮箱、网易邮箱等）
3. 允许自定义邮箱服务器配置
4. 可以保存和加载账户信息，避免重复输入

这是用户首次使用程序时看到的第一个界面。
"""

# ==================== 导入 PyQt5 GUI 组件 ====================
# 【PyQt5】是 Python 的图形界面开发框架，这里导入各种界面组件

from PyQt5.QtWidgets import (
    QDialog,        # 对话框基类，用于创建弹出式窗口
    QVBoxLayout,    # 垂直布局管理器，组件从上到下排列
    QHBoxLayout,    # 水平布局管理器，组件从左到右排列
    QFormLayout,    # 表单布局管理器，适合"标签：输入框"这种形式
    QLabel,         # 文本标签，用于显示提示文字
    QLineEdit,      # 单行文本输入框，用于输入邮箱、密码等
    QComboBox,      # 下拉选择框，用于选择邮箱类型
    QPushButton,    # 按钮组件，如"登录"、"取消"按钮
    QSpinBox,       # 数字输入框，用于输入端口号
    QCheckBox,      # 复选框，用于"记住密码"、"使用SSL"等选项
    QMessageBox,    # 消息提示框，用于显示警告、错误等信息
    QGroupBox       # 分组框，用于将相关控件组织在一起
)
from PyQt5.QtCore import Qt  # Qt 核心模块，包含各种枚举和常量

# ==================== 导入 Python 标准库 ====================
import sys  # 系统相关功能，这里用于修改模块搜索路径
import os   # 操作系统相关功能，这里用于处理文件路径

# 【重要】将项目根目录添加到 Python 模块搜索路径中
# 这样就可以导入 models 和 config 目录下的模块了
# os.path.abspath(__file__): 获取当前文件的绝对路径
# os.path.dirname(...): 获取父目录，调用两次得到项目根目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==================== 导入项目自定义模块 ====================
from models.email_model import EmailAccount    # 邮箱账户数据模型，用于存储账户信息
from config.settings import EMAIL_PRESETS, Settings  # EMAIL_PRESETS: 预设的邮箱配置；Settings: 配置管理类


class LoginDialog(QDialog):
    """
    【登录对话框类】

    这是一个继承自 QDialog 的对话框窗口，用于用户登录邮箱账户。

    主要属性：
        account: EmailAccount 对象，存储用户输入的账户信息
        settings: Settings 对象，用于保存和加载配置
        各种界面控件（输入框、按钮等）

    使用方法：
        # 创建对话框
        dialog = LoginDialog(parent_window)
        # 显示对话框并等待用户操作
        if dialog.exec_() == QDialog.Accepted:  # 用户点击了"登录"
            account = dialog.get_account()  # 获取账户信息
            # 使用账户信息进行登录...
        else:  # 用户点击了"取消"
            # 取消登录
    """

    def __init__(self, parent=None):
        """
        【构造函数】初始化登录对话框

        参数：
            parent: 父窗口对象，如果为 None 则这是独立窗口
                   传入父窗口可以实现窗口居中、模态对话框等效果

        执行流程：
            1. 调用父类构造函数初始化对话框
            2. 初始化账户信息为空
            3. 创建配置管理对象
            4. 构建用户界面
            5. 加载之前保存的账户信息（如果有）
        """
        super().__init__(parent)  # 调用 QDialog 的构造函数，必须先调用

        self.account = None  # 存储用户输入的账户信息，初始为 None
        self.settings = Settings()  # 创建配置管理对象，用于保存/加载账户

        self.init_ui()  # 初始化界面，创建所有控件
        self.load_saved_account()  # 尝试加载之前保存的账户信息

    def init_ui(self):
        """
        【初始化用户界面】构建对话框中的所有控件

        这个方法创建了登录对话框的完整界面，包括：
        1. 邮箱类型选择区域
        2. 账户信息输入区域（邮箱地址、密码）
        3. 服务器设置区域（IMAP/SMTP 服务器和端口）
        4. 选项区域（记住密码、使用SSL）
        5. 操作按钮（登录、取消）

        无参数，无返回值
        """
        # ========== 设置窗口基本属性 ==========
        self.setWindowTitle("邮箱登录")
        # 【UI优化】调整窗口宽度
        self.setMinimumWidth(480)
        self.setModal(True)

        # 创建【主布局】，垂直排列所有控件
        layout = QVBoxLayout(self)
        # 【UI优化】使用设计系统的间距
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ========== 邮箱类型选择区域 ==========
        type_layout = QHBoxLayout()  # 创建水平布局，让标签和下拉框并排显示
        type_layout.addWidget(QLabel("邮箱类型:"))  # 添加文字标签

        # 创建下拉选择框
        self.type_combo = QComboBox()
        # 从 EMAIL_PRESETS 字典中获取所有邮箱类型名称（如"QQ邮箱"、"网易邮箱"等）
        self.type_combo.addItems(EMAIL_PRESETS.keys())
        # 【信号与槽机制】当用户选择不同邮箱类型时，自动调用 on_type_changed 方法
        # currentTextChanged 是信号，on_type_changed 是槽函数
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)  # 将下拉框添加到水平布局

        layout.addLayout(type_layout)  # 将水平布局添加到主布局

        # ========== 提示信息标签 ==========
        # 用于显示不同邮箱类型的使用提示（比如"QQ邮箱需要使用授权码"）
        self.hint_label = QLabel()
        # 【UI优化】使用设计系统的三级文字色和说明文字字号
        self.hint_label.setStyleSheet("""
            color: #86909C;
            font-size: 12px;
            padding: 8px 12px;
            background-color: #F5F7FA;
            border-radius: 6px;
        """)
        self.hint_label.setWordWrap(True)
        layout.addWidget(self.hint_label)

        # ========== 账户信息分组 ==========
        # 【分组框】将相关的输入框组织在一起，带边框和标题
        account_group = QGroupBox("账户信息")
        # 【表单布局】自动对齐"标签：输入框"这种形式
        account_layout = QFormLayout()

        # 邮箱地址输入框
        self.email_edit = QLineEdit()  # 创建单行文本输入框
        # 设置【占位符文本】，当输入框为空时显示提示文字
        self.email_edit.setPlaceholderText("example@qq.com")
        # 添加到表单布局：第一个参数是标签文字，第二个参数是输入框控件
        account_layout.addRow("邮箱地址:", self.email_edit)

        # 密码/授权码输入框
        self.password_edit = QLineEdit()
        # 设置【密码模式】，输入的字符显示为 ● 或 * 号，保护隐私
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("请输入密码或授权码")
        account_layout.addRow("密码/授权码:", self.password_edit)

        # 将表单布局应用到分组框
        account_group.setLayout(account_layout)
        # 将整个分组框添加到主布局
        layout.addWidget(account_group)

        # ========== 服务器设置分组 ==========
        # 【邮件协议说明】
        # IMAP：接收邮件协议，用于从服务器下载邮件
        # SMTP：发送邮件协议，用于向服务器发送邮件
        server_group = QGroupBox("服务器设置")
        server_layout = QFormLayout()

        # IMAP 服务器地址输入框
        self.imap_server_edit = QLineEdit()
        server_layout.addRow("IMAP 服务器:", self.imap_server_edit)

        # IMAP 端口号输入框
        self.imap_port_spin = QSpinBox()  # 数字输入框，只能输入数字
        # 设置端口号范围：1-65535（这是网络端口的有效范围）
        self.imap_port_spin.setRange(1, 65535)
        # 设置默认值为 993（IMAP over SSL 的标准端口）
        self.imap_port_spin.setValue(993)
        server_layout.addRow("IMAP 端口:", self.imap_port_spin)

        # SMTP 服务器地址输入框
        self.smtp_server_edit = QLineEdit()
        server_layout.addRow("SMTP 服务器:", self.smtp_server_edit)

        # SMTP 端口号输入框
        self.smtp_port_spin = QSpinBox()
        self.smtp_port_spin.setRange(1, 65535)
        # 设置默认值为 465（SMTP over SSL 的标准端口）
        self.smtp_port_spin.setValue(465)
        server_layout.addRow("SMTP 端口:", self.smtp_port_spin)

        # SSL 加密选项
        # 【SSL】是一种加密协议，保护邮件传输的安全性
        self.ssl_check = QCheckBox("使用 SSL 加密")
        self.ssl_check.setChecked(True)  # 默认勾选，推荐使用加密
        # 第一个参数为空字符串，表示这一行没有左侧标签
        server_layout.addRow("", self.ssl_check)

        # 将表单布局应用到分组框
        server_group.setLayout(server_layout)
        # 将整个分组框添加到主布局
        layout.addWidget(server_group)

        # ========== 记住密码选项 ==========
        # 勾选后，下次打开程序会自动填入账户信息
        self.remember_check = QCheckBox("记住账户信息")
        self.remember_check.setChecked(True)  # 默认勾选
        layout.addWidget(self.remember_check)

        # ========== 操作按钮区域 ==========
        btn_layout = QHBoxLayout()  # 水平布局，让按钮横向排列
        btn_layout.addStretch()  # 添加弹性空间，让按钮靠右对齐

        # "登录"按钮
        self.login_btn = QPushButton("登录")
        # 设置为【默认按钮】，按 Enter 键时会自动触发这个按钮
        self.login_btn.setDefault(True)
        # 【信号与槽】点击按钮时调用 on_login 方法
        self.login_btn.clicked.connect(self.on_login)
        btn_layout.addWidget(self.login_btn)

        # "取消"按钮
        self.cancel_btn = QPushButton("取消")
        # self.reject() 是 QDialog 的方法，会关闭对话框并返回"取消"状态
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)  # 将按钮布局添加到主布局

        # ========== 初始化邮箱类型 ==========
        # 根据当前选择的邮箱类型，自动填充服务器配置
        # currentText() 获取下拉框当前选中的文字
        self.on_type_changed(self.type_combo.currentText())

    def on_type_changed(self, email_type: str):
        """
        【邮箱类型改变事件处理】当用户选择不同邮箱类型时自动更新服务器设置

        参数：
            email_type: 用户选择的邮箱类型字符串，如"QQ邮箱"、"网易邮箱"等

        功能：
            1. 从预设配置中读取对应邮箱的服务器信息
            2. 自动填充 IMAP/SMTP 服务器地址和端口
            3. 设置是否使用 SSL
            4. 显示该邮箱类型的使用提示
            5. 如果是"自定义"类型，允许用户手动编辑服务器地址

        返回值：无
        """
        # 检查选择的邮箱类型是否在预设配置中
        if email_type in EMAIL_PRESETS:
            # 获取该邮箱类型的预设配置（一个字典）
            preset = EMAIL_PRESETS[email_type]

            # 自动填充 IMAP 服务器地址
            self.imap_server_edit.setText(preset['imap_server'])
            # 自动填充 IMAP 端口号
            self.imap_port_spin.setValue(preset['imap_port'])
            # 自动填充 SMTP 服务器地址
            self.smtp_server_edit.setText(preset['smtp_server'])
            # 自动填充 SMTP 端口号
            self.smtp_port_spin.setValue(preset['smtp_port'])
            # 自动设置是否使用 SSL
            self.ssl_check.setChecked(preset['use_ssl'])
            # 显示该邮箱的使用提示（如果有）
            # .get('note', '') 表示获取 'note' 键的值，如果不存在则返回空字符串
            self.hint_label.setText(preset.get('note', ''))

            # ========== 控制服务器地址是否可编辑 ==========
            # 如果是"自定义"类型，用户需要手动输入服务器地址
            # 否则服务器地址已经预设好了，设为只读避免误改
            is_custom = (email_type == '自定义')
            # setReadOnly(True) 表示只读，setReadOnly(False) 表示可编辑
            self.imap_server_edit.setReadOnly(not is_custom)
            self.smtp_server_edit.setReadOnly(not is_custom)

    def load_saved_account(self):
        """
        【加载保存的账户信息】从配置文件中读取上次保存的账户信息并自动填充

        功能：
            1. 调用 Settings 对象的 load_account 方法读取配置
            2. 如果有保存的账户信息，自动填充到各个输入框
            3. 将邮箱类型设置为"自定义"以保留加载的配置

        这样用户下次打开程序时不需要重新输入所有信息。

        参数：无
        返回值：无
        """
        # 尝试从配置文件加载账户信息
        account = self.settings.load_account()

        # 如果加载成功（account 不为 None）
        if account:
            # 将账户信息填充到各个输入框
            self.email_edit.setText(account.email)  # 邮箱地址
            self.password_edit.setText(account.password)  # 密码/授权码
            self.imap_server_edit.setText(account.imap_server)  # IMAP 服务器
            self.imap_port_spin.setValue(account.imap_port)  # IMAP 端口
            self.smtp_server_edit.setText(account.smtp_server)  # SMTP 服务器
            self.smtp_port_spin.setValue(account.smtp_port)  # SMTP 端口
            self.ssl_check.setChecked(account.use_ssl)  # SSL 选项

            # ========== 重要：设置为自定义类型 ==========
            # 因为加载的配置可能不是标准预设，所以设置为"自定义"
            # 这样用户可以编辑服务器地址（不会被锁定为只读）
            self.type_combo.setCurrentText('自定义')
            self.imap_server_edit.setReadOnly(False)  # 允许编辑
            self.smtp_server_edit.setReadOnly(False)  # 允许编辑

    def on_login(self):
        """
        【登录按钮点击事件处理】验证用户输入并创建账户对象

        功能：
            1. 获取所有输入框的值
            2. 验证必填项是否已填写
            3. 创建 EmailAccount 对象
            4. 如果勾选了"记住账户"，保存配置到文件
            5. 关闭对话框并返回"接受"状态

        参数：无
        返回值：无（通过 self.account 属性传递账户信息）
        """
        # ========== 获取用户输入的值 ==========
        # .text() 获取文本框内容，.strip() 去除首尾空格
        email = self.email_edit.text().strip()
        password = self.password_edit.text()  # 密码不去空格，可能包含有效空格
        imap_server = self.imap_server_edit.text().strip()
        smtp_server = self.smtp_server_edit.text().strip()

        # ========== 验证用户输入 ==========
        # 检查邮箱地址是否为空
        if not email:
            # 显示警告消息框
            QMessageBox.warning(self, "提示", "请输入邮箱地址")
            self.email_edit.setFocus()  # 将光标定位到邮箱输入框
            return  # 终止登录流程

        # 检查密码是否为空
        if not password:
            QMessageBox.warning(self, "提示", "请输入密码或授权码")
            self.password_edit.setFocus()  # 将光标定位到密码输入框
            return

        # 检查服务器地址是否都已填写
        if not imap_server or not smtp_server:
            QMessageBox.warning(self, "提示", "请填写服务器地址")
            return

        # ========== 创建账户对象 ==========
        # 使用用户输入的信息创建 EmailAccount 实例
        self.account = EmailAccount(
            email=email,  # 邮箱地址
            password=password,  # 密码/授权码
            imap_server=imap_server,  # IMAP 服务器地址
            imap_port=self.imap_port_spin.value(),  # IMAP 端口号
            smtp_server=smtp_server,  # SMTP 服务器地址
            smtp_port=self.smtp_port_spin.value(),  # SMTP 端口号
            use_ssl=self.ssl_check.isChecked()  # 是否使用 SSL
        )

        # ========== 保存账户信息 ==========
        # 如果用户勾选了"记住账户信息"复选框
        if self.remember_check.isChecked():
            # 将账户信息保存到配置文件，下次自动加载
            self.settings.save_account(self.account)

        # ========== 关闭对话框 ==========
        # self.accept() 是 QDialog 的方法，会关闭对话框并返回"接受"状态
        # 调用者可以通过 dialog.exec_() == QDialog.Accepted 来判断
        self.accept()

    def get_account(self) -> EmailAccount:
        """
        【获取账户信息】返回用户输入的账户对象

        这个方法在对话框关闭后被调用，用于获取用户输入的账户信息。

        参数：无

        返回值：
            EmailAccount: 包含邮箱地址、密码、服务器配置等信息的账户对象
                         如果用户点击了"取消"，则返回 None

        使用示例：
            dialog = LoginDialog()
            if dialog.exec_() == QDialog.Accepted:
                account = dialog.get_account()  # 获取账户信息
                print(account.email)  # 打印邮箱地址
        """
        return self.account
