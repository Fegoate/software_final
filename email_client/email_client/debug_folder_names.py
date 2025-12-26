"""调试文件夹名称"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import Settings
from core.email_receiver import EmailReceiver

settings = Settings()
account = settings.load_account()

if not account:
    print("没有保存的账户配置")
    sys.exit()

print(f"连接到: {account.imap_server}")

receiver = EmailReceiver(account)
success, msg = receiver.connect()

if success:
    print("登录成功\n")
    folders = receiver.get_folders()

    print("获取到的文件夹:")
    print("=" * 50)
    for f in folders:
        print(f"  '{f}'")

    print("\n映射测试:")
    print("=" * 50)
    FOLDER_NAME_MAP = {
        "INBOX": "收件箱",
        "Sent Messages": "已发送",
        "Deleted Messages": "已删除",
        "Drafts": "草稿箱",
        "Junk": "垃圾邮件",
        "Spam": "垃圾邮件",
        "Trash": "已删除",
        "Sent": "已发送",
    }

    for f in folders:
        display = FOLDER_NAME_MAP.get(f, f)
        if display == f:
            print(f"  '{f}' -> 未匹配，保持原样")
        else:
            print(f"  '{f}' -> '{display}'")

    receiver.disconnect()
else:
    print(f"登录失败: {msg}")

input("\n按回车退出...")
