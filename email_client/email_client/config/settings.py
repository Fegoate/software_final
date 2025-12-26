"""
================================================================================
配置管理模块 - 负责保存和读取用户的邮箱账户配置
================================================================================

【文件作用】
这个文件负责管理用户的配置信息，主要功能：
1. 保存邮箱账户信息（邮箱地址、密码、服务器设置等）
2. 读取已保存的账户信息
3. 删除账户信息
4. 提供常见邮箱的预设配置

【配置文件存储位置】
配置文件保存在用户目录下的隐藏文件夹中：
- Windows: C:\\Users\\用户名\\.email_client\\config.json
- Mac/Linux: /Users/用户名/.email_client/config.json

【为什么需要保存配置】
用户每次打开邮件客户端时，不需要重新输入邮箱账号和密码，
程序会自动读取之前保存的配置，提升用户体验。

【安全提示】
目前密码是明文保存的，在实际生产环境中应该加密存储。
================================================================================
"""

# ============================================================================
# 导入必要的模块
# ============================================================================

# json 模块：用于读写 JSON 格式的文件
# JSON 是一种常用的数据交换格式，易于人类阅读和机器解析
import json

# os 模块：提供与操作系统交互的功能
import os

# sys 模块：提供与 Python 解释器交互的功能
import sys

# Optional：表示一个值可以是某种类型，也可以是 None
from typing import Optional

# Path：更现代化的路径处理类，比 os.path 更好用
from pathlib import Path

# 将项目根目录添加到模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入邮箱账户数据类
from models.email_model import EmailAccount


# ============================================================================
# 配置管理器类
# ============================================================================
class Settings:
    """
    配置管理器类 - 负责保存和读取邮箱账户配置

    【主要功能】
    1. save_account()：保存账户配置到文件
    2. load_account()：从文件读取账户配置
    3. delete_account()：删除保存的配置
    4. has_saved_account()：检查是否有已保存的配置

    【使用示例】
    # 创建配置管理器
    settings = Settings()

    # 保存账户
    account = EmailAccount(...)
    settings.save_account(account)

    # 读取账户
    account = settings.load_account()
    if account:
        print(f"已保存的邮箱: {account.email}")
    """

    def __init__(self):
        """
        初始化配置管理器

        【初始化过程】
        1. 确定配置文件的存储路径
        2. 确保配置目录存在
        """

        # 配置文件目录：用户主目录下的 .email_client 文件夹
        # Path.home() 返回当前用户的主目录
        # 例如：Windows 上是 C:\\Users\\用户名
        # "/" 运算符用于连接路径（Path 类的特殊用法）
        self.config_dir = Path.home() / ".email_client"

        # 配置文件的完整路径
        # 例如：C:\\Users\\用户名\\.email_client\\config.json
        self.config_file = self.config_dir / "config.json"

        # 确保配置目录存在（如果不存在就创建）
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """
        确保配置目录存在

        【方法名前的下划线 _ 】
        Python 中，方法名以下划线开头表示这是一个"私有"方法，
        意味着这个方法只在类内部使用，不建议外部直接调用。
        """
        # 检查目录是否存在
        if not self.config_dir.exists():
            # 如果不存在，创建目录
            # parents=True 表示如果父目录不存在也一并创建
            self.config_dir.mkdir(parents=True)

    def save_account(self, account: EmailAccount) -> bool:
        """
        保存账户配置到文件

        【参数】
        account：要保存的邮箱账户对象

        【返回值】
        True：保存成功
        False：保存失败

        【保存的内容】
        - 邮箱地址
        - 密码（授权码）
        - IMAP 服务器地址和端口
        - SMTP 服务器地址和端口
        - 是否使用 SSL

        【文件格式】
        保存为 JSON 格式，例如：
        {
            "email": "test@qq.com",
            "password": "abc123",
            "imap_server": "imap.qq.com",
            ...
        }
        """
        try:
            # 将账户信息转换为字典
            config = {
                'email': account.email,
                'password': account.password,  # 注意：实际应用中应该加密存储
                'imap_server': account.imap_server,
                'imap_port': account.imap_port,
                'smtp_server': account.smtp_server,
                'smtp_port': account.smtp_port,
                'use_ssl': account.use_ssl
            }

            # 将配置写入文件
            # open() 打开文件，'w' 表示写入模式（会覆盖原有内容）
            # encoding='utf-8' 指定使用 UTF-8 编码（支持中文）
            # with 语句确保文件使用完后自动关闭
            with open(self.config_file, 'w', encoding='utf-8') as f:
                # json.dump() 将字典转换为 JSON 并写入文件
                # indent=2 表示使用 2 个空格缩进，让文件更易读
                json.dump(config, f, indent=2)

            return True

        except Exception as e:
            # 如果保存过程中出错，打印错误信息并返回 False
            print(f"保存配置失败: {e}")
            return False

    def load_account(self) -> Optional[EmailAccount]:
        """
        从文件加载账户配置

        【返回值】
        - 如果配置文件存在且读取成功，返回 EmailAccount 对象
        - 如果配置文件不存在或读取失败，返回 None

        【Optional 类型说明】
        Optional[EmailAccount] 表示返回值可能是 EmailAccount 对象，
        也可能是 None。这提醒调用者需要检查返回值是否为 None。
        """
        # 首先检查配置文件是否存在
        if not self.config_file.exists():
            return None

        try:
            # 打开并读取配置文件
            # 'r' 表示读取模式
            with open(self.config_file, 'r', encoding='utf-8') as f:
                # json.load() 读取 JSON 文件并转换为字典
                config = json.load(f)

            # 根据读取的配置创建 EmailAccount 对象
            return EmailAccount(
                email=config['email'],
                password=config['password'],
                imap_server=config['imap_server'],
                imap_port=config['imap_port'],
                smtp_server=config['smtp_server'],
                smtp_port=config['smtp_port'],
                # .get() 方法可以提供默认值，如果 'use_ssl' 不存在则使用 True
                use_ssl=config.get('use_ssl', True)
            )

        except Exception as e:
            # 如果读取过程中出错，打印错误信息并返回 None
            print(f"加载配置失败: {e}")
            return None

    def delete_account(self) -> bool:
        """
        删除保存的账户配置

        【返回值】
        True：删除成功
        False：删除失败

        【使用场景】
        当用户想要注销账户或切换账户时，需要删除已保存的配置。
        """
        try:
            # 检查配置文件是否存在
            if self.config_file.exists():
                # 删除配置文件
                os.remove(self.config_file)
            return True

        except Exception as e:
            print(f"删除配置失败: {e}")
            return False

    def has_saved_account(self) -> bool:
        """
        检查是否有已保存的账户配置

        【返回值】
        True：有已保存的配置
        False：没有已保存的配置

        【使用场景】
        程序启动时，检查是否有已保存的账户：
        - 如果有，自动登录
        - 如果没有，显示登录界面
        """
        return self.config_file.exists()


# ============================================================================
# 常见邮箱服务器预设配置
# ============================================================================
# 这是一个字典，存储了常见邮箱的服务器配置
# 用户选择邮箱类型后，可以自动填充服务器地址和端口
EMAIL_PRESETS = {
    # -------------------------------------------------------------------------
    # QQ 邮箱配置
    # -------------------------------------------------------------------------
    'QQ邮箱': {
        'imap_server': 'imap.qq.com',    # IMAP 服务器地址（用于接收邮件）
        'imap_port': 993,                 # IMAP 端口（SSL 加密）
        'smtp_server': 'smtp.qq.com',    # SMTP 服务器地址（用于发送邮件）
        'smtp_port': 465,                 # SMTP 端口（SSL 加密）
        'use_ssl': True,                  # 使用 SSL 加密
        'note': '需要在QQ邮箱设置中开启IMAP/SMTP服务并获取授权码'  # 使用说明
    },

    # -------------------------------------------------------------------------
    # 网易 163 邮箱配置
    # -------------------------------------------------------------------------
    '163邮箱': {
        'imap_server': 'imap.163.com',
        'imap_port': 993,
        'smtp_server': 'smtp.163.com',
        'smtp_port': 465,
        'use_ssl': True,
        'note': '需要在163邮箱设置中开启IMAP/SMTP服务并设置授权码'
    },

    # -------------------------------------------------------------------------
    # 网易 126 邮箱配置
    # -------------------------------------------------------------------------
    '126邮箱': {
        'imap_server': 'imap.126.com',
        'imap_port': 993,
        'smtp_server': 'smtp.126.com',
        'smtp_port': 465,
        'use_ssl': True,
        'note': '需要在126邮箱设置中开启IMAP/SMTP服务并设置授权码'
    },

    # -------------------------------------------------------------------------
    # Gmail 配置（谷歌邮箱）
    # -------------------------------------------------------------------------
    'Gmail': {
        'imap_server': 'imap.gmail.com',
        'imap_port': 993,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,                 # Gmail 的 SMTP 使用 587 端口
        'use_ssl': True,
        'note': '需要开启两步验证并使用应用专用密码'
    },

    # -------------------------------------------------------------------------
    # Outlook/Hotmail 配置（微软邮箱）
    # -------------------------------------------------------------------------
    'Outlook/Hotmail': {
        'imap_server': 'outlook.office365.com',
        'imap_port': 993,
        'smtp_server': 'smtp.office365.com',
        'smtp_port': 587,
        'use_ssl': True,
        'note': '使用Microsoft账户密码或应用密码'
    },

    # -------------------------------------------------------------------------
    # 自定义配置（用于其他邮箱）
    # -------------------------------------------------------------------------
    '自定义': {
        'imap_server': '',    # 留空，需要用户自己填写
        'imap_port': 993,
        'smtp_server': '',
        'smtp_port': 465,
        'use_ssl': True,
        'note': '请填写您的邮箱服务器信息'
    }
}
