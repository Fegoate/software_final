"""
邮件夹管理对话框模块

本模块提供了一个【图形界面对话框】，用于管理邮箱中的邮件夹。
主要功能包括：
1. 显示所有邮件夹列表（收件箱、已发送、草稿箱等）
2. 创建新的邮件夹
3. 重命名自定义邮件夹
4. 删除自定义邮件夹
5. 保护系统文件夹（如收件箱）不被删除或重命名

技术要点：
- 使用 PyQt5 构建图形界面
- 实现了中英文名称映射（如 INBOX -> 收件箱）
- 对系统文件夹提供保护机制
"""

# sys: Python 系统相关的【标准库】，用于访问系统功能（如路径操作）
import sys
# os: 操作系统接口【标准库】，用于文件路径、目录操作
import os
# 将项目根目录添加到 Python 模块搜索路径中，使得可以导入项目中的其他模块
# os.path.abspath(__file__): 获取当前文件的【绝对路径】
# os.path.dirname(): 获取路径的【父目录】
# sys.path.insert(0, ...): 将路径插入到搜索路径的【最前面】，优先级最高
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# PyQt5.QtWidgets: PyQt5 的【窗口部件模块】，包含所有图形界面组件
from PyQt5.QtWidgets import (
    QDialog,          # 对话框基类，用于创建【模态或非模态对话框】
    QVBoxLayout,      # 垂直布局管理器，将控件【从上到下】排列
    QHBoxLayout,      # 水平布局管理器，将控件【从左到右】排列
    QLabel,           # 标签控件，用于显示【静态文本】
    QLineEdit,        # 单行文本编辑框，用于【输入文本】
    QPushButton,      # 按钮控件，用于【触发操作】
    QListWidget,      # 列表控件，用于显示【可选择的列表项】
    QListWidgetItem,  # 列表项，代表列表中的【单个条目】
    QMessageBox,      # 消息框，用于显示【提示、警告、错误】信息
    QInputDialog      # 输入对话框，用于【获取用户输入】
)
# PyQt5.QtCore: PyQt5 的【核心模块】，包含核心非 GUI 功能
from PyQt5.QtCore import Qt  # Qt 命名空间，包含各种【枚举常量和标志】


class FolderManagerDialog(QDialog):
    """
    邮件夹管理对话框类

    这个类继承自 QDialog（【对话框】基类），提供了一个完整的邮件夹管理界面。

    主要功能：
    1. 【显示邮件夹列表】：从邮箱服务器获取所有文件夹并显示
    2. 【新建文件夹】：创建新的自定义邮件夹
    3. 【重命名文件夹】：重命名用户创建的文件夹（系统文件夹不可重命名）
    4. 【删除文件夹】：删除用户创建的文件夹（系统文件夹受保护）
    5. 【中英文映射】：将英文文件夹名显示为中文（如 INBOX -> 收件箱）

    使用示例：
        receiver = EmailReceiver()  # 邮件接收器对象
        dialog = FolderManagerDialog(parent=main_window, receiver=receiver)
        dialog.exec_()  # 显示对话框

    重要属性：
        receiver: 邮件接收器对象，用于执行实际的文件夹操作
        folders: 存储原始的英文文件夹名列表
        folder_display_map: 显示名称到原始名称的映射字典
    """

    # 【类常量】：文件夹名称中英文映射字典
    # 这个字典定义了邮箱系统文件夹的英文名到中文名的对应关系
    # 键（Key）：邮箱服务器返回的【英文文件夹名】
    # 值（Value）：界面上显示的【中文文件夹名】
    FOLDER_NAME_MAP = {
        "INBOX": "收件箱",              # 收件箱，邮箱的主文件夹
        "Sent Messages": "已发送",      # 已发送的邮件
        "Deleted Messages": "已删除",   # 已删除的邮件
        "Drafts": "草稿箱",             # 草稿邮件
        "Junk": "垃圾邮件",             # 垃圾邮件（某些邮箱服务商使用）
        "Spam": "垃圾邮件",             # 垃圾邮件（另一种命名）
        "Trash": "已删除",              # 回收站（另一种命名）
        "Sent": "已发送",               # 已发送（简化命名）
    }

    def __init__(self, parent=None, receiver=None):
        """
        【构造函数】：初始化邮件夹管理对话框

        参数说明：
            parent (QWidget, 可选): 【父窗口】对象，默认为 None
                - 如果指定了父窗口，对话框会显示在父窗口中央
                - 当父窗口关闭时，这个对话框也会自动关闭
            receiver (EmailReceiver, 可选): 【邮件接收器】对象，默认为 None
                - 用于执行实际的文件夹操作（创建、删除、重命名、获取列表）
                - 如果为 None，则只能显示默认的收件箱

        执行流程：
            1. 调用父类 QDialog 的构造函数
            2. 保存邮件接收器对象的引用
            3. 初始化实例变量（文件夹列表、映射字典）
            4. 创建图形界面（调用 init_ui）
            5. 从服务器加载文件夹列表（调用 load_folders）
        """
        # 调用父类（QDialog）的【构造函数】，传入父窗口参数
        # super() 用于获取父类的引用，确保正确的【继承链】初始化
        super().__init__(parent)

        # 保存邮件接收器对象的引用，后续所有文件夹操作都通过它来执行
        self.receiver = receiver

        # 初始化【实例变量】：存储从服务器获取的原始文件夹名列表（英文）
        self.folders = []

        # 初始化【映射字典】：建立 "显示名称（中文）-> 原始名称（英文）" 的对应关系
        # 例如：{"收件箱": "INBOX", "已发送": "Sent Messages"}
        # 这样当用户点击"收件箱"时，可以找到对应的英文名 "INBOX" 来操作
        self.folder_display_map = {}

        # 调用界面初始化方法，创建所有的【图形控件】（按钮、列表等）
        self.init_ui()

        # 从邮箱服务器【加载文件夹列表】，并显示在界面上
        self.load_folders()

    def get_display_name(self, folder: str) -> str:
        """
        获取文件夹的中文显示名称

        功能说明：
            将邮箱服务器返回的【英文文件夹名】转换为【中文显示名】。
            如果文件夹名在映射字典中存在，返回对应的中文名；
            否则返回原始的英文名（用于用户自定义文件夹）。

        参数：
            folder (str): 原始的英文文件夹名（如 "INBOX", "Sent Messages"）

        返回值：
            str: 中文显示名称（如 "收件箱", "已发送"）或原始名称

        示例：
            >>> get_display_name("INBOX")
            "收件箱"
            >>> get_display_name("MyCustomFolder")
            "MyCustomFolder"  # 自定义文件夹，无映射，返回原名
        """
        # 使用字典的 get 方法查找映射
        # get(key, default): 如果 key 存在，返回对应的值；否则返回 default（默认值）
        return self.FOLDER_NAME_MAP.get(folder, folder)

    def get_real_name(self, display_name: str) -> str:
        """
        从显示名称获取原始的英文文件夹名

        功能说明：
            这是 get_display_name 的【逆向操作】。
            将界面上显示的【中文名称】转换回【英文原始名称】，
            以便向邮箱服务器发送正确的文件夹名进行操作。

        参数：
            display_name (str): 界面显示的文件夹名（如 "收件箱", "已发送"）

        返回值：
            str: 原始的英文文件夹名（如 "INBOX", "Sent Messages"）

        示例：
            >>> get_real_name("收件箱")
            "INBOX"
            >>> get_real_name("MyCustomFolder")
            "MyCustomFolder"  # 自定义文件夹，直接返回
        """
        # 从【显示名 -> 原始名】映射字典中查找
        # 如果找不到，说明是用户自定义文件夹，显示名就是原始名
        return self.folder_display_map.get(display_name, display_name)

    def init_ui(self):
        """
        初始化用户界面

        功能说明：
            创建并布局对话框中的所有【图形控件】，包括：
            - 标题标签
            - 文件夹列表控件
            - 操作按钮（新建、重命名、删除）
            - 关闭按钮

        界面布局结构：
            ┌─────────────────────────┐
            │   邮件夹列表:            │  <- 标题标签
            │  ┌────────────────────┐ │
            │  │ 收件箱              │ │
            │  │ 已发送              │ │  <- 文件夹列表
            │  │ 草稿箱              │ │
            │  └────────────────────┘ │
            │  [新建] [重命名] [删除]  │  <- 操作按钮
            │                  [关闭]  │  <- 关闭按钮
            └─────────────────────────┘

        无参数、无返回值
        """
        # 设置对话框的【窗口标题】
        self.setWindowTitle("邮件夹管理")

        # 【UI优化】调整最小尺寸
        self.setMinimumSize(420, 380)

        # 创建【垂直布局管理器】
        layout = QVBoxLayout(self)
        # 【UI优化】使用设计系统的间距
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ===== 1. 添加标题标签 =====
        # 创建并添加一个显示"邮件夹列表:"的标签控件
        layout.addWidget(QLabel("邮件夹列表:"))

        # ===== 2. 创建文件夹列表控件 =====
        # QListWidget: 【列表控件】，用于显示可选择的文件夹列表
        self.folder_list = QListWidget()

        # 连接【信号与槽】：当列表选择项改变时，自动调用 on_selection_changed 方法
        # itemSelectionChanged: 【信号】，当用户选择不同的列表项时发出
        # connect(): 连接信号到【槽函数】（响应函数）
        self.folder_list.itemSelectionChanged.connect(self.on_selection_changed)

        # 将列表控件添加到垂直布局中
        layout.addWidget(self.folder_list)

        # ===== 3. 创建操作按钮区域 =====
        # 创建【水平布局】，用于放置三个操作按钮（横向排列）
        btn_layout = QHBoxLayout()

        # --- 3.1 新建文件夹按钮 ---
        self.add_btn = QPushButton("新建文件夹")
        # 连接按钮的【点击信号】到 on_add 方法
        # clicked: 当按钮被点击时发出的【信号】
        self.add_btn.clicked.connect(self.on_add)
        btn_layout.addWidget(self.add_btn)

        # --- 3.2 重命名按钮 ---
        self.rename_btn = QPushButton("重命名")
        # 连接点击信号到 on_rename 方法
        self.rename_btn.clicked.connect(self.on_rename)
        # 设置为【禁用状态】（灰色，不可点击）
        # 只有选择了文件夹后，才会在 on_selection_changed 中启用
        self.rename_btn.setEnabled(False)
        btn_layout.addWidget(self.rename_btn)

        # --- 3.3 删除按钮 ---
        self.delete_btn = QPushButton("删除")
        # 连接点击信号到 on_delete 方法
        self.delete_btn.clicked.connect(self.on_delete)
        # 初始状态为禁用，防止误操作
        self.delete_btn.setEnabled(False)
        btn_layout.addWidget(self.delete_btn)

        # 将按钮的水平布局添加到主垂直布局中
        layout.addLayout(btn_layout)

        # ===== 4. 创建关闭按钮区域 =====
        # 创建另一个水平布局，用于放置关闭按钮
        close_layout = QHBoxLayout()

        # addStretch(): 添加【弹性空白】，将后面的控件推到右侧
        # 效果：关闭按钮会显示在窗口的右下角
        close_layout.addStretch()

        # 创建关闭按钮
        self.close_btn = QPushButton("关闭")
        # accept(): QDialog 的【槽函数】，关闭对话框并返回 Accepted 状态
        self.close_btn.clicked.connect(self.accept)
        close_layout.addWidget(self.close_btn)

        # 将关闭按钮布局添加到主垂直布局中
        layout.addLayout(close_layout)

    def load_folders(self):
        """
        从邮箱服务器加载文件夹列表并显示

        功能说明：
            1. 清空当前列表中的所有项
            2. 通过邮件接收器从服务器获取文件夹列表
            3. 将英文文件夹名转换为中文显示名
            4. 创建列表项并添加到界面
            5. 对收件箱等系统文件夹设置保护标志

        执行流程：
            1. 清空现有列表和映射字典
            2. 调用 receiver.get_folders() 获取文件夹列表
            3. 遍历每个文件夹，创建显示项
            4. 建立显示名到原始名的映射关系

        无参数、无返回值
        """
        # 清空列表控件中的【所有现有项】，准备重新加载
        self.folder_list.clear()

        # 清空【映射字典】，重新建立映射关系
        self.folder_display_map = {}

        # 判断是否有邮件接收器对象（是否已连接到邮箱服务器）
        if self.receiver:
            # 调用邮件接收器的 get_folders() 方法，从服务器【获取文件夹列表】
            # 返回值是一个包含所有文件夹名的列表，如 ["INBOX", "Sent Messages", ...]
            self.folders = self.receiver.get_folders()
        else:
            # 如果没有接收器（未连接），只显示默认的收件箱
            self.folders = ["INBOX"]

        # 【遍历】所有文件夹，为每个文件夹创建列表项
        for folder in self.folders:
            # 获取文件夹的【中文显示名】（如 "INBOX" -> "收件箱"）
            display_name = self.get_display_name(folder)

            # 在映射字典中建立 "显示名 -> 原始名" 的对应关系
            # 这样当用户点击"收件箱"时，可以找到原始名 "INBOX" 进行操作
            self.folder_display_map[display_name] = folder

            # 创建【列表项对象】，显示中文名称
            item = QListWidgetItem(display_name)

            # 【保护系统文件夹】：收件箱不能删除或重命名
            # upper(): 转换为大写，确保大小写不敏感的比较
            if folder.upper() == "INBOX":
                # 使用【位运算】移除列表项的"可编辑"标志
                # item.flags(): 获取当前项的所有标志（一个整数，每个位代表一个特性）
                # ~Qt.ItemIsEditable: 对"可编辑"标志进行【按位取反】
                # &: 【按位与】运算，移除可编辑标志
                # 效果：收件箱项变为只读，不可编辑
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)

            # 将列表项添加到【列表控件】中显示
            self.folder_list.addItem(item)

    def on_selection_changed(self):
        """
        【槽函数】：响应列表选择变化事件

        功能说明：
            当用户在列表中选择或取消选择文件夹时，这个方法会被自动调用。
            主要作用是根据选择的文件夹类型，动态启用或禁用"重命名"和"删除"按钮。

        业务逻辑：
            1. 如果选中了文件夹：
               - 判断是否为系统文件夹（收件箱、已发送等）
               - 系统文件夹：禁用重命名和删除按钮（保护系统文件夹）
               - 自定义文件夹：启用重命名和删除按钮
            2. 如果未选中任何文件夹：
               - 禁用重命名和删除按钮（没有操作对象）

        无参数、无返回值
        """
        # 获取【当前选中的列表项】
        # selectedItems() 返回一个列表，包含所有选中的项（通常只有一个）
        selected = self.folder_list.selectedItems()

        # 判断是否有选中的项
        if selected:
            # 获取选中项显示的【文本内容】（中文名称，如"收件箱"）
            # selected[0]: 取第一个（通常也是唯一的）选中项
            display_name = selected[0].text()

            # 通过显示名获取【原始英文文件夹名】（如"INBOX"）
            real_name = self.get_real_name(display_name)

            # 【判断是否为系统文件夹】（不允许修改的文件夹）
            # 两种情况被视为系统文件夹：
            # 1. 收件箱（INBOX）
            # 2. 在映射字典中定义的文件夹（Sent Messages, Drafts 等）
            # in self.FOLDER_NAME_MAP: 检查原始名是否在系统文件夹字典的【键】中
            is_system = real_name.upper() == "INBOX" or real_name in self.FOLDER_NAME_MAP

            # 根据是否为系统文件夹，设置按钮的【启用状态】
            # not is_system: 如果不是系统文件夹，则启用按钮（True）
            # setEnabled(True): 启用按钮（可点击）
            # setEnabled(False): 禁用按钮（灰色，不可点击）
            self.rename_btn.setEnabled(not is_system)  # 系统文件夹不能重命名
            self.delete_btn.setEnabled(not is_system)  # 系统文件夹不能删除
        else:
            # 如果没有选中任何项，【禁用】重命名和删除按钮
            # 防止用户在未选择文件夹时误点击操作按钮
            self.rename_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

    def on_add(self):
        """
        【槽函数】：处理新建文件夹操作

        功能说明：
            当用户点击"新建文件夹"按钮时，这个方法会被调用。
            它会显示一个输入对话框，让用户输入新文件夹的名称，
            然后进行验证并在邮箱服务器上创建该文件夹。

        执行流程：
            1. 弹出输入对话框，获取用户输入的文件夹名
            2. 验证输入（不能为空、不能重复）
            3. 调用邮件接收器创建文件夹
            4. 刷新文件夹列表
            5. 显示操作结果

        无参数、无返回值
        """
        # 显示【输入对话框】，让用户输入新文件夹的名称
        # QInputDialog.getText() 返回两个值：
        # - name: 用户输入的文本内容
        # - ok: 布尔值，表示用户是点击了"确定"(True)还是"取消"(False)
        # 参数说明：
        #   self: 对话框的父窗口（当前对话框）
        #   "新建文件夹": 对话框的标题
        #   "请输入文件夹名称:": 提示文本
        name, ok = QInputDialog.getText(
            self, "新建文件夹", "请输入文件夹名称:"
        )

        # 判断用户是否点击了"确定"按钮，并且输入了内容
        # ok: 用户点击了确定（而不是取消）
        # name: 输入的内容不为空字符串
        if ok and name:
            # 【去除首尾空格】：清理用户输入
            # strip() 方法会移除字符串开头和结尾的空白字符（空格、制表符等）
            name = name.strip()

            # 再次检查：去除空格后，如果字符串变成空的，说明用户只输入了空格
            if not name:
                # 显示【警告消息框】
                # QMessageBox.warning(父窗口, 标题, 消息内容)
                QMessageBox.warning(self, "错误", "文件夹名称不能为空")
                return  # 中断函数执行，返回到对话框

            # 检查【文件夹名是否已存在】
            # in self.folders: 检查名称是否在现有文件夹列表中
            if name in self.folders:
                QMessageBox.warning(self, "错误", "该文件夹已存在")
                return  # 文件夹已存在，不能重复创建

            # 判断是否有邮件接收器（是否已连接到邮箱服务器）
            if self.receiver:
                # 调用邮件接收器的【创建文件夹】方法
                # create_folder() 返回两个值：
                # - success: 布尔值，表示操作是否成功
                # - msg: 字符串，包含成功或失败的详细消息
                success, msg = self.receiver.create_folder(name)

                # 根据操作结果，显示不同的消息
                if success:
                    # 操作成功：重新加载文件夹列表，显示新创建的文件夹
                    self.load_folders()
                    # 显示【信息消息框】（成功提示）
                    QMessageBox.information(self, "成功", msg)
                else:
                    # 操作失败：显示错误信息
                    QMessageBox.warning(self, "失败", msg)
            else:
                # 没有邮件接收器，无法执行操作
                QMessageBox.warning(self, "错误", "未连接到邮箱服务器")

    def on_rename(self):
        """
        【槽函数】：处理重命名文件夹操作

        功能说明：
            当用户点击"重命名"按钮时，这个方法会被调用。
            它会显示一个输入对话框，让用户输入新的文件夹名称，
            然后进行验证并在邮箱服务器上重命名该文件夹。

        执行流程：
            1. 获取当前选中的文件夹
            2. 检查是否为系统文件夹（系统文件夹不可重命名）
            3. 弹出输入对话框，获取新名称
            4. 验证新名称（不能为空、不能与现有文件夹重复）
            5. 调用邮件接收器执行重命名
            6. 刷新文件夹列表

        无参数、无返回值
        """
        # 获取【当前选中的列表项】
        selected = self.folder_list.selectedItems()

        # 如果没有选中任何项，直接返回（理论上不应该发生，因为按钮应该是禁用的）
        if not selected:
            return

        # 获取选中项的【显示名称】（中文）
        display_name = selected[0].text()

        # 通过显示名获取【原始英文名称】
        real_name = self.get_real_name(display_name)

        # 【安全检查】：再次确认不是系统文件夹
        # 虽然在 on_selection_changed 中已经禁用了按钮，但这里再检查一次更安全
        if real_name.upper() == "INBOX" or real_name in self.FOLDER_NAME_MAP:
            QMessageBox.warning(self, "错误", "不能重命名系统文件夹")
            return

        # 显示【输入对话框】，让用户输入新的文件夹名称
        # 参数 text=real_name: 将当前文件夹名作为【默认值】显示在输入框中
        # 这样用户可以基于现有名称进行修改，而不是从头输入
        new_name, ok = QInputDialog.getText(
            self, "重命名文件夹",
            "请输入新名称:",
            text=real_name  # 默认显示原始名称
        )

        # 判断用户是否点击了"确定"并输入了内容
        if ok and new_name:
            # 【去除首尾空格】
            new_name = new_name.strip()

            # 检查新名称是否为空
            if not new_name:
                QMessageBox.warning(self, "错误", "文件夹名称不能为空")
                return

            # 检查新名称是否与原名称相同（没有实际修改）
            # 如果相同，直接返回，不需要执行重命名操作
            if new_name == real_name:
                return

            # 检查【新名称是否与其他文件夹重复】
            if new_name in self.folders:
                QMessageBox.warning(self, "错误", "该文件夹已存在")
                return

            # 判断是否有邮件接收器
            if self.receiver:
                # 调用邮件接收器的【重命名文件夹】方法
                # rename_folder(旧名称, 新名称)
                success, msg = self.receiver.rename_folder(real_name, new_name)

                # 根据操作结果显示消息
                if success:
                    # 重命名成功：重新加载文件夹列表，显示新名称
                    self.load_folders()
                    QMessageBox.information(self, "成功", msg)
                else:
                    # 重命名失败：显示错误信息
                    QMessageBox.warning(self, "失败", msg)

    def on_delete(self):
        """
        【槽函数】：处理删除文件夹操作

        功能说明：
            当用户点击"删除"按钮时，这个方法会被调用。
            它会显示一个确认对话框，确认用户真的要删除该文件夹，
            然后在邮箱服务器上删除该文件夹及其中的所有邮件。

        执行流程：
            1. 获取当前选中的文件夹
            2. 检查是否为系统文件夹（系统文件夹不可删除）
            3. 弹出确认对话框，警告用户文件夹中的邮件也会被删除
            4. 如果用户确认，调用邮件接收器执行删除
            5. 刷新文件夹列表

        注意事项：
            删除操作是【不可逆】的，文件夹中的所有邮件都会被永久删除！

        无参数、无返回值
        """
        # 获取【当前选中的列表项】
        selected = self.folder_list.selectedItems()

        # 如果没有选中任何项，直接返回
        if not selected:
            return

        # 获取选中项的【显示名称】（中文）
        display_name = selected[0].text()

        # 通过显示名获取【原始英文名称】
        real_name = self.get_real_name(display_name)

        # 【安全检查】：再次确认不是系统文件夹
        # 系统文件夹（如收件箱、已发送等）不允许删除，以保护用户数据
        if real_name.upper() == "INBOX" or real_name in self.FOLDER_NAME_MAP:
            QMessageBox.warning(self, "错误", "不能删除系统文件夹")
            return

        # 显示【确认对话框】，让用户再次确认删除操作
        # QMessageBox.question() 返回用户点击的按钮（Yes 或 No）
        # 使用 f-string 格式化字符串，将文件夹名插入到提示信息中
        # \n\n: 插入两个换行符，使警告信息更醒目
        # QMessageBox.Yes | QMessageBox.No: 使用【位或运算】组合两个按钮
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除文件夹 '{display_name}' 吗？\n\n注意：文件夹中的邮件也会被删除！",
            QMessageBox.Yes | QMessageBox.No  # 显示"是"和"否"两个按钮
        )

        # 判断用户是否点击了"是"按钮
        # 只有用户明确确认，才执行删除操作（防止误操作）
        if reply == QMessageBox.Yes:
            # 判断是否有邮件接收器
            if self.receiver:
                # 调用邮件接收器的【删除文件夹】方法
                # delete_folder(文件夹名) 会删除该文件夹及其中的所有邮件
                success, msg = self.receiver.delete_folder(real_name)

                # 根据操作结果显示消息
                if success:
                    # 删除成功：重新加载文件夹列表，移除已删除的文件夹
                    self.load_folders()
                    QMessageBox.information(self, "成功", msg)
                else:
                    # 删除失败：显示错误信息
                    QMessageBox.warning(self, "失败", msg)

    def get_folders(self) -> list:
        """
        获取文件夹列表

        功能说明：
            返回当前从邮箱服务器获取的所有文件夹名称列表（原始英文名）。
            这个方法通常用于其他组件需要获取文件夹列表时调用。

        参数：
            无

        返回值：
            list: 包含所有文件夹【原始名称】的列表
                 例如：["INBOX", "Sent Messages", "Drafts", "MyFolder"]

        使用示例：
            >>> dialog = FolderManagerDialog(receiver=receiver)
            >>> folders = dialog.get_folders()
            >>> print(folders)
            ["INBOX", "Sent Messages", "Drafts"]
        """
        # 返回【实例变量】self.folders
        # 这个列表在 load_folders() 方法中从邮箱服务器获取并更新
        return self.folders
