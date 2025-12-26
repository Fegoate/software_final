"""
================================================================================
SMTP 邮件发送模块 - 负责发送邮件
================================================================================

【文件作用】
这个文件负责发送邮件，主要功能：
1. 连接到 SMTP 服务器
2. 发送普通邮件
3. 发送带附件的邮件
4. 支持多收件人、抄送、密送
5. 转发邮件

【什么是 SMTP】
SMTP（Simple Mail Transfer Protocol，简单邮件传输协议）是用于发送邮件的标准协议。
就像是邮局的发信窗口，你把信（邮件）交给它，它帮你送到收件人手中。

【发送邮件的基本流程】
1. 连接到 SMTP 服务器（如 smtp.qq.com）
2. 登录验证（使用邮箱地址和密码/授权码）
3. 构建邮件（包括发件人、收件人、主题、正文、附件等）
4. 发送邮件
5. 断开连接

【关于 MIME】
MIME（Multipurpose Internet Mail Extensions）是邮件的格式标准。
它允许邮件包含多种类型的内容，如文本、图片、附件等。
================================================================================
"""

# ============================================================================
# 导入必要的模块
# ============================================================================

# smtplib：Python 内置的 SMTP 协议库，用于发送邮件
import smtplib

# os 模块：用于文件操作，如获取文件名、检查文件是否存在
import os

# mimetypes：用于猜测文件的 MIME 类型
# 比如 .jpg 文件的 MIME 类型是 image/jpeg
import mimetypes

# MIMEText：用于创建纯文本邮件内容
from email.mime.text import MIMEText

# MIMEMultipart：用于创建包含多个部分的邮件（如正文+附件）
from email.mime.multipart import MIMEMultipart

# MIMEBase：用于创建附件的基类
from email.mime.base import MIMEBase

# Header：用于处理邮件头的编码（支持中文等非 ASCII 字符）
from email.header import Header

# encoders：用于编码附件内容
from email import encoders

# 类型提示
from typing import Tuple, Optional, List

# sys 和 os：用于设置模块路径
import sys
import os

# 将项目根目录添加到模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入邮箱账户数据类
from models.email_model import EmailAccount


# ============================================================================
# 邮件发送器类
# ============================================================================
class EmailSender:
    """
    SMTP 邮件发送器类

    【主要功能】
    1. connect()：测试与 SMTP 服务器的连接
    2. send_email()：发送邮件（支持附件、抄送、密送）
    3. forward_email()：转发邮件

    【使用示例】
    # 创建发送器
    sender = EmailSender(account)

    # 测试连接
    success, message = sender.connect()

    # 发送邮件
    success, message = sender.send_email(
        to="recipient@example.com",
        subject="测试邮件",
        content="这是邮件内容"
    )
    """

    def __init__(self, account: EmailAccount):
        """
        初始化邮件发送器

        【参数】
        account：邮箱账户配置对象，包含服务器信息和登录凭证
        """
        # 保存账户配置
        self.account = account

    def _create_connection(self) -> Tuple[Optional[smtplib.SMTP], str]:
        """
        创建与 SMTP 服务器的连接

        【私有方法说明】
        方法名以下划线开头表示这是私有方法，只在类内部使用。

        【返回值】
        返回一个元组 (connection, message)：
        - connection：连接对象，如果连接失败则为 None
        - message：状态消息

        【SSL 和 STARTTLS 的区别】
        - SSL（端口 465）：直接建立加密连接
        - STARTTLS（端口 587）：先建立普通连接，再升级为加密连接
        """
        try:
            # 判断使用哪种加密方式
            if self.account.use_ssl and self.account.smtp_port == 465:
                # 使用 SSL 加密（端口 465）
                # SMTP_SSL 类会自动建立 SSL 加密连接
                connection = smtplib.SMTP_SSL(
                    self.account.smtp_server,  # SMTP 服务器地址
                    self.account.smtp_port,    # SMTP 端口
                    timeout=30                  # 超时时间（秒）
                )
            else:
                # 使用 STARTTLS 加密（端口 587）或不加密
                connection = smtplib.SMTP(
                    self.account.smtp_server,
                    self.account.smtp_port,
                    timeout=30
                )
                # 如果需要 SSL，升级连接
                if self.account.use_ssl:
                    # starttls() 将普通连接升级为加密连接
                    connection.starttls()

            # 登录 SMTP 服务器
            # 这里使用邮箱地址和密码（或授权码）进行身份验证
            connection.login(self.account.email, self.account.password)

            return connection, "连接成功"

        except smtplib.SMTPAuthenticationError:
            # 登录验证失败（用户名或密码错误）
            return None, "认证失败，请检查邮箱和密码/授权码"
        except smtplib.SMTPConnectError as e:
            # 无法连接到服务器
            return None, f"连接服务器失败: {str(e)}"
        except Exception as e:
            # 其他错误
            return None, f"连接失败: {str(e)}"

    def connect(self) -> Tuple[bool, str]:
        """
        测试与 SMTP 服务器的连接

        【用途】
        在登录时用于验证账户配置是否正确。

        【返回值】
        - (True, "连接成功")：连接测试通过
        - (False, 错误信息)：连接失败
        """
        # 尝试创建连接
        conn, msg = self._create_connection()

        if conn:
            try:
                # 连接成功后立即关闭
                # quit() 方法会发送 QUIT 命令并关闭连接
                conn.quit()
            except:
                pass
            return True, msg

        return False, msg

    def disconnect(self):
        """
        断开连接

        【说明】
        由于每次发送邮件都会创建新连接，这个方法实际上不需要做任何事情。
        保留这个方法是为了与 EmailReceiver 类的接口保持一致。
        """
        pass

    def send_email(self, to: str, subject: str, content: str,
                   attachments: List[str] = None,
                   cc: str = "",
                   bcc: str = "",
                   is_forward: bool = False,
                   original_sender: str = "") -> Tuple[bool, str]:
        """
        发送邮件

        【参数说明】
        - to：收件人邮箱地址（多个收件人用逗号或分号分隔）
              例如："user1@qq.com, user2@163.com"
        - subject：邮件主题
        - content：邮件正文内容
        - attachments：附件文件路径列表，例如 ["C:/文档/报告.pdf"]
        - cc：抄送收件人（多个用逗号或分号分隔）
              抄送的人可以看到邮件，也能看到其他收件人
        - bcc：密送收件人（多个用逗号或分号分隔）
               密送的人可以看到邮件，但其他收件人看不到他们
        - is_forward：是否是转发邮件
        - original_sender：原始发件人（转发时使用）

        【返回值】
        - (True, "发送成功")：邮件发送成功
        - (False, 错误信息)：发送失败
        """

        # 创建连接
        connection, conn_msg = self._create_connection()
        if not connection:
            return False, conn_msg

        try:
            # ------------------------------------------------------------------
            # 构建邮件
            # ------------------------------------------------------------------

            # 创建一个支持多部分内容的邮件对象
            # MIMEMultipart 可以同时包含正文和附件
            msg = MIMEMultipart()

            # 设置发件人
            msg['From'] = self.account.email

            # 设置收件人
            msg['To'] = to

            # 设置主题
            # 使用 Header 类来处理中文主题，确保正确编码
            msg['Subject'] = Header(subject, 'utf-8')

            # 设置抄送（如果有）
            if cc:
                msg['Cc'] = cc

            # 设置密送（如果有）
            # 注意：密送地址不会出现在邮件头中，但需要在发送时包含
            if bcc:
                msg['Bcc'] = bcc

            # ------------------------------------------------------------------
            # 处理转发邮件
            # ------------------------------------------------------------------
            if is_forward and original_sender:
                # 在转发的邮件前添加转发标记
                forward_header = f"\n\n---------- 转发的邮件 ----------\n原始发件人: {original_sender}\n\n"
                content = forward_header + content

            # ------------------------------------------------------------------
            # 添加邮件正文
            # ------------------------------------------------------------------
            # MIMEText 用于创建文本内容
            # 'plain' 表示纯文本格式，'utf-8' 是字符编码
            msg.attach(MIMEText(content, 'plain', 'utf-8'))

            # ------------------------------------------------------------------
            # 添加附件
            # ------------------------------------------------------------------
            if attachments:
                for file_path in attachments:
                    # 检查文件是否存在
                    if os.path.exists(file_path):
                        # 调用私有方法添加附件
                        self._attach_file(msg, file_path)

            # ------------------------------------------------------------------
            # 发送邮件
            # ------------------------------------------------------------------

            # 解析所有收件人（包括收件人、抄送、密送）
            all_recipients = self._parse_recipients(to, cc, bcc)

            # 发送邮件
            # sendmail 方法参数：发件人、收件人列表、邮件内容
            connection.sendmail(
                self.account.email,      # 发件人
                all_recipients,          # 所有收件人（列表）
                msg.as_string()          # 邮件内容（转换为字符串）
            )

            return True, "发送成功"

        except smtplib.SMTPRecipientsRefused:
            # 收件人地址被拒绝（可能是无效的邮箱地址）
            return False, "收件人地址无效"
        except smtplib.SMTPDataError as e:
            # 邮件数据错误（可能是内容被服务器拒绝）
            return False, f"邮件被拒绝: {str(e)}"
        except smtplib.SMTPException as e:
            # 其他 SMTP 错误
            return False, f"发送失败: {str(e)}"
        except Exception as e:
            # 其他未知错误
            return False, f"发送失败: {str(e)}"
        finally:
            # finally 块中的代码无论成功还是失败都会执行
            # 确保关闭连接，释放资源
            try:
                connection.quit()
            except:
                pass

    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """
        添加附件到邮件

        【参数】
        - msg：邮件对象
        - file_path：附件文件的完整路径

        【处理步骤】
        1. 获取文件名
        2. 猜测文件的 MIME 类型
        3. 读取文件内容
        4. 创建附件对象
        5. 编码附件内容（Base64 编码）
        6. 设置附件头信息
        7. 将附件添加到邮件
        """

        # 获取文件名（不含路径）
        # 例如：C:/文档/报告.pdf -> 报告.pdf
        filename = os.path.basename(file_path)

        # 猜测文件的 MIME 类型
        # 例如：.pdf -> application/pdf，.jpg -> image/jpeg
        content_type, encoding = mimetypes.guess_type(file_path)

        # 如果无法猜测类型，使用通用的二进制流类型
        if content_type is None:
            content_type = 'application/octet-stream'

        # 分离主类型和子类型
        # 例如：application/pdf -> main_type='application', sub_type='pdf'
        main_type, sub_type = content_type.split('/', 1)

        # 读取文件内容（二进制模式）
        with open(file_path, 'rb') as f:
            file_data = f.read()

        # 创建附件对象
        attachment = MIMEBase(main_type, sub_type)

        # 设置附件内容
        attachment.set_payload(file_data)

        # 对附件内容进行 Base64 编码
        # 这是为了确保二进制数据可以通过邮件传输
        encoders.encode_base64(attachment)

        # 设置附件头，告诉邮件客户端这是一个附件
        # Content-Disposition: attachment 表示这是附件
        # filename 指定附件的文件名
        attachment.add_header(
            'Content-Disposition',
            'attachment',
            filename=('utf-8', '', filename)  # 使用 UTF-8 编码文件名（支持中文）
        )

        # 将附件添加到邮件
        msg.attach(attachment)

    def _parse_recipients(self, to: str, cc: str = "", bcc: str = "") -> List[str]:
        """
        解析所有收件人地址

        【参数】
        - to：收件人
        - cc：抄送
        - bcc：密送

        【返回值】
        所有收件人的邮箱地址列表

        【支持的格式】
        - 单个地址：user@example.com
        - 多个地址（逗号分隔）：user1@qq.com, user2@163.com
        - 多个地址（分号分隔）：user1@qq.com; user2@163.com
        - 带名称的地址：张三 <zhangsan@qq.com>
        """
        recipients = []

        # 遍历所有地址字段
        for addr_str in [to, cc, bcc]:
            if addr_str:
                # 将分号替换为逗号，统一分隔符
                addr_str = addr_str.replace(';', ',')

                # 按逗号分割，获取每个地址
                for addr in addr_str.split(','):
                    # 去除前后空白
                    addr = addr.strip()

                    # 检查是否是有效的邮箱地址
                    if addr and '@' in addr:
                        # 如果地址包含尖括号，提取其中的邮箱地址
                        # 例如：张三 <zhangsan@qq.com> -> zhangsan@qq.com
                        if '<' in addr and '>' in addr:
                            addr = addr.split('<')[1].split('>')[0]
                        recipients.append(addr)

        return recipients

    def forward_email(self, to: str, original_subject: str,
                      original_content: str, original_sender: str,
                      attachments: List[str] = None) -> Tuple[bool, str]:
        """
        转发邮件

        【参数】
        - to：转发给谁
        - original_subject：原邮件主题
        - original_content：原邮件内容
        - original_sender：原发件人
        - attachments：附件列表

        【返回值】
        - (True, "发送成功")：转发成功
        - (False, 错误信息)：转发失败
        """

        # 在主题前添加 "Fwd:" 标记
        subject = f"Fwd: {original_subject}"

        # 调用发送邮件方法，设置 is_forward=True
        return self.send_email(
            to=to,
            subject=subject,
            content=original_content,
            attachments=attachments,
            is_forward=True,
            original_sender=original_sender
        )
