"""
================================================================================
邮件管理模块 - 负责邮件的本地管理
================================================================================

【文件作用】
这个文件负责在程序内存中管理邮件，主要功能：
1. 存储和维护邮件列表
2. 搜索邮件（按关键词、发件人、主题、日期等）
3. 标记邮件已读
4. 删除邮件
5. 排序邮件
6. 统计邮件数量

【与 EmailReceiver 的区别】
- EmailReceiver：负责与邮件服务器通信，下载邮件
- EmailManager：负责在本地管理下载后的邮件

【设计模式】
这是一个简单的"管理器"模式，所有邮件操作都通过这个类进行，
便于统一管理和维护。
================================================================================
"""

# ============================================================================
# 导入必要的模块
# ============================================================================

# 类型提示：List 表示列表，Optional 表示可能为 None
from typing import List, Optional

# datetime：用于处理日期时间
from datetime import datetime

# 导入路径设置模块
import sys
import os

# 将项目根目录添加到模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入邮件数据类
from models.email_model import Email


# ============================================================================
# 邮件管理器类
# ============================================================================
class EmailManager:
    """
    邮件管理器类 - 负责邮件的本地存储和管理

    【主要功能】
    1. 存储邮件列表
    2. 搜索邮件
    3. 删除和标记邮件
    4. 排序和统计

    【使用示例】
    manager = EmailManager()

    # 设置邮件列表
    manager.set_emails(emails)

    # 搜索邮件
    results = manager.search_emails("关键词")

    # 获取未读数量
    count = manager.get_unread_count()
    """

    def __init__(self):
        """
        初始化邮件管理器

        【初始化内容】
        创建一个空的邮件列表，用于存储邮件
        """
        # 邮件列表：存储所有邮件对象
        # List[Email] 表示这是一个 Email 对象的列表
        self.emails: List[Email] = []

    def set_emails(self, emails: List[Email]):
        """
        设置邮件列表

        【用途】
        当从服务器获取邮件后，使用此方法将邮件列表存入管理器。

        【参数】
        emails：邮件对象列表
        """
        self.emails = emails

    def add_email(self, email: Email):
        """
        添加单封邮件

        【用途】
        当收到新邮件时，可以单独添加到列表中。

        【参数】
        email：要添加的邮件对象
        """
        self.emails.append(email)

    def get_all_emails(self) -> List[Email]:
        """
        获取所有邮件（不包括已删除的）

        【返回值】
        未删除的邮件列表

        【说明】
        使用列表推导式过滤掉已删除的邮件。
        列表推导式语法：[表达式 for 元素 in 列表 if 条件]
        """
        # 返回所有 is_deleted 为 False 的邮件
        return [e for e in self.emails if not e.is_deleted]

    def get_email_by_uid(self, uid: str) -> Optional[Email]:
        """
        根据邮件 UID 获取邮件

        【参数】
        uid：邮件的唯一标识符

        【返回值】
        - 如果找到，返回邮件对象
        - 如果未找到，返回 None
        """
        # 遍历所有邮件
        for email in self.emails:
            # 如果 UID 匹配，返回该邮件
            if email.uid == uid:
                return email
        # 未找到，返回 None
        return None

    def delete_email(self, uid: str) -> bool:
        """
        删除邮件（软删除，只标记为已删除）

        【软删除 vs 硬删除】
        - 软删除：只标记为已删除，数据还在（可以恢复）
        - 硬删除：彻底删除数据（不可恢复）

        【参数】
        uid：要删除的邮件的 UID

        【返回值】
        - True：删除成功
        - False：未找到该邮件
        """
        # 先查找邮件
        email = self.get_email_by_uid(uid)
        if email:
            # 标记为已删除
            email.is_deleted = True
            return True
        return False

    def remove_email(self, uid: str) -> bool:
        """
        彻底移除邮件（硬删除）

        【注意】
        此操作不可恢复！

        【参数】
        uid：要移除的邮件的 UID

        【返回值】
        - True：移除成功
        - False：未找到该邮件
        """
        # enumerate() 返回索引和元素
        for i, email in enumerate(self.emails):
            if email.uid == uid:
                # pop() 方法删除指定索引的元素
                self.emails.pop(i)
                return True
        return False

    def mark_as_read(self, uid: str) -> bool:
        """
        标记邮件为已读

        【参数】
        uid：邮件的 UID

        【返回值】
        - True：标记成功
        - False：未找到该邮件
        """
        email = self.get_email_by_uid(uid)
        if email:
            email.is_read = True
            return True
        return False

    def search_emails(self, keyword: str) -> List[Email]:
        """
        全文搜索邮件

        【搜索范围】
        - 发件人地址
        - 发件人名称
        - 邮件主题
        - 邮件正文

        【参数】
        keyword：搜索关键词

        【返回值】
        匹配的邮件列表

        【搜索逻辑】
        - 不区分大小写
        - 只要关键词出现在任一字段中就算匹配
        """
        # 如果关键词为空，返回所有邮件
        if not keyword:
            return self.get_all_emails()

        # 将关键词转为小写，实现不区分大小写的搜索
        keyword = keyword.lower()
        results = []

        for email in self.emails:
            # 跳过已删除的邮件
            if email.is_deleted:
                continue

            # 在发件人中搜索
            if keyword in email.sender.lower() or keyword in email.sender_name.lower():
                results.append(email)
                continue  # 已匹配，跳过后续检查

            # 在主题中搜索
            if keyword in email.subject.lower():
                results.append(email)
                continue

            # 在正文中搜索
            if keyword in email.content.lower():
                results.append(email)
                continue

        return results

    def search_by_sender(self, sender: str) -> List[Email]:
        """
        按发件人搜索

        【参数】
        sender：发件人关键词（地址或名称的一部分）

        【返回值】
        匹配的邮件列表
        """
        sender = sender.lower()
        # 使用列表推导式进行过滤
        return [e for e in self.emails
                if not e.is_deleted and
                (sender in e.sender.lower() or sender in e.sender_name.lower())]

    def search_by_subject(self, subject: str) -> List[Email]:
        """
        按主题搜索

        【参数】
        subject：主题关键词

        【返回值】
        匹配的邮件列表
        """
        subject = subject.lower()
        return [e for e in self.emails
                if not e.is_deleted and subject in e.subject.lower()]

    def search_by_date_range(self, start: datetime, end: datetime) -> List[Email]:
        """
        按日期范围搜索

        【参数】
        - start：开始日期
        - end：结束日期

        【返回值】
        在指定日期范围内的邮件列表

        【示例】
        from datetime import datetime
        start = datetime(2024, 1, 1)  # 2024年1月1日
        end = datetime(2024, 1, 31)   # 2024年1月31日
        emails = manager.search_by_date_range(start, end)
        """
        return [e for e in self.emails
                if not e.is_deleted and start <= e.date <= end]

    def get_unread_count(self) -> int:
        """
        获取未读邮件数量

        【返回值】
        未读邮件的数量

        【逻辑】
        统计所有未删除且未读的邮件数量
        """
        # len() 获取列表长度
        return len([e for e in self.emails if not e.is_deleted and not e.is_read])

    def get_total_count(self) -> int:
        """
        获取邮件总数

        【返回值】
        未删除邮件的总数
        """
        return len([e for e in self.emails if not e.is_deleted])

    def sort_by_date(self, reverse: bool = True) -> List[Email]:
        """
        按日期排序邮件

        【参数】
        reverse：是否倒序排列
                True（默认）：最新的在前面
                False：最旧的在前面

        【返回值】
        排序后的邮件列表

        【说明】
        - sorted() 函数返回一个新的排序列表，不会修改原列表
        - key 参数指定排序的依据，这里使用邮件的日期
        - lambda 是匿名函数，lambda x: x.date 表示取邮件的 date 属性
        """
        emails = self.get_all_emails()
        return sorted(emails, key=lambda x: x.date, reverse=reverse)

    def clear(self):
        """
        清空邮件列表

        【注意】
        此操作会清除所有邮件数据！
        """
        self.emails.clear()
