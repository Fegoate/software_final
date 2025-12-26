"""测试创建中文文件夹"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import Settings
from core.email_receiver import EmailReceiver, imap_utf7_encode

# 测试编码
test_name = "测试文件夹"
encoded = imap_utf7_encode(test_name)
print(f"编码测试: '{test_name}' -> '{encoded}'")

settings = Settings()
account = settings.load_account()

if not account:
    print("没有保存的账户配置")
    sys.exit()

receiver = EmailReceiver(account)
success, msg = receiver.connect()

if success:
    print("登录成功\n")

    # 尝试创建中文文件夹
    folder_name = "测试文件夹"
    print(f"尝试创建文件夹: {folder_name}")

    success, msg = receiver.create_folder(folder_name)
    print(f"结果: {success}, {msg}")

    if success:
        # 刷新文件夹列表
        folders = receiver.get_folders()
        print(f"\n当前文件夹列表: {folders}")

    receiver.disconnect()
else:
    print(f"登录失败: {msg}")

input("\n按回车退出...")
