"""
================================================================================
邮件数据模型 - 定义程序中使用的数据结构
================================================================================

【文件作用】
这个文件定义了程序中使用的各种"数据类"（类似于表格的模板）。
就像你用 Excel 表格存储数据时需要先定义列名一样，
我们需要先定义数据的结构，然后才能存储和使用数据。

【包含的数据类】
1. Attachment（附件）：存储邮件附件的信息
2. Email（邮件）：存储一封邮件的所有信息
3. EmailAccount（邮箱账户）：存储邮箱登录配置
4. Contact（联系人）：存储通讯录中的联系人信息

【技术说明】
使用了 Python 的 dataclass 装饰器，它可以自动帮我们：
- 生成 __init__ 方法（创建对象时用）
- 生成 __repr__ 方法（打印对象时用）
- 减少重复代码，让代码更简洁
================================================================================
"""

# ============================================================================
# 导入必要的模块
# ============================================================================

# dataclass：Python 3.7+ 引入的装饰器，用于快速创建数据类
# field：用于设置字段的默认值（特别是列表、字典等可变类型）
from dataclasses import dataclass, field

# datetime：用于处理日期和时间
from datetime import datetime

# Optional：表示一个值可以是某种类型，也可以是 None
# List：表示列表类型
from typing import Optional, List


# ============================================================================
# 附件数据类
# ============================================================================
@dataclass
class Attachment:
    """
    附件数据类 - 存储邮件附件的信息

    【什么是附件】
    附件就是邮件中携带的文件，比如图片、文档、压缩包等。

    【属性说明】
    - filename：文件名，比如 "报告.docx"
    - content_type：文件类型，比如 "application/pdf" 表示 PDF 文件
    - data：文件的实际内容（二进制数据）
    - size：文件大小（字节数）

    【使用示例】
    attachment = Attachment(
        filename="照片.jpg",
        content_type="image/jpeg",
        data=b"...(文件二进制数据)...",
        size=1024000
    )
    print(attachment.get_size_str())  # 输出: "1000.0 KB"
    """

    # 文件名，比如 "文档.pdf"、"照片.jpg"
    filename: str

    # MIME 类型，用于标识文件的类型
    # 常见的 MIME 类型：
    # - "text/plain"：纯文本
    # - "image/jpeg"：JPEG 图片
    # - "image/png"：PNG 图片
    # - "application/pdf"：PDF 文档
    # - "application/msword"：Word 文档
    content_type: str

    # 文件的二进制数据
    # bytes 类型用于存储二进制数据（如图片、文档的原始内容）
    data: bytes

    # 文件大小，单位是字节（Byte）
    # 1 KB = 1024 字节
    # 1 MB = 1024 KB = 1048576 字节
    size: int = 0

    def get_size_str(self) -> str:
        """
        获取人类可读的文件大小字符串

        【为什么需要这个方法】
        文件大小用字节表示时数字很大，不容易阅读。
        比如 1048576 字节，转换后是 "1.0 MB"，更容易理解。

        【返回值示例】
        - 500 字节 -> "500 B"
        - 2048 字节 -> "2.0 KB"
        - 1048576 字节 -> "1.0 MB"
        """
        if self.size < 1024:
            # 小于 1KB，显示字节
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            # 小于 1MB，显示 KB（保留一位小数）
            return f"{self.size / 1024:.1f} KB"
        else:
            # 大于等于 1MB，显示 MB（保留一位小数）
            return f"{self.size / (1024 * 1024):.1f} MB"


# ============================================================================
# 邮件数据类
# ============================================================================
@dataclass
class Email:
    """
    邮件数据类 - 存储一封邮件的所有信息

    【属性说明】
    - uid：邮件的唯一标识符，用于在服务器上定位这封邮件
    - sender：发件人的邮箱地址
    - sender_name：发件人的显示名称
    - recipient：收件人的邮箱地址
    - subject：邮件主题（标题）
    - content：邮件正文内容
    - date：邮件发送/接收的时间
    - is_read：是否已读
    - is_deleted：是否已删除
    - folder：邮件所在的文件夹
    - attachments：附件列表

    【使用示例】
    email = Email(
        uid="123",
        sender="zhangsan@qq.com",
        sender_name="张三",
        recipient="lisi@163.com",
        subject="你好",
        content="这是邮件正文",
        date=datetime.now()
    )
    print(email.get_date_str())  # 输出: "2024-01-15 10:30"
    """

    # 邮件唯一标识符（UID = Unique Identifier）
    # 每封邮件在服务器上都有一个唯一的编号
    uid: str

    # 发件人的邮箱地址，比如 "zhangsan@qq.com"
    sender: str

    # 发件人的显示名称，比如 "张三"
    # 有时候邮件只有地址没有名称，这时名称就等于地址
    sender_name: str

    # 收件人的邮箱地址
    recipient: str

    # 邮件主题（标题）
    subject: str

    # 邮件正文内容
    content: str

    # 邮件的日期时间
    # datetime 类型可以存储年、月、日、时、分、秒
    date: datetime

    # 是否已读，默认为 False（未读）
    is_read: bool = False

    # 是否已删除，默认为 False
    is_deleted: bool = False

    # 邮件所在的文件夹，默认是 "INBOX"（收件箱）
    folder: str = "INBOX"

    # 附件列表
    # field(default_factory=list) 的意思是：默认值是一个空列表
    # 注意：不能直接写 attachments: List[Attachment] = []
    # 因为 Python 中可变对象（如列表）作为默认值会有问题
    attachments: List[Attachment] = field(default_factory=list)

    def get_date_str(self) -> str:
        """
        获取格式化的日期字符串

        【返回格式】
        "年-月-日 时:分"，比如 "2024-01-15 10:30"

        【格式说明】
        %Y：四位数的年份（2024）
        %m：两位数的月份（01-12）
        %d：两位数的日期（01-31）
        %H：24小时制的小时（00-23）
        %M：两位数的分钟（00-59）
        """
        return self.date.strftime("%Y-%m-%d %H:%M")

    def get_short_content(self, max_length: int = 50) -> str:
        """
        获取邮件内容的摘要（简短版本）

        【参数】
        max_length：最大长度，默认 50 个字符

        【作用】
        在邮件列表中显示时，只显示开头的一部分内容，
        如果内容太长就截断并加上 "..."

        【示例】
        原文："这是一封很长很长的邮件，包含了很多内容..."
        摘要："这是一封很长很长的邮件，包含了很多内容..."（超过50字会被截断）
        """
        # 将换行符替换为空格，并去掉首尾空白
        content = self.content.replace('\n', ' ').strip()

        # 如果内容超过最大长度，截断并加上省略号
        if len(content) > max_length:
            return content[:max_length] + "..."

        return content

    def has_attachments(self) -> bool:
        """
        检查邮件是否有附件

        【返回值】
        True：有附件
        False：没有附件
        """
        return len(self.attachments) > 0


# ============================================================================
# 邮箱账户配置类
# ============================================================================
@dataclass
class EmailAccount:
    """
    邮箱账户配置类 - 存储邮箱的登录信息和服务器配置

    【什么是 IMAP 和 SMTP】
    - IMAP（Internet Message Access Protocol）：用于接收邮件的协议
    - SMTP（Simple Mail Transfer Protocol）：用于发送邮件的协议
    这就像是两条不同的路：一条用来收信，一条用来寄信。

    【什么是 SSL】
    SSL（Secure Sockets Layer）是一种加密技术，
    可以保护你的邮件内容在传输过程中不被窃取。
    现在几乎所有邮箱都使用 SSL 加密。

    【常见端口号】
    - IMAP + SSL：993
    - SMTP + SSL：465 或 587
    端口号就像是门牌号，不同的服务使用不同的端口。

    【使用示例】
    # 方法1：手动创建
    account = EmailAccount(
        email="zhangsan@qq.com",
        password="abc123",
        imap_server="imap.qq.com",
        imap_port=993,
        smtp_server="smtp.qq.com",
        smtp_port=465,
        use_ssl=True
    )

    # 方法2：使用预设配置
    account = EmailAccount.get_preset("qq", "zhangsan@qq.com", "abc123")
    """

    # 邮箱地址，比如 "zhangsan@qq.com"
    email: str

    # 密码或授权码
    # 注意：很多邮箱（如 QQ 邮箱）需要使用"授权码"而不是登录密码
    # 授权码可以在邮箱设置中生成
    password: str

    # IMAP 服务器地址，用于接收邮件
    # 例如：
    # - QQ 邮箱：imap.qq.com
    # - 163 邮箱：imap.163.com
    # - Gmail：imap.gmail.com
    imap_server: str

    # IMAP 服务器端口号，通常是 993（使用 SSL 时）
    imap_port: int

    # SMTP 服务器地址，用于发送邮件
    # 例如：
    # - QQ 邮箱：smtp.qq.com
    # - 163 邮箱：smtp.163.com
    # - Gmail：smtp.gmail.com
    smtp_server: str

    # SMTP 服务器端口号，通常是 465 或 587
    smtp_port: int

    # 是否使用 SSL 加密，默认为 True（强烈建议开启）
    use_ssl: bool = True

    @classmethod
    def get_preset(cls, provider: str, email: str, password: str) -> Optional['EmailAccount']:
        """
        获取常见邮箱的预设配置

        【什么是类方法 @classmethod】
        类方法可以不创建对象就直接调用，比如：
        EmailAccount.get_preset("qq", "xxx@qq.com", "密码")

        【参数说明】
        - provider：邮箱提供商，支持 "qq"、"163"、"126"、"gmail"、"outlook"
        - email：邮箱地址
        - password：密码或授权码

        【返回值】
        - 如果是支持的邮箱，返回配置好的 EmailAccount 对象
        - 如果不支持，返回 None

        【使用示例】
        account = EmailAccount.get_preset("qq", "test@qq.com", "abc123")
        if account:
            print("配置成功")
        else:
            print("不支持的邮箱类型")
        """

        # 预设配置字典
        # 每种邮箱的服务器地址和端口都是固定的
        presets = {
            # QQ 邮箱配置
            'qq': {
                'imap_server': 'imap.qq.com',     # QQ 邮箱 IMAP 服务器
                'imap_port': 993,                  # IMAP 端口（SSL）
                'smtp_server': 'smtp.qq.com',     # QQ 邮箱 SMTP 服务器
                'smtp_port': 465,                  # SMTP 端口（SSL）
                'use_ssl': True                    # 使用 SSL 加密
            },
            # 网易 163 邮箱配置
            '163': {
                'imap_server': 'imap.163.com',
                'imap_port': 993,
                'smtp_server': 'smtp.163.com',
                'smtp_port': 465,
                'use_ssl': True
            },
            # 网易 126 邮箱配置
            '126': {
                'imap_server': 'imap.126.com',
                'imap_port': 993,
                'smtp_server': 'smtp.126.com',
                'smtp_port': 465,
                'use_ssl': True
            },
            # Gmail 配置
            'gmail': {
                'imap_server': 'imap.gmail.com',
                'imap_port': 993,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,                  # Gmail 使用 587 端口
                'use_ssl': True
            },
            # Outlook/Hotmail 配置
            'outlook': {
                'imap_server': 'outlook.office365.com',
                'imap_port': 993,
                'smtp_server': 'smtp.office365.com',
                'smtp_port': 587,
                'use_ssl': True
            }
        }

        # 检查是否支持该邮箱类型
        # .lower() 将输入转换为小写，这样 "QQ"、"qq"、"Qq" 都能识别
        if provider.lower() in presets:
            # 获取对应的配置
            config = presets[provider.lower()]

            # 创建并返回 EmailAccount 对象
            # **config 会把字典中的键值对展开作为参数传入
            # 相当于：
            # cls(email=email, password=password,
            #     imap_server='imap.qq.com', imap_port=993, ...)
            return cls(
                email=email,
                password=password,
                **config
            )

        # 如果不支持该邮箱类型，返回 None
        return None


# ============================================================================
# 联系人数据类
# ============================================================================
@dataclass
class Contact:
    """
    联系人数据类 - 存储通讯录中的联系人信息

    【属性说明】
    - name：联系人姓名
    - email：邮箱地址
    - phone：电话号码（可选）
    - group：分组名称，默认是 "默认"
    - notes：备注信息（可选）

    【使用示例】
    contact = Contact(
        name="张三",
        email="zhangsan@qq.com",
        phone="13800138000",
        group="朋友",
        notes="大学同学"
    )

    # 转换为字典（用于保存到文件）
    data = contact.to_dict()

    # 从字典创建联系人（用于从文件读取）
    contact = Contact.from_dict(data)
    """

    # 联系人姓名
    name: str

    # 邮箱地址
    email: str

    # 电话号码，可选，默认为空字符串
    phone: str = ""

    # 分组名称，默认是 "默认" 分组
    group: str = "默认"

    # 备注信息，可选
    notes: str = ""

    def to_dict(self) -> dict:
        """
        将联系人对象转换为字典

        【为什么需要这个方法】
        Python 对象不能直接保存到文件，需要先转换为字典，
        然后用 JSON 格式保存。

        【返回值示例】
        {
            'name': '张三',
            'email': 'zhangsan@qq.com',
            'phone': '13800138000',
            'group': '朋友',
            'notes': '大学同学'
        }
        """
        return {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'group': self.group,
            'notes': self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Contact':
        """
        从字典创建联系人对象

        【什么是类方法 @classmethod】
        类方法可以不创建对象就直接调用，比如：
        Contact.from_dict({'name': '张三', 'email': 'xxx@qq.com'})

        【参数说明】
        data：包含联系人信息的字典

        【返回值】
        创建好的 Contact 对象

        【使用示例】
        data = {'name': '张三', 'email': 'zhangsan@qq.com'}
        contact = Contact.from_dict(data)
        print(contact.name)  # 输出: 张三
        """
        # 使用 .get() 方法获取字典中的值
        # .get() 的好处是：如果键不存在，不会报错，而是返回默认值
        return cls(
            name=data.get('name', ''),           # 如果没有 name，返回空字符串
            email=data.get('email', ''),         # 如果没有 email，返回空字符串
            phone=data.get('phone', ''),         # 如果没有 phone，返回空字符串
            group=data.get('group', '默认'),      # 如果没有 group，返回 "默认"
            notes=data.get('notes', '')          # 如果没有 notes，返回空字符串
        )
