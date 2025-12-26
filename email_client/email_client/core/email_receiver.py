"""
================================================================================
IMAP 邮件接收模块 - 负责从邮件服务器接收邮件
================================================================================

【文件作用】
这个文件负责接收邮件，主要功能：
1. 连接到 IMAP 服务器
2. 获取邮件夹列表（收件箱、已发送、草稿箱等）
3. 获取邮件列表
4. 下载邮件内容和附件
5. 管理邮件夹（创建、删除、重命名）
6. 移动和删除邮件

【什么是 IMAP】
IMAP（Internet Message Access Protocol，互联网邮件访问协议）是用于接收邮件的标准协议。
与 POP3 不同，IMAP 可以让你在服务器上管理邮件，而不是下载后删除。
这意味着你可以在多个设备上同步查看同一个邮箱的邮件。

【IMAP UTF-7 编码】
IMAP 协议使用一种特殊的 UTF-7 编码来处理非 ASCII 字符（如中文）的文件夹名称。
这个编码与标准的 UTF-7 略有不同，主要区别是：
- 使用 & 代替 + 作为转义符
- 使用 , 代替 / 作为 Base64 填充
================================================================================
"""

# ============================================================================
# 导入必要的模块
# ============================================================================

# imaplib：Python 内置的 IMAP 协议库，用于接收邮件
import imaplib

# email：用于解析邮件内容
import email

# decode_header：用于解码邮件头中的编码文本（如主题、发件人名称）
from email.header import decode_header

# parsedate_to_datetime：将邮件中的日期字符串转换为 datetime 对象
from email.utils import parsedate_to_datetime

# 类型提示
from typing import List, Optional, Tuple

# datetime：用于处理日期时间
from datetime import datetime

# codecs：用于编码解码操作
import codecs

# 导入路径设置模块
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入数据模型
from models.email_model import Email, EmailAccount, Attachment


# ============================================================================
# IMAP UTF-7 编码解码函数
# ============================================================================

def imap_utf7_decode(s: str) -> str:
    """
    解码 IMAP UTF-7 编码的文件夹名称

    【为什么需要这个函数】
    IMAP 协议使用修改版的 UTF-7 编码来表示非 ASCII 字符的文件夹名称。
    例如，"已发送" 会被编码为 "&XstrQ9c-"。
    这个函数将编码后的名称转换回中文。

    【参数】
    s：IMAP UTF-7 编码的字符串

    【返回值】
    解码后的字符串（如中文）

    【编码规则】
    - & 开始编码段
    - - 结束编码段
    - &- 表示 & 字符本身
    - & 和 - 之间是 Base64 编码的 Unicode 文本
    """
    if not s:
        return s

    try:
        result = []  # 存储解码结果
        i = 0  # 当前处理位置

        while i < len(s):
            if s[i] == '&':
                # 找到编码段的结束位置
                end = s.find('-', i)
                if end == -1:
                    end = len(s)

                if i + 1 == end:
                    # &- 表示 & 字符本身
                    result.append('&')
                else:
                    # 将 IMAP UTF-7 转换为标准 UTF-7
                    # IMAP: & 开始，, 替代 /
                    # 标准: + 开始，/ 不变
                    encoded = '+' + s[i+1:end].replace(',', '/')
                    try:
                        # 解码标准 UTF-7
                        decoded = codecs.decode(encoded.encode('ascii'), 'utf-7')
                        result.append(decoded)
                    except:
                        # 解码失败，保留原始内容
                        result.append(s[i:end+1])
                i = end + 1
            else:
                # 普通 ASCII 字符，直接添加
                result.append(s[i])
                i += 1

        return ''.join(result)
    except:
        return s


def imap_utf7_encode(s: str) -> str:
    """
    将字符串编码为 IMAP UTF-7 格式

    【为什么需要这个函数】
    当我们创建中文名称的邮件夹时，需要将中文转换为 IMAP UTF-7 编码。

    【参数】
    s：要编码的字符串（如中文文件夹名称）

    【返回值】
    IMAP UTF-7 编码后的字符串
    """
    if not s:
        return s

    try:
        # 检查是否全是 ASCII 字符
        # 如果是，只需要处理 & 字符（转换为 &-）
        if all(ord(c) < 128 and c != '&' for c in s):
            return s.replace('&', '&-')

        # 将字符串编码为标准 UTF-7
        utf7_bytes = s.encode('utf-7')
        utf7_str = utf7_bytes.decode('ascii')

        # 将标准 UTF-7 转换为 IMAP UTF-7
        # 标准 UTF-7 使用 +，IMAP UTF-7 使用 &
        result = utf7_str.replace('+', '&').replace(',', ',')
        return result
    except:
        return s


# ============================================================================
# 邮件接收器类
# ============================================================================
class EmailReceiver:
    """
    IMAP 邮件接收器类

    【主要功能】
    1. connect() / disconnect()：连接/断开 IMAP 服务器
    2. get_folders()：获取所有邮件夹
    3. fetch_emails()：获取邮件列表
    4. create_folder() / delete_folder() / rename_folder()：管理邮件夹
    5. move_email() / delete_email()：管理邮件
    6. mark_as_read()：标记邮件已读

    【使用示例】
    receiver = EmailReceiver(account)

    # 连接服务器
    success, msg = receiver.connect()

    # 获取文件夹列表
    folders = receiver.get_folders()

    # 获取收件箱邮件
    emails = receiver.fetch_emails("INBOX", limit=50)

    # 断开连接
    receiver.disconnect()
    """

    def __init__(self, account: EmailAccount):
        """
        初始化邮件接收器

        【参数】
        account：邮箱账户配置对象
        """
        # 保存账户配置
        self.account = account

        # IMAP 连接对象，初始为 None（未连接）
        self.connection: Optional[imaplib.IMAP4_SSL] = None

        # 当前选中的文件夹，默认是收件箱
        self.current_folder = "INBOX"

        # 文件夹名称映射：显示名称 -> 原始名称
        # 例如：{"已发送": '"Sent Messages"', "草稿箱": '"Drafts"'}
        self.folder_map = {}

    def connect(self) -> Tuple[bool, str]:
        """
        连接到 IMAP 服务器

        【返回值】
        (成功标志, 消息) 元组：
        - (True, "连接成功")：连接成功
        - (False, 错误信息)：连接失败
        """
        try:
            # 根据是否使用 SSL 选择连接方式
            if self.account.use_ssl:
                # 使用 SSL 加密连接（端口通常是 993）
                self.connection = imaplib.IMAP4_SSL(
                    self.account.imap_server,
                    self.account.imap_port
                )
            else:
                # 不使用 SSL 的普通连接
                self.connection = imaplib.IMAP4(
                    self.account.imap_server,
                    self.account.imap_port
                )

            # 登录服务器
            self.connection.login(self.account.email, self.account.password)
            return True, "连接成功"

        except imaplib.IMAP4.error as e:
            # IMAP 协议错误（通常是登录失败）
            return False, f"登录失败: {str(e)}"
        except Exception as e:
            # 其他错误（如网络问题）
            return False, f"连接失败: {str(e)}"

    def disconnect(self):
        """
        断开与 IMAP 服务器的连接

        【说明】
        即使断开失败，也会将连接对象设为 None，
        这样可以避免后续操作使用无效的连接。
        """
        if self.connection:
            try:
                # logout() 发送 LOGOUT 命令并关闭连接
                self.connection.logout()
            except:
                pass
            self.connection = None

    def _decode_str(self, s: str) -> str:
        """
        解码邮件头字符串

        【为什么需要这个函数】
        邮件的主题、发件人名称等可能包含编码文本，如：
        =?UTF-8?B?5rWL6K+V?=（Base64 编码的 "测试"）
        =?UTF-8?Q?Hello?=（Quoted-Printable 编码）

        【参数】
        s：可能包含编码的字符串

        【返回值】
        解码后的字符串
        """
        if s is None:
            return ""

        # decode_header 返回 [(解码内容, 编码方式), ...] 的列表
        decoded_parts = decode_header(s)
        result = []

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                # 如果是字节串，需要解码
                try:
                    if encoding:
                        # 使用指定的编码解码
                        result.append(part.decode(encoding))
                    else:
                        # 没有指定编码，尝试 UTF-8
                        result.append(part.decode('utf-8', errors='ignore'))
                except:
                    # 解码失败，强制使用 UTF-8
                    result.append(part.decode('utf-8', errors='ignore'))
            else:
                # 已经是字符串，直接使用
                result.append(part)

        return ''.join(result)

    def _parse_sender(self, from_header: str) -> Tuple[str, str]:
        """
        解析发件人信息

        【发件人格式示例】
        - 简单格式：user@example.com
        - 带名称格式：张三 <zhangsan@example.com>
        - 带引号格式："张三" <zhangsan@example.com>

        【参数】
        from_header：邮件的 From 头内容

        【返回值】
        (邮箱地址, 显示名称) 元组
        """
        # 先解码可能的编码内容
        from_header = self._decode_str(from_header)

        if '<' in from_header and '>' in from_header:
            # 格式：名称 <邮箱>
            # 提取 < 之前的部分作为名称
            name = from_header.split('<')[0].strip().strip('"')
            # 提取 < 和 > 之间的部分作为邮箱
            addr = from_header.split('<')[1].split('>')[0]
            return addr, name if name else addr
        # 简单格式：直接就是邮箱地址
        return from_header, from_header

    def _get_email_content(self, msg) -> Tuple[str, List[Attachment]]:
        """
        获取邮件正文内容和附件

        【邮件结构说明】
        邮件可以是：
        1. 简单邮件：只有纯文本正文
        2. 多部分邮件：包含正文和/或附件的组合

        【参数】
        msg：email.message.Message 对象

        【返回值】
        (正文内容, 附件列表) 元组
        """
        content = ""          # 邮件正文
        attachments = []      # 附件列表

        if msg.is_multipart():
            # 多部分邮件：遍历所有部分
            for part in msg.walk():
                # 获取内容类型和处置方式
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                # 处理附件
                if "attachment" in content_disposition or part.get_filename():
                    filename = part.get_filename()
                    if filename:
                        # 解码文件名
                        filename = self._decode_str(filename)
                        # 获取附件数据
                        data = part.get_payload(decode=True)
                        if data:
                            # 创建附件对象
                            attachment = Attachment(
                                filename=filename,
                                content_type=content_type,
                                data=data,
                                size=len(data)
                            )
                            attachments.append(attachment)
                    continue

                # 处理正文（优先使用纯文本，其次是 HTML）
                if content_type == "text/plain" and not content:
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        payload = part.get_payload(decode=True)
                        if payload:
                            content = payload.decode(charset, errors='ignore')
                    except:
                        continue
                elif content_type == "text/html" and not content:
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        payload = part.get_payload(decode=True)
                        if payload:
                            # 简单去除 HTML 标签
                            import re
                            html_content = payload.decode(charset, errors='ignore')
                            content = re.sub('<[^<]+?>', '', html_content)
                    except:
                        continue
        else:
            # 简单邮件：直接获取正文
            try:
                charset = msg.get_content_charset() or 'utf-8'
                payload = msg.get_payload(decode=True)
                if payload:
                    content = payload.decode(charset, errors='ignore')
            except:
                content = ""

        return content.strip(), attachments

    def get_folders(self) -> List[str]:
        """
        获取所有邮件夹列表

        【返回值】
        邮件夹显示名称列表（如 ["收件箱", "已发送", "草稿箱"]）

        【处理说明】
        1. 从服务器获取原始文件夹列表
        2. 解析文件夹名称（处理 IMAP UTF-7 编码）
        3. 过滤掉不可选择的文件夹（NoSelect 标志）
        4. 建立显示名称到原始名称的映射
        """
        folders = []
        self.folder_map = {}

        if not self.connection:
            return ["INBOX"]

        try:
            # 获取文件夹列表
            _, folder_list = self.connection.list()

            for folder_data in folder_list:
                if folder_data:
                    # 解析文件夹数据
                    folder_str = folder_data.decode() if isinstance(folder_data, bytes) else str(folder_data)

                    # 跳过 NoSelect 文件夹（不能被选中的，如分隔符）
                    if '\\NoSelect' in folder_str:
                        continue

                    # 提取文件夹名（原始编码）
                    raw_name = None
                    if '"' in folder_str:
                        # 格式：(...) "/" "文件夹名"
                        parts = folder_str.split('"')
                        if len(parts) >= 4:
                            raw_name = parts[-2]
                    elif ' ' in folder_str:
                        # 简单格式：属性 分隔符 文件夹名
                        raw_name = folder_str.split(' ')[-1]

                    if raw_name:
                        # 解码显示名称（处理中文等）
                        display_name = imap_utf7_decode(raw_name)
                        folders.append(display_name)
                        # 保存映射（保持原始名称，交给 imaplib 处理引号）
                        self.folder_map[display_name] = raw_name

        except Exception as e:
            print(f"获取文件夹列表失败: {e}")

        # 如果没有获取到任何文件夹，至少返回收件箱
        if not folders:
            folders = ["INBOX"]
            self.folder_map["INBOX"] = "INBOX"

        return folders

    def get_raw_folder_name(self, display_name: str) -> str:
        """
        获取文件夹的原始名称（用于 IMAP 命令）

        【参数】
        display_name：显示名称（如 "已发送"）

        【返回值】
        原始名称（如 '"Sent Messages"'）
        """
        raw = self.folder_map.get(display_name)

        # 如果映射不存在，说明可能还没调用过 get_folders，
        # 直接对显示名称进行 IMAP UTF-7 编码，确保非 ASCII 名称也能被服务器识别。
        if raw is None:
            raw = imap_utf7_encode(display_name)

        return raw

    def create_folder(self, folder_name: str) -> Tuple[bool, str]:
        """
        创建新邮件夹

        【参数】
        folder_name：文件夹名称（支持中文）

        【返回值】
        (成功标志, 消息) 元组
        """
        if not self.connection:
            return False, "未连接到服务器"

        try:
            # 将中文名称编码为 IMAP UTF-7
            raw_name = imap_utf7_encode(folder_name)
            # 创建文件夹（imaplib 会自动处理引号）
            self.connection.create(raw_name)
            # 更新映射
            self.folder_map[folder_name] = raw_name
            return True, f"文件夹 '{folder_name}' 创建成功"
        except Exception as e:
            return False, f"创建失败: {str(e)}"

    def delete_folder(self, folder_name: str) -> Tuple[bool, str]:
        """
        删除邮件夹

        【参数】
        folder_name：要删除的文件夹名称

        【返回值】
        (成功标志, 消息) 元组

        【注意】
        不能删除收件箱（INBOX）
        """
        if not self.connection:
            return False, "未连接到服务器"

        if folder_name.upper() == "INBOX":
            return False, "不能删除收件箱"

        try:
            # 获取原始文件夹名称
            raw_name = self.get_raw_folder_name(folder_name)
            # 删除文件夹
            self.connection.delete(raw_name)
            # 从映射中移除
            if folder_name in self.folder_map:
                del self.folder_map[folder_name]
            return True, f"文件夹 '{folder_name}' 删除成功"
        except Exception as e:
            return False, f"删除失败: {str(e)}"

    def rename_folder(self, old_name: str, new_name: str) -> Tuple[bool, str]:
        """
        重命名邮件夹

        【参数】
        - old_name：原文件夹名称
        - new_name：新文件夹名称

        【返回值】
        (成功标志, 消息) 元组

        【注意】
        不能重命名收件箱
        """
        if not self.connection:
            return False, "未连接到服务器"

        if old_name.upper() == "INBOX":
            return False, "不能重命名收件箱"

        try:
            # 获取原始名称并编码新名称
            raw_old = self.get_raw_folder_name(old_name)
            raw_new = imap_utf7_encode(new_name)
            # 执行重命名
            self.connection.rename(raw_old, raw_new)
            # 更新映射
            if old_name in self.folder_map:
                del self.folder_map[old_name]
            self.folder_map[new_name] = raw_new
            return True, f"文件夹已重命名为 '{new_name}'"
        except Exception as e:
            return False, f"重命名失败: {str(e)}"

    def fetch_emails(self, folder: str = "INBOX", limit: int = 50) -> List[Email]:
        """
        获取邮件列表

        【参数】
        - folder：文件夹名称，默认是收件箱
        - limit：最多获取多少封邮件

        【返回值】
        邮件对象列表，按时间倒序排列（最新的在前）
        """
        emails = []

        if not self.connection:
            return emails

        try:
            # 记录当前文件夹
            self.current_folder = folder

            # 选择文件夹
            raw_folder = self.get_raw_folder_name(folder)
            self.connection.select(raw_folder)

            # 搜索所有邮件
            _, message_numbers = self.connection.search(None, "ALL")

            if not message_numbers[0]:
                return emails

            # 获取邮件编号列表
            nums = message_numbers[0].split()

            # 只取最新的 limit 封
            nums = nums[-limit:] if len(nums) > limit else nums

            # 倒序，最新的在前
            nums.reverse()

            # 逐个获取邮件
            for num in nums:
                try:
                    # 获取完整邮件（RFC822 格式）
                    _, msg_data = self.connection.fetch(num, "(RFC822)")

                    if msg_data[0] is None:
                        continue

                    # 解析邮件
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # 解析各个字段
                    sender_addr, sender_name = self._parse_sender(msg.get("From", ""))
                    subject = self._decode_str(msg.get("Subject", "无主题"))
                    recipient = self._decode_str(msg.get("To", ""))
                    content, attachments = self._get_email_content(msg)

                    # 解析日期
                    date_str = msg.get("Date", "")
                    try:
                        date = parsedate_to_datetime(date_str)
                    except:
                        date = datetime.now()

                    # 创建邮件对象
                    email_obj = Email(
                        uid=num.decode() if isinstance(num, bytes) else str(num),
                        sender=sender_addr,
                        sender_name=sender_name,
                        recipient=recipient,
                        subject=subject,
                        content=content,
                        date=date,
                        folder=folder,
                        attachments=attachments
                    )
                    emails.append(email_obj)

                except Exception as e:
                    print(f"解析邮件失败: {e}")
                    continue

        except Exception as e:
            print(f"获取邮件列表失败: {e}")

        return emails

    def move_email(self, uid: str, target_folder: str) -> Tuple[bool, str]:
        """
        移动邮件到指定文件夹

        【IMAP 移动邮件的原理】
        IMAP 没有直接的移动命令，需要：
        1. 复制邮件到目标文件夹
        2. 标记原邮件为删除
        3. 执行 expunge 真正删除原邮件

        【参数】
        - uid：邮件的 UID
        - target_folder：目标文件夹名称

        【返回值】
        (成功标志, 消息) 元组
        """
        if not self.connection:
            return False, "未连接到服务器"

        try:
            # 选择当前文件夹
            raw_current = self.get_raw_folder_name(self.current_folder)
            raw_target = self.get_raw_folder_name(target_folder)
            self.connection.select(raw_current)

            # 复制邮件到目标文件夹
            self.connection.copy(uid.encode(), raw_target)

            # 标记原邮件为删除
            self.connection.store(uid.encode(), '+FLAGS', '\\Deleted')

            # 真正删除（expunge）
            self.connection.expunge()

            return True, "移动成功"
        except Exception as e:
            return False, f"移动失败: {str(e)}"

    def delete_email(self, uid: str) -> Tuple[bool, str]:
        """
        删除邮件

        【参数】
        uid：邮件的 UID

        【返回值】
        (成功标志, 消息) 元组
        """
        if not self.connection:
            return False, "未连接到服务器"

        try:
            # 选择当前文件夹
            raw_folder = self.get_raw_folder_name(self.current_folder)
            self.connection.select(raw_folder)

            # 标记为删除
            self.connection.store(uid.encode(), '+FLAGS', '\\Deleted')

            # 真正删除
            self.connection.expunge()

            return True, "删除成功"
        except Exception as e:
            return False, f"删除失败: {str(e)}"

    def mark_as_read(self, uid: str) -> bool:
        """
        标记邮件为已读

        【参数】
        uid：邮件的 UID

        【返回值】
        是否成功
        """
        if not self.connection:
            return False

        try:
            # 选择当前文件夹
            raw_folder = self.get_raw_folder_name(self.current_folder)
            self.connection.select(raw_folder)

            # 添加 \Seen 标志（已读标志）
            self.connection.store(uid.encode(), '+FLAGS', '\\Seen')

            return True
        except:
            return False
