"""调试文件夹列表"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import Settings
import imaplib

settings = Settings()
account = settings.load_account()

if not account:
    print("没有保存的账户配置")
    input("按回车退出...")
    sys.exit()

print(f"连接到: {account.imap_server}")

try:
    conn = imaplib.IMAP4_SSL(account.imap_server, account.imap_port)
    conn.login(account.email, account.password)
    print("登录成功")

    _, folder_list = conn.list()
    print(f"\n找到 {len(folder_list)} 个文件夹:")
    print("=" * 60)

    for i, folder_data in enumerate(folder_list):
        if folder_data:
            folder_str = folder_data.decode() if isinstance(folder_data, bytes) else str(folder_data)
            print(f"\n[{i}] 原始数据: {folder_data}")
            print(f"    解码后: {folder_str}")

            # 尝试解析
            if '"' in folder_str:
                parts = folder_str.split('"')
                print(f"    分割: {parts}")
                if len(parts) >= 4:
                    folder_name = parts[-2]
                    print(f"    提取名称: {folder_name}")

    conn.logout()
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

input("\n按回车退出...")
