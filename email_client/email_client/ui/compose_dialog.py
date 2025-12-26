"""
【写邮件对话框模块】

本模块提供了一个功能完整的邮件撰写对话框，支持：
- 发送新邮件和转发邮件
- 多收件人、抄送、密送
- 添加和管理附件
- 保存草稿功能
- 从通讯录选择联系人
- 邮箱地址自动补全

主要类：
- ComposeDialog: 邮件撰写对话框主类

作者: 邮件客户端开发团队
创建日期: 2024
"""

# ========== 标准库导入 ==========
import os  # 用于文件路径操作，如获取文件名、判断文件是否存在、获取文件大小等

# ========== PyQt5 界面组件导入 ==========
from PyQt5.QtWidgets import (
    QDialog,          # 【对话框基类】- 用于创建弹出式窗口，本类继承自它
    QVBoxLayout,      # 【垂直布局】- 控件从上到下垂直排列
    QHBoxLayout,      # 【水平布局】- 控件从左到右水平排列
    QFormLayout,      # 【表单布局】- 以"标签-控件"形式排列，适合输入表单
    QLabel,           # 【文本标签】- 显示静态文本，如"主题:"、"内容:"等提示文字
    QLineEdit,        # 【单行输入框】- 用于输入收件人、主题等单行文本
    QTextEdit,        # 【多行文本编辑器】- 用于输入邮件正文内容
    QPushButton,      # 【按钮】- 可点击的按钮，如"发送"、"取消"等
    QMessageBox,      # 【消息对话框】- 显示提示、警告、确认等弹窗
    QFileDialog,      # 【文件选择对话框】- 用于选择附件文件
    QListWidget,      # 【列表控件】- 显示附件列表
    QListWidgetItem,  # 【列表项】- 列表中的单个条目
    QGroupBox,        # 【分组框】- 将相关控件组合在一起，带边框和标题
    QCompleter        # 【自动补全器】- 输入时提供自动补全建议
)
from PyQt5.QtCore import Qt  # PyQt5核心模块，提供枚举常量如Qt.UserRole、Qt.CaseInsensitive等

# ========== 项目内部模块导入 ==========
import sys
# 【动态路径设置】将项目根目录添加到Python模块搜索路径中，确保可以导入项目内的其他模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.email_model import Email  # 邮件数据模型，表示一封邮件的结构
from core.contact_manager import ContactManager  # 联系人管理器，用于获取和管理联系人信息


class ComposeDialog(QDialog):
    """
    【邮件撰写对话框类】

    这是一个功能完整的邮件编写界面，继承自QDialog（对话框）。
    用户可以在这个对话框中撰写新邮件、转发邮件或编辑草稿。

    主要功能：
    1. 输入收件人、抄送、密送（支持多个邮箱）
    2. 输入邮件主题和正文内容
    3. 添加和删除附件
    4. 保存为草稿或直接发送
    5. 从通讯录选择联系人
    6. 邮箱地址自动补全

    属性说明：
        forward_email (Email): 要转发的邮件对象，如果是转发邮件则有值，否则为None
        contact_manager (ContactManager): 联系人管理器，用于获取联系人列表
        attachments (list): 附件文件路径列表
        is_draft (bool): 标记是否保存为草稿（True）还是发送（False）

        界面控件：
        - to_edit: 收件人输入框
        - cc_edit: 抄送输入框
        - bcc_edit: 密送输入框
        - subject_edit: 主题输入框
        - content_edit: 内容编辑器
        - attachments_list: 附件列表

    使用示例：
        # 写新邮件
        dialog = ComposeDialog(parent)
        if dialog.exec_() == QDialog.Accepted:
            email_data = dialog.get_email_data()

        # 转发邮件
        dialog = ComposeDialog(parent, forward_email=email_obj)

        # 编辑草稿
        dialog = ComposeDialog(parent, draft_data={'to': 'test@example.com', ...})
    """

    def __init__(self, parent=None, forward_email: Email = None, contact_manager: ContactManager = None, draft_data: dict = None):
        """
        【构造函数】初始化邮件撰写对话框

        参数说明：
            parent (QWidget, optional): 父窗口对象，用于将对话框关联到主窗口
            forward_email (Email, optional): 要转发的邮件对象。如果提供此参数，对话框会自动填充转发内容
            contact_manager (ContactManager, optional): 联系人管理器。如果不提供则创建新实例
            draft_data (dict, optional): 草稿数据字典，包含to、cc、bcc、subject、content、attachments等键

        返回值：
            无

        执行流程：
            1. 调用父类QDialog的构造函数
            2. 保存转发邮件对象和联系人管理器
            3. 初始化附件列表和草稿标记
            4. 调用init_ui()创建界面
            5. 如果是转发邮件，填充转发内容
            6. 如果是编辑草稿，加载草稿数据
        """
        # 调用父类QDialog的构造函数，parent参数用于建立窗口的父子关系
        super().__init__(parent)

        # 保存要转发的邮件对象（如果是转发操作）
        self.forward_email = forward_email

        # 初始化联系人管理器，如果没有传入则创建新实例
        # 【or运算符】：如果contact_manager为None，则使用ContactManager()
        self.contact_manager = contact_manager or ContactManager()

        # 初始化附件列表，用于存储用户选择的附件文件的完整路径
        self.attachments = []

        # 【草稿标记】标记用户是保存草稿(True)还是发送邮件(False)
        self.is_draft = False

        # 创建并布局所有界面控件
        self.init_ui()

        # 【条件处理】根据不同情况初始化对话框内容
        if forward_email:
            # 如果是转发邮件，填充转发内容（主题、正文等）
            self.setup_forward()
        elif draft_data:
            # 如果是编辑草稿，加载草稿数据
            self.load_draft(draft_data)

    def init_ui(self):
        """
        【界面初始化方法】创建并布局所有界面控件

        参数说明：
            无

        返回值：
            无

        功能说明：
            创建对话框的所有可视元素，包括：
            1. 收件人区域（收件人、抄送、密送输入框和通讯录按钮）
            2. 主题输入框
            3. 内容编辑器
            4. 附件列表和管理按钮
            5. 底部操作按钮（保存草稿、发送、取消）

        布局结构：
            垂直布局 (QVBoxLayout)
            ├─ 收件人分组框 (QGroupBox)
            │  ├─ 收件人行（输入框 + 通讯录按钮）
            │  ├─ 抄送行（输入框 + 通讯录按钮）
            │  └─ 密送行（输入框 + 通讯录按钮）
            ├─ 主题行
            ├─ 内容编辑器
            ├─ 附件分组框
            │  ├─ 附件列表
            │  └─ 按钮行（添加附件、移除附件）
            └─ 操作按钮行（保存草稿、发送、取消）
        """
        # ========== 窗口基本设置 ==========
        # 根据是否转发邮件设置不同的窗口标题
        if self.forward_email:
            self.setWindowTitle("转发邮件")
        else:
            self.setWindowTitle("写邮件")

        # 【UI优化】调整对话框尺寸，确保输入框有足够宽度
        self.setMinimumSize(700, 600)
        self.resize(700, 600)
        self.setModal(True)

        # 创建主垂直布局
        layout = QVBoxLayout(self)
        # 【UI优化】使用设计系统的间距
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ========== 收件人区域 ==========
        # 【UI优化】创建分组框，使用垂直布局替代表单布局以获得更好的控制
        recipients_group = QGroupBox("收件人")
        recipients_layout = QVBoxLayout()
        recipients_layout.setSpacing(12)  # 【UI优化】行间距

        # --- 收件人输入行 ---
        to_layout = QHBoxLayout()
        to_layout.setSpacing(8)
        to_label = QLabel("收件人:")
        to_label.setFixedWidth(50)  # 【UI优化】固定标签宽度
        to_layout.addWidget(to_label)

        self.to_edit = QLineEdit()
        self.to_edit.setPlaceholderText("多个收件人用逗号或分号分隔")
        self.to_edit.setMinimumHeight(32)  # 【UI优化】设置输入框最小高度
        self._setup_completer(self.to_edit)
        to_layout.addWidget(self.to_edit, 1)  # 【UI优化】stretch=1 让输入框自动扩展

        # 【UI优化】通信簿按钮 - 调整尺寸和字体
        self.contacts_btn = QPushButton("选择")
        self.contacts_btn.setFixedSize(52, 30)
        self.contacts_btn.setStyleSheet("font-size: 11px; padding: 2px 4px;")  # 【UI优化】缩小字体确保完整显示
        self.contacts_btn.clicked.connect(lambda: self.select_from_contacts('to'))
        to_layout.addWidget(self.contacts_btn)
        recipients_layout.addLayout(to_layout)

        # --- 抄送输入行 ---
        cc_layout = QHBoxLayout()
        cc_layout.setSpacing(8)
        cc_label = QLabel("抄送:")
        cc_label.setFixedWidth(50)
        cc_layout.addWidget(cc_label)

        self.cc_edit = QLineEdit()
        self.cc_edit.setPlaceholderText("抄送（可选，多个用逗号分隔）")
        self.cc_edit.setMinimumHeight(32)
        self._setup_completer(self.cc_edit)
        cc_layout.addWidget(self.cc_edit, 1)

        self.cc_contacts_btn = QPushButton("选择")
        self.cc_contacts_btn.setFixedSize(52, 30)
        self.cc_contacts_btn.setStyleSheet("font-size: 11px; padding: 2px 4px;")  # 【UI优化】缩小字体
        self.cc_contacts_btn.clicked.connect(lambda: self.select_from_contacts('cc'))
        cc_layout.addWidget(self.cc_contacts_btn)
        recipients_layout.addLayout(cc_layout)

        # --- 密送输入行 ---
        bcc_layout = QHBoxLayout()
        bcc_layout.setSpacing(8)
        bcc_label = QLabel("密送:")
        bcc_label.setFixedWidth(50)
        bcc_layout.addWidget(bcc_label)

        self.bcc_edit = QLineEdit()
        self.bcc_edit.setPlaceholderText("密送（可选，多个用逗号分隔）")
        self.bcc_edit.setMinimumHeight(32)
        self._setup_completer(self.bcc_edit)
        bcc_layout.addWidget(self.bcc_edit, 1)

        self.bcc_contacts_btn = QPushButton("选择")
        self.bcc_contacts_btn.setFixedSize(52, 30)
        self.bcc_contacts_btn.setStyleSheet("font-size: 11px; padding: 2px 4px;")  # 【UI优化】缩小字体
        self.bcc_contacts_btn.clicked.connect(lambda: self.select_from_contacts('bcc'))
        bcc_layout.addWidget(self.bcc_contacts_btn)
        recipients_layout.addLayout(bcc_layout)

        # 将布局设置为分组框的布局
        recipients_group.setLayout(recipients_layout)
        layout.addWidget(recipients_group)

        # ========== 主题输入区域 ==========
        subject_layout = QHBoxLayout()
        subject_layout.addWidget(QLabel("主题:"))  # 添加标签
        self.subject_edit = QLineEdit()  # 创建主题输入框
        self.subject_edit.setPlaceholderText("邮件主题")
        subject_layout.addWidget(self.subject_edit)
        layout.addLayout(subject_layout)  # 将主题行添加到主布局

        # ========== 邮件内容编辑区域 ==========
        layout.addWidget(QLabel("内容:"))  # 添加"内容:"标签
        # 【多行文本编辑器】QTextEdit可以输入和编辑多行文本，支持格式化
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("在这里输入邮件内容...")
        layout.addWidget(self.content_edit)  # 文本编辑器会占据剩余的大部分空间

        # ========== 附件区域 ==========
        attachments_group = QGroupBox("附件")
        attachments_layout = QVBoxLayout()

        # 创建附件列表控件，用于显示已添加的附件
        self.attachments_list = QListWidget()
        # 限制附件列表的最大高度为80像素，避免占用太多空间
        self.attachments_list.setMaximumHeight(80)
        attachments_layout.addWidget(self.attachments_list)

        # 附件操作按钮行
        attach_btn_layout = QHBoxLayout()
        self.add_attachment_btn = QPushButton("添加附件")
        # 连接到添加附件的方法
        self.add_attachment_btn.clicked.connect(self.on_add_attachment)
        attach_btn_layout.addWidget(self.add_attachment_btn)

        self.remove_attachment_btn = QPushButton("移除附件")
        # 连接到移除附件的方法
        self.remove_attachment_btn.clicked.connect(self.on_remove_attachment)
        attach_btn_layout.addWidget(self.remove_attachment_btn)

        # 【弹性空间】addStretch()添加可伸缩空间，将按钮推到左侧
        attach_btn_layout.addStretch()
        attachments_layout.addLayout(attach_btn_layout)

        attachments_group.setLayout(attachments_layout)
        layout.addWidget(attachments_group)

        # ========== 底部操作按钮 ==========
        btn_layout = QHBoxLayout()
        # 添加弹性空间，将按钮推到右侧
        btn_layout.addStretch()

        # "保存草稿"按钮
        self.draft_btn = QPushButton("保存草稿")
        self.draft_btn.clicked.connect(self.on_save_draft)
        btn_layout.addWidget(self.draft_btn)

        # "发送"按钮
        self.send_btn = QPushButton("发送")
        # 【默认按钮】设置为默认按钮，用户按回车键时会触发此按钮
        self.send_btn.setDefault(True)
        self.send_btn.clicked.connect(self.on_send)
        btn_layout.addWidget(self.send_btn)

        # "取消"按钮
        self.cancel_btn = QPushButton("取消")
        # 【reject()】关闭对话框并返回rejected状态，表示用户取消了操作
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)  # 将按钮行添加到主布局

    def _setup_completer(self, line_edit: QLineEdit):
        """
        【设置自动补全功能】为输入框配置联系人自动补全

        参数说明：
            line_edit (QLineEdit): 需要设置自动补全的输入框控件

        返回值：
            无

        功能说明：
            从联系人管理器获取所有联系人，将其格式化为"姓名 <邮箱>"的形式，
            然后创建自动补全器并应用到输入框。用户输入时会自动显示匹配的联系人建议。

        实现细节：
            1. 从contact_manager获取所有联系人对象列表
            2. 使用列表推导式将每个联系人格式化为"姓名 <邮箱>"
            3. 创建QCompleter对象并传入格式化后的邮箱列表
            4. 设置为不区分大小写匹配
            5. 将补全器应用到输入框
        """
        # 从联系人管理器获取所有联系人对象
        contacts = self.contact_manager.get_all_contacts()

        # 【列表推导式】将联系人列表转换为"姓名 <邮箱>"格式的字符串列表
        # 例如：["张三 <zhangsan@example.com>", "李四 <lisi@example.com>"]
        emails = [f"{c.name} <{c.email}>" for c in contacts]

        # 创建自动补全器对象，传入邮箱字符串列表
        completer = QCompleter(emails)

        # 【不区分大小写】设置补全时不区分大小写，用户输入"zhang"或"Zhang"都能匹配
        completer.setCaseSensitivity(Qt.CaseInsensitive)

        # 将补全器应用到输入框，用户开始输入时会自动显示匹配建议
        line_edit.setCompleter(completer)

    def select_from_contacts(self, field: str):
        """
        【从通讯录选择联系人】打开联系人选择对话框，将选中的联系人添加到指定字段

        参数说明：
            field (str): 目标字段名称，可选值：'to'（收件人）、'cc'（抄送）、'bcc'（密送）

        返回值：
            无

        功能说明：
            1. 打开联系人选择对话框
            2. 如果用户选择了联系人并确认，获取选中的联系人字符串
            3. 根据field参数，将联系人添加到对应的输入框
            4. 如果输入框已有内容，用逗号分隔后追加；否则直接设置

        使用场景：
            用户点击"通信簿"按钮时调用，避免手动输入邮箱地址
        """
        # 【延迟导入】在方法内部导入，避免循环导入问题
        from ui.contact_dialog import ContactSelectDialog

        # 创建联系人选择对话框，self作为父窗口
        dialog = ContactSelectDialog(self)

        # 【模态对话框执行】exec_()会阻塞程序，直到用户关闭对话框
        # 返回QDialog.Accepted表示用户点击了"确定"，Rejected表示点击了"取消"
        if dialog.exec_() == QDialog.Accepted:
            # 获取用户选择的联系人字符串（格式："姓名 <邮箱>"）
            contact_str = dialog.get_selected_contact()
            if contact_str:
                # 【根据字段类型添加联系人】根据field参数决定添加到哪个输入框
                if field == 'to':
                    # 获取收件人输入框的当前内容
                    current = self.to_edit.text()
                    if current:
                        # 如果已有内容，用逗号+空格连接新联系人
                        self.to_edit.setText(f"{current}, {contact_str}")
                    else:
                        # 如果为空，直接设置
                        self.to_edit.setText(contact_str)
                elif field == 'cc':
                    # 抄送字段的处理逻辑相同
                    current = self.cc_edit.text()
                    if current:
                        self.cc_edit.setText(f"{current}, {contact_str}")
                    else:
                        self.cc_edit.setText(contact_str)
                elif field == 'bcc':
                    # 密送字段的处理逻辑相同
                    current = self.bcc_edit.text()
                    if current:
                        self.bcc_edit.setText(f"{current}, {contact_str}")
                    else:
                        self.bcc_edit.setText(contact_str)

    def setup_forward(self):
        """
        【设置转发邮件内容】当转发邮件时，自动填充主题和正文

        参数说明：
            无（使用实例属性self.forward_email）

        返回值：
            无

        功能说明：
            1. 在原主题前添加"Fwd:"前缀（如果没有的话）
            2. 在邮件正文中插入原邮件的信息（发件人、日期、主题、内容）
            3. 将光标聚焦到收件人输入框，方便用户直接输入

        邮件格式：
            Fwd: 原主题

            ---------- 转发的邮件 ----------
            发件人: 张三 <zhangsan@example.com>
            日期: 2024-01-01 10:00:00
            主题: 原主题

            原邮件内容...
        """
        if self.forward_email:
            # ========== 设置主题 ==========
            # 获取原邮件主题
            original_subject = self.forward_email.subject
            # 检查主题是否已经有"Fwd:"前缀（避免重复转发时多次添加）
            if not original_subject.startswith("Fwd:"):
                # 【转发标记】在主题前添加"Fwd:"（Forward的缩写）
                self.subject_edit.setText(f"Fwd: {original_subject}")
            else:
                # 如果已有前缀，直接使用原主题
                self.subject_edit.setText(original_subject)

            # ========== 设置正文内容 ==========
            # 【三引号字符串】可以包含多行文本，保持格式
            # 【f-string】使用f""格式化字符串，可以嵌入变量
            forward_content = f"""

---------- 转发的邮件 ----------
发件人: {self.forward_email.sender_name} <{self.forward_email.sender}>
日期: {self.forward_email.get_date_str()}
主题: {self.forward_email.subject}

{self.forward_email.content}
"""
            # 将格式化好的转发内容设置到文本编辑器
            self.content_edit.setText(forward_content)

            # 【聚焦】将输入焦点设置到收件人输入框，方便用户直接输入
            # 这样用户打开对话框后可以立即开始输入收件人，无需点击
            self.to_edit.setFocus()

    def on_add_attachment(self):
        """
        【添加附件】打开文件选择对话框，让用户选择要添加的附件

        参数说明：
            无

        返回值：
            无

        功能说明：
            1. 打开文件选择对话框（支持多选）
            2. 遍历用户选择的所有文件
            3. 对每个文件：
               - 检查是否已添加（避免重复）
               - 将文件路径添加到attachments列表
               - 在附件列表控件中显示文件名和大小
               - 使用Qt.UserRole存储完整路径

        界面显示格式：
            文件名.txt (15.5 KB)
            图片.jpg (2.3 MB)
        """
        # 【打开文件选择对话框】
        # getOpenFileNames()支持多选文件，返回(文件路径列表, 选择的过滤器)
        # 参数：父窗口、对话框标题、初始目录、文件过滤器
        files, _ = QFileDialog.getOpenFileNames(
            self,              # 父窗口
            "选择附件",        # 对话框标题
            "",                # 初始目录（空字符串表示使用默认目录）
            "所有文件 (*.*)"   # 文件过滤器（*.*表示所有文件）
        )

        # 【遍历选中的文件】处理用户选择的每个文件
        for file_path in files:
            # 检查文件是否已经在附件列表中（避免重复添加）
            if file_path not in self.attachments:
                # 将文件完整路径添加到附件列表
                self.attachments.append(file_path)

                # 【提取文件名】从完整路径中获取文件名（不含路径）
                # 例如：C:\Users\test\file.txt -> file.txt
                filename = os.path.basename(file_path)

                # 【获取文件大小】以字节为单位
                size = os.path.getsize(file_path)

                # 格式化文件大小为易读格式（KB、MB等）
                size_str = self._format_size(size)

                # 创建列表项，显示"文件名 (大小)"
                item = QListWidgetItem(f"{filename} ({size_str})")

                # 【存储完整路径】使用Qt.UserRole在列表项中存储文件的完整路径
                # 这样删除时可以通过列表项获取到文件路径
                item.setData(Qt.UserRole, file_path)

                # 将列表项添加到附件列表控件中显示
                self.attachments_list.addItem(item)

    def on_remove_attachment(self):
        """
        【移除附件】删除用户选中的附件

        参数说明：
            无

        返回值：
            无

        功能说明：
            1. 获取附件列表中当前选中的项
            2. 如果有选中项：
               - 从UserRole中获取文件完整路径
               - 从self.attachments列表中移除该路径
               - 从附件列表控件中删除该项

        注意事项：
            如果用户没有选中任何附件，此方法不会执行任何操作
        """
        # 获取附件列表中当前选中的项（QListWidgetItem对象）
        current = self.attachments_list.currentItem()

        # 检查是否有选中项
        if current:
            # 【获取存储的数据】从列表项的Qt.UserRole中获取文件完整路径
            # 这个路径是在添加附件时通过setData()存储的
            file_path = current.data(Qt.UserRole)

            # 从附件路径列表中移除该文件（如果存在）
            if file_path in self.attachments:
                self.attachments.remove(file_path)

            # 【从列表控件中删除】takeItem()会移除并返回指定位置的项
            # row()方法获取该项在列表中的索引位置
            self.attachments_list.takeItem(self.attachments_list.row(current))

    def _format_size(self, size: int) -> str:
        """
        【格式化文件大小】将字节数转换为易读的格式（B、KB、MB）

        参数说明：
            size (int): 文件大小，以字节为单位

        返回值：
            str: 格式化后的文件大小字符串，如"1.5 KB"、"2.3 MB"

        功能说明：
            根据文件大小自动选择合适的单位：
            - 小于1KB：显示为字节（B）
            - 小于1MB：显示为千字节（KB），保留1位小数
            - 大于等于1MB：显示为兆字节（MB），保留1位小数

        示例：
            _format_size(500) -> "500 B"
            _format_size(1536) -> "1.5 KB"
            _format_size(2621440) -> "2.5 MB"
        """
        # 【单位换算】1 KB = 1024 B, 1 MB = 1024 KB = 1048576 B
        if size < 1024:
            # 小于1KB，直接显示字节数
            return f"{size} B"
        elif size < 1024 * 1024:
            # 小于1MB，转换为KB，保留1位小数
            # {size / 1024:.1f} 表示除以1024后保留1位小数
            return f"{size / 1024:.1f} KB"
        else:
            # 大于等于1MB，转换为MB，保留1位小数
            return f"{size / (1024 * 1024):.1f} MB"

    def load_draft(self, draft_data: dict):
        """
        【加载草稿数据】从草稿字典中恢复邮件内容

        参数说明：
            draft_data (dict): 草稿数据字典，包含以下可选键：
                - 'to': 收件人字符串
                - 'cc': 抄送字符串
                - 'bcc': 密送字符串
                - 'subject': 主题字符串
                - 'content': 邮件正文
                - 'attachments': 附件路径列表

        返回值：
            无

        功能说明：
            1. 将草稿中的收件人、抄送、密送、主题、内容填充到对应输入框
            2. 恢复附件列表（只加载仍然存在的文件）
            3. 使用get()方法安全获取字典值，如果键不存在则使用空字符串

        使用场景：
            用户继续编辑之前保存的草稿邮件
        """
        # 【安全获取字典值】get(key, default)如果key不存在则返回default
        # 将草稿中的各项内容填充到对应的输入框
        self.to_edit.setText(draft_data.get('to', ''))
        self.cc_edit.setText(draft_data.get('cc', ''))
        self.bcc_edit.setText(draft_data.get('bcc', ''))
        self.subject_edit.setText(draft_data.get('subject', ''))
        self.content_edit.setText(draft_data.get('content', ''))

        # ========== 加载附件 ==========
        # 获取草稿中的附件列表（如果没有则使用空列表）
        for file_path in draft_data.get('attachments', []):
            # 【检查文件是否存在】只加载仍然存在的附件
            # 因为草稿保存后，文件可能被移动或删除
            if os.path.exists(file_path):
                # 将文件路径添加到附件列表
                self.attachments.append(file_path)

                # 提取文件名和大小
                filename = os.path.basename(file_path)
                size = os.path.getsize(file_path)
                size_str = self._format_size(size)

                # 创建列表项并显示
                item = QListWidgetItem(f"{filename} ({size_str})")
                # 存储完整路径以便后续删除
                item.setData(Qt.UserRole, file_path)
                # 添加到附件列表控件
                self.attachments_list.addItem(item)

    def on_save_draft(self):
        """
        【保存草稿】将当前邮件内容保存为草稿

        参数说明：
            无

        返回值：
            无

        功能说明：
            1. 获取主题、内容、收件人并去除首尾空格
            2. 验证邮件是否完全为空（如果全空则不允许保存）
            3. 设置is_draft标记为True
            4. 调用accept()关闭对话框并返回Accepted状态

        与发送邮件的区别：
            - 草稿可以没有收件人（发送时必须有）
            - 草稿可以没有主题（发送时会提示）
            - 只要有任何内容就可以保存为草稿

        工作流程：
            用户点击"保存草稿"按钮 -> 验证内容 -> 设置标记 -> 关闭对话框
            -> 主窗口检测到is_draft=True -> 将邮件保存到草稿箱
        """
        # ========== 获取输入内容 ==========
        # strip()方法去除字符串首尾的空白字符（空格、换行、制表符等）
        subject = self.subject_edit.text().strip()
        # toPlainText()获取纯文本内容（不包含HTML格式）
        content = self.content_edit.toPlainText().strip()
        to = self.to_edit.text().strip()

        # ========== 验证草稿内容 ==========
        # 【草稿验证规则】草稿可以没有收件人，但至少要有主题、内容或收件人之一
        # 如果三者都为空，说明用户没有输入任何内容，不允许保存
        if not subject and not content and not to:
            QMessageBox.warning(self, "提示", "邮件内容为空，无法保存草稿")
            return  # 提前返回，不关闭对话框

        # ========== 标记为草稿并关闭对话框 ==========
        # 设置草稿标记为True，主窗口会根据此标记判断是保存草稿还是发送邮件
        self.is_draft = True
        # 【accept()】关闭对话框并返回QDialog.Accepted状态
        # 表示用户完成了操作（区别于点击"取消"按钮调用的reject()）
        self.accept()

    def on_send(self):
        """发送按钮点击"""
        to = self.to_edit.text().strip()
        subject = self.subject_edit.text().strip()
        content = self.content_edit.toPlainText()

        # 验证输入
        if not to:
            QMessageBox.warning(self, "提示", "请输入收件人邮箱")
            self.to_edit.setFocus()
            return

        # 验证所有收件人邮箱格式
        all_recipients = to.replace(';', ',').split(',')
        for addr in all_recipients:
            addr = addr.strip()
            if addr and '@' not in addr and '<' not in addr:
                QMessageBox.warning(self, "提示", f"邮箱地址格式不正确: {addr}")
                self.to_edit.setFocus()
                return

        if not subject:
            reply = QMessageBox.question(
                self, "提示",
                "邮件主题为空，是否继续发送？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                self.subject_edit.setFocus()
                return
            subject = "(无主题)"

        self.is_draft = False
        self.accept()

    def get_email_data(self) -> dict:
        """获取邮件数据"""
        return {
            'to': self.to_edit.text().strip(),
            'cc': self.cc_edit.text().strip(),
            'bcc': self.bcc_edit.text().strip(),
            'subject': self.subject_edit.text().strip() or "(无主题)",
            'content': self.content_edit.toPlainText(),
            'attachments': self.attachments.copy(),
            'is_forward': self.forward_email is not None,
            'original_sender': self.forward_email.sender if self.forward_email else "",
            'is_draft': self.is_draft
        }
