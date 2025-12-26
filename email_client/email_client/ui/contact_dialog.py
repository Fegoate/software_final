"""
【通讯录对话框模块】

本文件实现了邮件客户端的通讯录管理功能，包含三个主要对话框：
1. ContactEditDialog - 联系人编辑对话框，用于添加或修改单个联系人信息
2. ContactManagerDialog - 通讯录管理对话框，用于批量管理联系人（增删改查、导入导出）
3. ContactSelectDialog - 联系人选择对话框，用于在撰写邮件时快速选择收件人

主要功能：
- 添加、编辑、删除联系人
- 搜索和分组过滤联系人
- 导入/导出 CSV 和 JSON 格式的通讯录
- 双击快速选择联系人

作者：邮件客户端开发团队
日期：2024
"""

# ========== PyQt5 图形界面组件导入 ==========
from PyQt5.QtWidgets import (
    QDialog,              # 【对话框基类】，所有弹窗对话框都继承自这个类
    QVBoxLayout,          # 【垂直布局管理器】，让控件从上到下排列
    QHBoxLayout,          # 【水平布局管理器】，让控件从左到右排列
    QFormLayout,          # 【表单布局管理器】，自动生成"标签:输入框"这样的表单行
    QLabel,               # 【标签控件】，用于显示静态文本（如"姓名:"、"邮箱:"）
    QLineEdit,            # 【单行文本输入框】，用于输入姓名、邮箱等简短信息
    QTextEdit,            # 【多行文本编辑器】，用于输入备注等较长文本
    QPushButton,          # 【按钮控件】，用于"保存"、"取消"等操作按钮
    QTableWidget,         # 【表格控件】，用于以表格形式展示多个联系人
    QTableWidgetItem,     # 【表格单元项】，表格中每个单元格的数据项
    QHeaderView,          # 【表头视图】，用于设置表格列宽等属性
    QMessageBox,          # 【消息框】，用于显示提示、警告、确认等弹窗
    QFileDialog,          # 【文件对话框】，用于打开/保存文件时的文件选择窗口
    QComboBox,            # 【下拉框控件】，用于选择联系人分组
    QGroupBox,            # 【分组框】，用于将相关控件组合在一起（本文件中导入但未使用）
    QSplitter,            # 【分割器】，可拖动调整两侧窗口大小（本文件中导入但未使用）
    QWidget,              # 【控件基类】，所有可视控件的父类（本文件中导入但未使用）
    QAbstractItemView     # 【抽象项视图】，用于设置表格的选择模式和编辑模式
)
from PyQt5.QtCore import Qt  # Qt核心常量，如对齐方式、键盘修饰符等

# ========== Python 标准库导入 ==========
import sys  # 系统相关功能，这里用于修改 Python 模块搜索路径
import os   # 操作系统接口，这里用于处理文件路径

# 【动态添加父目录到模块搜索路径】
# 这样可以导入项目其他目录下的模块（如 models、core 目录）
# os.path.abspath(__file__) - 获取当前文件的绝对路径
# os.path.dirname(...) - 获取父目录，调用两次得到项目根目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ========== 项目内部模块导入 ==========
from models.email_model import Contact          # 【Contact 数据模型类】，表示单个联系人的数据结构
from core.contact_manager import ContactManager  # 【联系人管理器】，负责联系人的业务逻辑（增删改查、导入导出）


class ContactEditDialog(QDialog):
    """
    【联系人编辑对话框类】

    这个对话框用于添加新联系人或编辑现有联系人的信息。
    它包含姓名、邮箱、电话、分组、备注等输入字段。

    使用场景：
    - 在通讯录管理器中点击"添加"按钮时创建此对话框（不传 contact 参数）
    - 在通讯录管理器中点击"编辑"按钮时创建此对话框（传入现有 contact）

    示例：
        # 添加新联系人
        dialog = ContactEditDialog(parent_window)
        if dialog.exec_() == QDialog.Accepted:
            new_contact = dialog.get_contact()

        # 编辑现有联系人
        dialog = ContactEditDialog(parent_window, existing_contact)
        if dialog.exec_() == QDialog.Accepted:
            updated_contact = dialog.get_contact()
    """

    def __init__(self, parent=None, contact: Contact = None):
        """
        初始化联系人编辑对话框

        参数说明：
            parent (QWidget, 可选): 父窗口对象，设置后对话框会居中显示在父窗口上方
            contact (Contact, 可选): 要编辑的联系人对象
                                     - 如果为 None，表示添加新联系人
                                     - 如果传入 Contact 对象，表示编辑现有联系人

        工作流程：
            1. 调用父类 QDialog 的初始化方法
            2. 保存 contact 参数到实例变量
            3. 调用 init_ui() 创建界面控件
            4. 如果是编辑模式，加载联系人数据到输入框
        """
        super().__init__(parent)  # 【调用父类构造函数】，完成 QDialog 的基础初始化
        self.contact = contact    # 【保存联系人对象】，用于判断是添加还是编辑模式
        self.init_ui()            # 【初始化用户界面】，创建所有控件和布局

        # 【编辑模式】：如果传入了联系人对象，将其数据填充到输入框中
        if contact:
            self.load_contact(contact)

    def init_ui(self):
        """
        初始化用户界面，创建所有输入控件和按钮

        界面结构：
            ┌─────────────────────────┐
            │  姓名: [输入框]         │
            │  邮箱: [输入框]         │
            │  电话: [输入框]         │
            │  分组: [下拉框]         │
            │  备注: [多行输入框]     │
            │                         │
            │        [保存] [取消]    │
            └─────────────────────────┘

        返回值：无
        """
        # 【设置窗口标题】：根据是否有 contact 判断是"编辑"还是"添加"
        self.setWindowTitle("编辑联系人" if self.contact else "添加联系人")
        # 【UI优化】调整最小宽度
        self.setMinimumWidth(400)

        # 【创建主垂直布局】
        layout = QVBoxLayout(self)
        # 【UI优化】使用设计系统的间距
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ========== 表单输入区域 ==========
        # 【创建表单布局】：自动对齐"标签:输入框"，美观整齐
        form_layout = QFormLayout()

        # 【姓名输入框】
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("联系人姓名")  # 【占位符文本】，输入框为空时显示的提示文字
        form_layout.addRow("姓名:", self.name_edit)      # 添加到表单：左侧标签"姓名:"，右侧输入框

        # 【邮箱输入框】
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("email@example.com")
        form_layout.addRow("邮箱:", self.email_edit)

        # 【电话输入框】
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("电话号码（可选）")
        form_layout.addRow("电话:", self.phone_edit)

        # 【分组下拉框】
        self.group_combo = QComboBox()
        self.group_combo.setEditable(True)  # 【设置可编辑】，用户可以选择现有分组，也可以输入新分组名
        # 【添加预设分组选项】
        self.group_combo.addItems(["默认", "家人", "朋友", "同事", "客户"])
        form_layout.addRow("分组:", self.group_combo)

        # 【备注多行文本框】
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("备注信息（可选）")
        self.notes_edit.setMaximumHeight(80)  # 【限制最大高度】，避免占用太多空间
        form_layout.addRow("备注:", self.notes_edit)

        # 【将表单布局添加到主布局】
        layout.addLayout(form_layout)

        # ========== 按钮区域 ==========
        btn_layout = QHBoxLayout()  # 【水平布局】，让按钮横向排列
        btn_layout.addStretch()     # 【添加弹性空间】，将按钮推到右侧

        # 【保存按钮】
        self.save_btn = QPushButton("保存")
        # 【连接信号与槽】：点击按钮时调用 on_save 方法
        # clicked 是按钮的信号，connect 连接到处理函数（槽）
        self.save_btn.clicked.connect(self.on_save)
        btn_layout.addWidget(self.save_btn)

        # 【取消按钮】
        self.cancel_btn = QPushButton("取消")
        # reject() 是 QDialog 的内置方法，关闭对话框并返回 Rejected 状态
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        # 【将按钮布局添加到主布局】
        layout.addLayout(btn_layout)

    def load_contact(self, contact: Contact):
        """
        加载联系人信息到各个输入框（用于编辑模式）

        参数说明：
            contact (Contact): 要加载的联系人对象

        功能：
            将 Contact 对象的各个字段值填充到对应的输入控件中，
            这样用户就可以看到现有信息并进行修改。

        返回值：无
        """
        self.name_edit.setText(contact.name)           # 设置姓名输入框的文本
        self.email_edit.setText(contact.email)         # 设置邮箱输入框的文本
        self.phone_edit.setText(contact.phone)         # 设置电话输入框的文本
        self.group_combo.setCurrentText(contact.group) # 设置下拉框当前选中的分组
        self.notes_edit.setPlainText(contact.notes)    # 设置备注文本框的内容

    def on_save(self):
        """
        保存按钮的点击事件处理函数

        功能流程：
            1. 获取并去除首尾空格的用户输入
            2. 验证必填字段（姓名、邮箱）是否填写
            3. 验证邮箱格式是否包含 @ 符号
            4. 创建 Contact 对象保存所有信息
            5. 调用 accept() 关闭对话框并返回 Accepted 状态

        返回值：无

        注意：
            - 如果验证失败，会弹出警告框并 return，不会关闭对话框
            - 只有验证通过才会调用 accept() 关闭对话框
        """
        # 【获取用户输入】并去除首尾空格
        # strip() 方法会移除字符串开头和结尾的空白字符（空格、制表符、换行符等）
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()

        # 【验证姓名】：检查是否为空
        # 空字符串在 Python 中是 False，not "" 为 True
        if not name:
            QMessageBox.warning(self, "提示", "请输入联系人姓名")
            return  # 【提前返回】，不继续执行后续代码

        # 【验证邮箱】：检查是否为空且包含 @ 符号
        # 这是一个简单的邮箱格式验证，确保至少有 @ 符号
        if not email or '@' not in email:
            QMessageBox.warning(self, "提示", "请输入有效的邮箱地址")
            return

        # 【创建 Contact 对象】：封装所有联系人信息
        self.contact = Contact(
            name=name,
            email=email,
            phone=self.phone_edit.text().strip(),     # 电话号码（可选）
            group=self.group_combo.currentText(),     # 当前选中或输入的分组名
            notes=self.notes_edit.toPlainText().strip()  # toPlainText() 获取多行文本的纯文本内容
        )

        # 【接受对话框】：关闭窗口并返回 Accepted 状态
        # 调用者可以通过 dialog.exec_() == QDialog.Accepted 判断用户是否点击了保存
        self.accept()

    def get_contact(self) -> Contact:
        """
        获取用户保存的联系人对象

        返回值：
            Contact: 用户创建或修改后的联系人对象
                    如果用户点击了"取消"，返回的可能是 None（添加模式）或原对象（编辑模式）

        使用方式：
            dialog = ContactEditDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                contact = dialog.get_contact()  # 获取用户保存的联系人
                # 进行后续处理...
        """
        return self.contact


class ContactManagerDialog(QDialog):
    """
    【通讯录管理对话框类】

    这是通讯录的主界面，提供完整的联系人管理功能。
    用户可以在这里查看、添加、编辑、删除联系人，以及进行搜索、分组过滤、导入导出等操作。

    主要功能：
    - 以表格形式展示所有联系人
    - 搜索联系人（支持姓名、邮箱、电话）
    - 按分组筛选联系人
    - 添加新联系人（打开 ContactEditDialog）
    - 编辑现有联系人（双击或点击"编辑"按钮）
    - 删除联系人（带确认提示）
    - 导入联系人（支持 CSV 和 JSON 格式）
    - 导出联系人（支持 CSV 和 JSON 格式）

    界面布局：
        ┌────────────────────────────────────┐
        │ 搜索: [输入框]  [分组过滤下拉框]  │
        ├────────────────────────────────────┤
        │ 姓名 │ 邮箱 │ 电话 │ 分组 │ 备注  │
        │─────────────────────────────────── │
        │ 张三 │ ... │ ... │ ... │ ...    │
        │ 李四 │ ... │ ... │ ... │ ...    │
        ├────────────────────────────────────┤
        │ [添加][编辑][删除] [导入][导出] [关闭] │
        └────────────────────────────────────┘
    """

    def __init__(self, parent=None):
        """
        初始化通讯录管理对话框

        参数说明：
            parent (QWidget, 可选): 父窗口对象

        工作流程：
            1. 调用父类构造函数
            2. 创建 ContactManager 实例（负责联系人的业务逻辑）
            3. 初始化 selected_contact 为 None（当前选中的联系人）
            4. 创建界面
            5. 从数据库加载所有联系人到表格中
        """
        super().__init__(parent)  # 【调用父类构造函数】
        self.manager = ContactManager()  # 【创建联系人管理器】，处理数据持久化和业务逻辑
        self.selected_contact: Contact = None  # 【当前选中的联系人】，用于编辑和删除操作
        self.init_ui()        # 【初始化界面】
        self.load_contacts()  # 【加载联系人数据】，从数据库读取并显示在表格中

    def init_ui(self):
        """
        初始化通讯录管理界面

        创建的主要组件：
        1. 搜索栏 - 包含搜索输入框和分组过滤下拉框
        2. 联系人表格 - 显示所有联系人信息
        3. 按钮栏 - 包含添加、编辑、删除、导入、导出、关闭按钮

        返回值：无
        """
        self.setWindowTitle("通信簿管理")
        # 【UI优化】调整最小尺寸
        self.setMinimumSize(750, 520)

        # 【创建主垂直布局】
        layout = QVBoxLayout(self)
        # 【UI优化】使用设计系统的间距
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ========== 搜索栏区域 ==========
        search_layout = QHBoxLayout()  # 【水平布局】，让搜索控件横向排列

        # 【搜索标签】
        search_layout.addWidget(QLabel("搜索:"))

        # 【搜索输入框】
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入姓名、邮箱或电话搜索...")
        # 【连接文本改变信号】：每次输入内容变化时自动调用 on_search 方法
        # 这实现了【实时搜索】功能，无需点击搜索按钮
        self.search_edit.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_edit)

        # 【分组过滤下拉框】
        self.group_filter = QComboBox()
        self.group_filter.addItem("全部分组")  # 默认选项，显示所有联系人
        # 【连接选项改变信号】：当用户选择不同分组时，自动筛选联系人
        self.group_filter.currentTextChanged.connect(self.on_filter_group)
        search_layout.addWidget(self.group_filter)

        # 【将搜索栏添加到主布局】
        layout.addLayout(search_layout)

        # ========== 联系人表格区域 ==========
        self.table = QTableWidget()  # 【创建表格控件】
        self.table.setColumnCount(5)  # 【设置列数】：5列分别是姓名、邮箱、电话、分组、备注
        # 【设置表头标签】
        self.table.setHorizontalHeaderLabels(["姓名", "邮箱", "电话", "分组", "备注"])

        # 【设置选择行为】：SelectRows 表示点击单元格时选中整行
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 【设置选择模式】：SingleSelection 表示一次只能选中一行
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        # 【禁用编辑】：NoEditTriggers 表示表格不可直接编辑，必须通过"编辑"按钮
        # 这样可以更好地控制数据验证流程
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 【设置列宽模式】：第2列（索引1，邮箱列）设置为 Stretch（自动拉伸填充剩余空间）
        # 这样邮箱列会自动占用多余空间，其他列保持默认宽度
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        # 【连接选择改变信号】：当用户选中不同行时，更新按钮的启用状态
        self.table.itemSelectionChanged.connect(self.on_selection_changed)

        # 【连接双击信号】：双击表格行时打开编辑对话框
        self.table.doubleClicked.connect(self.on_edit)

        # 【将表格添加到主布局】
        layout.addWidget(self.table)

        # ========== 按钮区域 ==========
        btn_layout = QHBoxLayout()  # 【水平布局】，让所有按钮横向排列

        # 【添加按钮】：打开空白的编辑对话框以添加新联系人
        self.add_btn = QPushButton("添加")
        self.add_btn.clicked.connect(self.on_add)  # 连接到添加联系人的处理函数
        btn_layout.addWidget(self.add_btn)

        # 【编辑按钮】：打开已填充数据的编辑对话框
        self.edit_btn = QPushButton("编辑")
        self.edit_btn.clicked.connect(self.on_edit)  # 连接到编辑联系人的处理函数
        self.edit_btn.setEnabled(False)  # 【初始禁用】，只有选中联系人后才启用
        btn_layout.addWidget(self.edit_btn)

        # 【删除按钮】：删除选中的联系人
        self.delete_btn = QPushButton("删除")
        self.delete_btn.clicked.connect(self.on_delete)  # 连接到删除联系人的处理函数
        self.delete_btn.setEnabled(False)  # 【初始禁用】，只有选中联系人后才启用
        btn_layout.addWidget(self.delete_btn)

        # 【添加弹性空间】：将后续按钮推向右侧，形成视觉分组
        btn_layout.addStretch()

        # 【导入按钮】：从文件导入联系人
        self.import_btn = QPushButton("导入")
        self.import_btn.clicked.connect(self.on_import)  # 连接到导入联系人的处理函数
        btn_layout.addWidget(self.import_btn)

        # 【导出按钮】：将联系人导出到文件
        self.export_btn = QPushButton("导出")
        self.export_btn.clicked.connect(self.on_export)  # 连接到导出联系人的处理函数
        btn_layout.addWidget(self.export_btn)

        # 【再次添加弹性空间】：将关闭按钮推向最右侧
        btn_layout.addStretch()

        # 【关闭按钮】：关闭对话框
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)  # accept() 关闭对话框
        btn_layout.addWidget(self.close_btn)

        # 【将按钮布局添加到主布局】
        layout.addLayout(btn_layout)

    def load_contacts(self, contacts: list = None):
        """
        加载联系人数据到表格中显示

        参数说明：
            contacts (list, 可选): 要显示的联系人列表
                                  如果为 None，则从数据库获取所有联系人

        功能：
            1. 设置表格行数为联系人数量
            2. 遍历每个联系人，将其信息填充到表格对应行
            3. 更新分组过滤器的选项列表

        返回值：无

        使用场景：
            - 初始化时加载所有联系人
            - 搜索后显示搜索结果
            - 添加、编辑、删除后刷新表格
        """
        # 【获取联系人数据】：如果没有传入参数，从管理器获取所有联系人
        if contacts is None:
            contacts = self.manager.get_all_contacts()

        # 【设置表格行数】：根据联系人数量动态设置
        self.table.setRowCount(len(contacts))

        # 【填充表格数据】：遍历联系人列表，逐行填充
        # enumerate() 返回索引和元素，row 是行号，contact 是联系人对象
        for row, contact in enumerate(contacts):
            # 【创建表格项】：QTableWidgetItem 是表格单元格的数据项
            # setItem(行号, 列号, 数据项)
            self.table.setItem(row, 0, QTableWidgetItem(contact.name))   # 第1列：姓名
            self.table.setItem(row, 1, QTableWidgetItem(contact.email))  # 第2列：邮箱
            self.table.setItem(row, 2, QTableWidgetItem(contact.phone))  # 第3列：电话
            self.table.setItem(row, 3, QTableWidgetItem(contact.group))  # 第4列：分组
            self.table.setItem(row, 4, QTableWidgetItem(contact.notes))  # 第5列：备注

        # 【更新分组过滤器】：根据当前数据库中的分组更新下拉框选项
        self.update_group_filter()

    def update_group_filter(self):
        """
        更新分组过滤器的选项列表

        功能：
            从数据库获取所有存在的分组，更新下拉框选项。
            如果当前选中的分组仍然存在，保持选中状态。

        技术要点：
            使用 blockSignals 暂时阻止信号触发，避免在更新选项时
            意外触发 currentTextChanged 信号，导致不必要的数据刷新。

        返回值：无
        """
        # 【阻止信号触发】：防止清空和添加选项时触发 currentTextChanged 信号
        # 这样可以避免递归调用和性能问题
        self.group_filter.blockSignals(True)

        # 【保存当前选中的分组】
        current = self.group_filter.currentText()

        # 【清空并重新添加选项】
        self.group_filter.clear()
        self.group_filter.addItem("全部分组")  # 第一个选项始终是"全部分组"

        # 【添加所有存在的分组】
        for group in self.manager.get_groups():
            self.group_filter.addItem(group)

        # 【恢复之前的选中状态】：如果之前选中的分组还存在，继续选中
        index = self.group_filter.findText(current)  # 查找文本对应的索引
        if index >= 0:  # 如果找到了
            self.group_filter.setCurrentIndex(index)  # 设置为当前选中项

        # 【恢复信号】：重新启用信号触发
        self.group_filter.blockSignals(False)

    def on_selection_changed(self):
        """
        表格选择改变事件处理函数

        功能：
            当用户点击表格选中某一行时：
            1. 根据选中行的邮箱地址获取完整的联系人对象
            2. 启用"编辑"和"删除"按钮

            当用户取消选择时：
            1. 清空选中的联系人
            2. 禁用"编辑"和"删除"按钮

        返回值：无

        设计原因：
            编辑和删除操作需要先选中联系人，通过按钮的启用/禁用状态
            可以直观地告诉用户当前是否可以进行这些操作。
        """
        selected = self.table.selectedItems()  # 【获取选中的单元格列表】

        # 【判断是否有选中项】
        if selected:
            # 【获取选中行的行号】：selected[0] 是选中的第一个单元格
            row = selected[0].row()

            # 【获取该行的邮箱】：第2列（索引1）是邮箱
            email = self.table.item(row, 1).text()

            # 【根据邮箱获取完整的联系人对象】
            # 表格只显示部分信息，完整数据需要从管理器获取
            self.selected_contact = self.manager.get_contact_by_email(email)

            # 【启用编辑和删除按钮】
            self.edit_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
        else:
            # 【没有选中项时】
            self.selected_contact = None

            # 【禁用编辑和删除按钮】
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def on_search(self, keyword: str):
        """
        搜索输入框文本改变事件处理函数（实时搜索）

        参数说明：
            keyword (str): 用户输入的搜索关键词

        功能：
            根据关键词搜索联系人并刷新表格显示。
            支持在姓名、邮箱、电话中搜索（由 ContactManager 实现）。

        返回值：无

        特点：
            【实时搜索】：每次输入改变都会立即执行搜索，无需点击按钮。
            如果输入框为空，显示所有联系人。
        """
        # 【判断是否有关键词】
        if keyword:
            # 【执行搜索】：调用管理器的搜索方法
            contacts = self.manager.search_contacts(keyword)
        else:
            # 【关键词为空】：显示所有联系人
            contacts = self.manager.get_all_contacts()

        # 【刷新表格】：用搜索结果更新表格显示
        self.load_contacts(contacts)

    def on_filter_group(self, group: str):
        """
        分组过滤下拉框选项改变事件处理函数

        参数说明：
            group (str): 选中的分组名称

        功能：
            根据选中的分组筛选联系人并刷新表格显示。
            如果选择"全部分组"，显示所有联系人。

        返回值：无
        """
        # 【判断是否选择了"全部分组"】
        if group == "全部分组":
            # 【获取所有联系人】
            contacts = self.manager.get_all_contacts()
        else:
            # 【按分组筛选】：只获取该分组下的联系人
            contacts = self.manager.get_contacts_by_group(group)

        # 【刷新表格】：用筛选结果更新表格显示
        self.load_contacts(contacts)

    def on_add(self):
        """
        "添加"按钮点击事件处理函数

        功能流程：
            1. 打开空白的 ContactEditDialog 对话框
            2. 如果用户点击"保存"（返回 Accepted 状态）：
               a. 获取用户输入的联系人信息
               b. 调用管理器添加到数据库
               c. 刷新表格显示
               d. 显示成功或失败提示

        返回值：无

        注意：
            如果邮箱已存在，管理器会返回 False，此时显示警告。
        """
        # 【创建编辑对话框】：不传 contact 参数，表示添加新联系人
        dialog = ContactEditDialog(self)

        # 【显示对话框并等待用户操作】
        # exec_() 是【模态对话框】，会阻塞当前窗口直到对话框关闭
        # 返回 QDialog.Accepted 表示用户点击了"保存"
        if dialog.exec_() == QDialog.Accepted:
            # 【获取用户创建的联系人对象】
            contact = dialog.get_contact()

            # 【添加到数据库】：如果成功返回 True，失败返回 False（邮箱重复）
            if self.manager.add_contact(contact):
                # 【刷新表格】：重新加载所有联系人
                self.load_contacts()
                # 【显示成功提示】
                QMessageBox.information(self, "成功", "联系人添加成功")
            else:
                # 【显示失败提示】：邮箱已存在
                QMessageBox.warning(self, "失败", "该邮箱已存在")

    def on_edit(self):
        """
        "编辑"按钮点击事件处理函数（双击表格行也会触发）

        功能流程：
            1. 检查是否选中了联系人
            2. 打开填充了现有数据的 ContactEditDialog 对话框
            3. 如果用户点击"保存"：
               a. 获取用户修改后的联系人信息
               b. 调用管理器更新数据库（可能修改了邮箱）
               c. 刷新表格显示
               d. 显示成功提示

        返回值：无

        技术要点：
            保存旧邮箱地址是因为邮箱可能被修改，而数据库是用邮箱作为主键查找联系人的。
        """
        # 【检查是否选中联系人】：如果没选中，直接返回
        if not self.selected_contact:
            return

        # 【保存旧邮箱】：因为邮箱可能会被修改，需要用旧邮箱定位数据库记录
        old_email = self.selected_contact.email

        # 【创建编辑对话框】：传入 contact 参数，自动填充现有数据
        dialog = ContactEditDialog(self, self.selected_contact)

        # 【显示对话框并等待用户操作】
        if dialog.exec_() == QDialog.Accepted:
            # 【获取用户修改后的联系人对象】
            new_contact = dialog.get_contact()

            # 【更新数据库】：用旧邮箱定位记录，用新对象更新所有字段
            if self.manager.update_contact(old_email, new_contact):
                # 【刷新表格】
                self.load_contacts()
                # 【显示成功提示】
                QMessageBox.information(self, "成功", "联系人更新成功")

    def on_delete(self):
        """
        "删除"按钮点击事件处理函数

        功能流程：
            1. 检查是否选中了联系人
            2. 弹出确认对话框，避免误删
            3. 如果用户确认删除：
               a. 调用管理器从数据库删除
               b. 刷新表格显示
               c. 清空选中状态

        返回值：无

        用户体验：
            删除是不可逆操作，因此使用 QMessageBox.question 让用户确认。
        """
        # 【检查是否选中联系人】
        if not self.selected_contact:
            return

        # 【弹出确认对话框】
        # QMessageBox.question 返回用户点击的按钮
        reply = QMessageBox.question(
            self,  # 父窗口
            "确认删除",  # 对话框标题
            f"确定要删除联系人 '{self.selected_contact.name}' 吗？",  # 提示信息（使用 f-string 插入姓名）
            QMessageBox.Yes | QMessageBox.No  # 【按钮组合】：显示"是"和"否"两个按钮
        )

        # 【判断用户的选择】
        if reply == QMessageBox.Yes:
            # 【从数据库删除】：用邮箱作为标识
            if self.manager.delete_contact(self.selected_contact.email):
                # 【刷新表格】
                self.load_contacts()
                # 【清空选中状态】：已删除的联系人不应该继续保持选中
                self.selected_contact = None

    def on_import(self):
        """导入联系人"""
        file_path, file_type = QFileDialog.getOpenFileName(
            self, "选择导入文件", "",
            "CSV文件 (*.csv);;JSON文件 (*.json);;所有文件 (*.*)"
        )

        if not file_path:
            return

        if file_path.endswith('.csv'):
            count = self.manager.import_from_csv(file_path)
        elif file_path.endswith('.json'):
            count = self.manager.import_from_json(file_path)
        else:
            QMessageBox.warning(self, "错误", "不支持的文件格式")
            return

        self.load_contacts()
        QMessageBox.information(self, "导入完成", f"成功导入 {count} 个联系人")

    def on_export(self):
        """导出联系人"""
        file_path, file_type = QFileDialog.getSaveFileName(
            self, "保存文件", "contacts",
            "CSV文件 (*.csv);;JSON文件 (*.json)"
        )

        if not file_path:
            return

        if "csv" in file_type.lower():
            if not file_path.endswith('.csv'):
                file_path += '.csv'
            success = self.manager.export_to_csv(file_path)
        else:
            if not file_path.endswith('.json'):
                file_path += '.json'
            success = self.manager.export_to_json(file_path)

        if success:
            QMessageBox.information(self, "导出成功", f"联系人已导出到:\n{file_path}")
        else:
            QMessageBox.warning(self, "导出失败", "导出联系人时发生错误")

    def get_contact_manager(self) -> ContactManager:
        """获取联系人管理器"""
        return self.manager


class ContactSelectDialog(QDialog):
    """联系人选择对话框 - 用于写邮件时选择收件人"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = ContactManager()
        self.selected_contact = None
        self.init_ui()
        self.load_contacts()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("选择联系人")
        # 【UI优化】调整最小尺寸
        self.setMinimumSize(520, 420)

        layout = QVBoxLayout(self)
        # 【UI优化】使用设计系统的间距
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # 搜索栏
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入姓名或邮箱搜索...")
        self.search_edit.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)

        # 联系人表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["姓名", "邮箱", "分组"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.doubleClicked.connect(self.on_add_contact)
        layout.addWidget(self.table)

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.add_btn = QPushButton("添加到收件人")
        self.add_btn.clicked.connect(self.on_add_contact)
        self.add_btn.setEnabled(False)
        btn_layout.addWidget(self.add_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    def load_contacts(self, contacts: list = None):
        """加载联系人到表格"""
        if contacts is None:
            contacts = self.manager.get_all_contacts()

        self.table.setRowCount(len(contacts))

        for row, contact in enumerate(contacts):
            self.table.setItem(row, 0, QTableWidgetItem(contact.name))
            self.table.setItem(row, 1, QTableWidgetItem(contact.email))
            self.table.setItem(row, 2, QTableWidgetItem(contact.group))

    def on_search(self, keyword: str):
        """搜索联系人"""
        if keyword:
            contacts = self.manager.search_contacts(keyword)
        else:
            contacts = self.manager.get_all_contacts()
        self.load_contacts(contacts)

    def on_selection_changed(self):
        """选择改变"""
        selected = self.table.selectedItems()
        self.add_btn.setEnabled(len(selected) > 0)

    def on_add_contact(self):
        """添加联系人"""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            name = self.table.item(row, 0).text()
            email = self.table.item(row, 1).text()
            self.selected_contact = f"{name} <{email}>"
            self.accept()

    def get_selected_contact(self) -> str:
        """获取选中的联系人"""
        return self.selected_contact
