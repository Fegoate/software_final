"""
================================================================================
通信簿管理模块 - 负责联系人的增删改查和导入导出
================================================================================

【文件作用】
这个文件负责管理通信簿（联系人列表），主要功能：
1. 添加、修改、删除联系人
2. 搜索联系人
3. 按分组管理联系人
4. 导入/导出联系人（支持 CSV 和 JSON 格式）

【数据存储】
联系人数据保存在用户目录下的文件中：
- Windows: C:\\Users\\用户名\\.email_client\\contacts.json
- Mac/Linux: /Users/用户名/.email_client/contacts.json

【什么是 CSV】
CSV（Comma-Separated Values，逗号分隔值）是一种简单的文本文件格式，
可以用 Excel 打开和编辑。每行是一条记录，字段用逗号分隔。

【什么是 JSON】
JSON（JavaScript Object Notation）是一种轻量级的数据交换格式，
易于人类阅读和机器解析。
================================================================================
"""

# ============================================================================
# 导入必要的模块
# ============================================================================

# json 模块：用于读写 JSON 文件
import json

# csv 模块：用于读写 CSV 文件
import csv

# os 模块：用于文件和目录操作
import os

# 类型提示
from typing import List, Optional

# Path：现代化的路径处理类
from pathlib import Path

# 导入路径设置模块
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入联系人数据类
from models.email_model import Contact


# ============================================================================
# 通信簿管理器类
# ============================================================================
class ContactManager:
    """
    通信簿管理器类 - 负责联系人的管理和持久化存储

    【主要功能】
    1. 增删改查联系人
    2. 分组管理
    3. 搜索联系人
    4. 导入导出（CSV/JSON）

    【使用示例】
    manager = ContactManager()

    # 添加联系人
    contact = Contact(name="张三", email="zhangsan@qq.com")
    manager.add_contact(contact)

    # 搜索联系人
    results = manager.search_contacts("张")

    # 导出到 CSV
    manager.export_to_csv("contacts.csv")
    """

    def __init__(self):
        """
        初始化通信簿管理器

        【初始化过程】
        1. 创建空的联系人列表
        2. 设置配置文件路径
        3. 确保配置目录存在
        4. 加载已保存的联系人
        """
        # 联系人列表
        self.contacts: List[Contact] = []

        # 配置目录：用户主目录下的 .email_client 文件夹
        self.config_dir = Path.home() / ".email_client"

        # 联系人数据文件路径
        self.contacts_file = self.config_dir / "contacts.json"

        # 确保配置目录存在
        self._ensure_config_dir()

        # 从文件加载联系人
        self.load_contacts()

    def _ensure_config_dir(self):
        """
        确保配置目录存在

        【私有方法说明】
        方法名以下划线开头表示这是私有方法，只在类内部使用。
        """
        if not self.config_dir.exists():
            # 创建目录，parents=True 表示同时创建父目录
            self.config_dir.mkdir(parents=True)

    def load_contacts(self) -> bool:
        """
        从文件加载联系人数据

        【返回值】
        - True：加载成功
        - False：加载失败或文件不存在
        """
        # 检查文件是否存在
        if not self.contacts_file.exists():
            return False

        try:
            # 打开并读取 JSON 文件
            with open(self.contacts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 将字典列表转换为 Contact 对象列表
                # Contact.from_dict() 是我们在 Contact 类中定义的类方法
                self.contacts = [Contact.from_dict(c) for c in data]
            return True
        except Exception as e:
            print(f"加载联系人失败: {e}")
            return False

    def save_contacts(self) -> bool:
        """
        保存联系人数据到文件

        【返回值】
        - True：保存成功
        - False：保存失败
        """
        try:
            # 将 Contact 对象列表转换为字典列表
            data = [c.to_dict() for c in self.contacts]

            # 写入 JSON 文件
            with open(self.contacts_file, 'w', encoding='utf-8') as f:
                # indent=2：缩进2个空格，让文件更易读
                # ensure_ascii=False：允许中文直接写入，不转义
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存联系人失败: {e}")
            return False

    def add_contact(self, contact: Contact) -> bool:
        """
        添加新联系人

        【参数】
        contact：要添加的联系人对象

        【返回值】
        - True：添加成功
        - False：添加失败（邮箱已存在）

        【注意】
        不允许添加重复的邮箱地址
        """
        # 检查邮箱是否已存在
        if self.get_contact_by_email(contact.email):
            return False

        # 添加到列表
        self.contacts.append(contact)

        # 保存到文件
        self.save_contacts()
        return True

    def update_contact(self, old_email: str, new_contact: Contact) -> bool:
        """
        更新联系人信息

        【参数】
        - old_email：要更新的联系人的原邮箱地址
        - new_contact：新的联系人信息

        【返回值】
        - True：更新成功
        - False：未找到该联系人
        """
        # 遍历查找要更新的联系人
        for i, c in enumerate(self.contacts):
            if c.email == old_email:
                # 替换为新的联系人信息
                self.contacts[i] = new_contact
                # 保存更改
                self.save_contacts()
                return True
        return False

    def delete_contact(self, email: str) -> bool:
        """
        删除联系人

        【参数】
        email：要删除的联系人的邮箱地址

        【返回值】
        - True：删除成功
        - False：未找到该联系人
        """
        for i, c in enumerate(self.contacts):
            if c.email == email:
                # 从列表中移除
                self.contacts.pop(i)
                # 保存更改
                self.save_contacts()
                return True
        return False

    def get_contact_by_email(self, email: str) -> Optional[Contact]:
        """
        根据邮箱地址获取联系人

        【参数】
        email：邮箱地址

        【返回值】
        - 如果找到，返回联系人对象
        - 如果未找到，返回 None
        """
        for c in self.contacts:
            if c.email == email:
                return c
        return None

    def get_all_contacts(self) -> List[Contact]:
        """
        获取所有联系人

        【返回值】
        联系人列表的副本

        【为什么返回副本】
        .copy() 返回列表的浅拷贝，防止外部直接修改内部列表。
        这是一种保护性编程的做法。
        """
        return self.contacts.copy()

    def get_contacts_by_group(self, group: str) -> List[Contact]:
        """
        根据分组获取联系人

        【参数】
        group：分组名称

        【返回值】
        该分组下的所有联系人
        """
        return [c for c in self.contacts if c.group == group]

    def get_groups(self) -> List[str]:
        """
        获取所有分组名称

        【返回值】
        分组名称列表（已排序，去重）

        【使用 set 去重】
        set 是集合类型，自动去除重复元素
        """
        groups = set()  # 创建空集合
        for c in self.contacts:
            groups.add(c.group)  # 添加分组名称
        # 转换为列表并排序后返回
        return sorted(list(groups))

    def search_contacts(self, keyword: str) -> List[Contact]:
        """
        搜索联系人

        【搜索范围】
        - 姓名
        - 邮箱
        - 电话
        - 备注

        【参数】
        keyword：搜索关键词

        【返回值】
        匹配的联系人列表

        【搜索逻辑】
        - 不区分大小写
        - 只要关键词出现在任一字段中就算匹配
        """
        keyword = keyword.lower()  # 转小写，实现不区分大小写
        results = []

        for c in self.contacts:
            # 检查各个字段是否包含关键词
            if (keyword in c.name.lower() or
                keyword in c.email.lower() or
                keyword in c.phone.lower() or
                keyword in c.notes.lower()):
                results.append(c)

        return results

    def export_to_csv(self, file_path: str) -> bool:
        """
        导出联系人到 CSV 文件

        【什么是 CSV】
        CSV 是一种表格数据格式，可以用 Excel 打开。
        每行是一条记录，字段用逗号分隔。

        【参数】
        file_path：要保存的文件路径

        【返回值】
        - True：导出成功
        - False：导出失败

        【导出格式】
        姓名,邮箱,电话,分组,备注
        张三,zhangsan@qq.com,13800138000,朋友,大学同学
        """
        try:
            # 打开文件准备写入
            # encoding='utf-8-sig'：UTF-8 编码并带有 BOM 标记
            # BOM 标记可以让 Excel 正确识别中文
            # newline=''：防止 Windows 下产生额外的空行
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)

                # 写入表头
                writer.writerow(['姓名', '邮箱', '电话', '分组', '备注'])

                # 写入每个联系人的数据
                for c in self.contacts:
                    writer.writerow([c.name, c.email, c.phone, c.group, c.notes])

            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False

    def import_from_csv(self, file_path: str) -> int:
        """
        从 CSV 文件导入联系人

        【参数】
        file_path：CSV 文件路径

        【返回值】
        成功导入的联系人数量

        【CSV 格式要求】
        第一行是表头：姓名,邮箱,电话,分组,备注
        后续每行是一个联系人的数据
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return 0

        imported = 0  # 导入计数器

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)

                # 跳过第一行（表头）
                # next() 获取迭代器的下一个元素
                header = next(reader, None)

                # 逐行读取数据
                for row in reader:
                    # 至少需要2个字段（姓名和邮箱）
                    if len(row) >= 2:
                        # 创建联系人对象
                        # 使用安全的索引访问，防止数组越界
                        contact = Contact(
                            name=row[0] if len(row) > 0 else "",
                            email=row[1] if len(row) > 1 else "",
                            phone=row[2] if len(row) > 2 else "",
                            group=row[3] if len(row) > 3 else "默认",
                            notes=row[4] if len(row) > 4 else ""
                        )

                        # 如果邮箱有效且添加成功，计数加1
                        if contact.email and self.add_contact(contact):
                            imported += 1

        except Exception as e:
            print(f"导入失败: {e}")

        return imported

    def export_to_json(self, file_path: str) -> bool:
        """
        导出联系人到 JSON 文件

        【参数】
        file_path：要保存的文件路径

        【返回值】
        - True：导出成功
        - False：导出失败
        """
        try:
            # 将联系人转换为字典列表
            data = [c.to_dict() for c in self.contacts]

            # 写入 JSON 文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False

    def import_from_json(self, file_path: str) -> int:
        """
        从 JSON 文件导入联系人

        【参数】
        file_path：JSON 文件路径

        【返回值】
        成功导入的联系人数量

        【JSON 格式要求】
        [
            {"name": "张三", "email": "zhangsan@qq.com", ...},
            {"name": "李四", "email": "lisi@163.com", ...}
        ]
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return 0

        imported = 0

        try:
            # 读取 JSON 文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 遍历每个联系人数据
            for item in data:
                # 从字典创建联系人对象
                contact = Contact.from_dict(item)

                # 如果邮箱有效且添加成功，计数加1
                if contact.email and self.add_contact(contact):
                    imported += 1

        except Exception as e:
            print(f"导入失败: {e}")

        return imported

    def clear(self):
        """
        清空所有联系人

        【注意】
        此操作会删除所有联系人数据！
        操作会立即保存到文件。
        """
        self.contacts.clear()  # 清空列表
        self.save_contacts()   # 保存空列表到文件
