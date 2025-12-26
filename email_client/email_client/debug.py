"""调试脚本 - 检查通信簿问题"""
import sys
import os
import traceback

# 设置路径
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

print(f"项目目录: {project_dir}")
print(f"Python路径: {sys.path[:3]}")
print()

try:
    print("1. 导入 Contact 模型...")
    from models.email_model import Contact
    print("   成功!")

    print("2. 导入 ContactManager...")
    from core.contact_manager import ContactManager
    print("   成功!")

    print("3. 创建 ContactManager 实例...")
    cm = ContactManager()
    print(f"   成功! 联系人数量: {len(cm.contacts)}")

    print("4. 导入 PyQt5...")
    from PyQt5.QtWidgets import QApplication, QDialog
    print("   成功!")

    print("5. 导入 ContactManagerDialog...")
    from ui.contact_dialog import ContactManagerDialog
    print("   成功!")

    print("6. 创建 QApplication...")
    app = QApplication([])
    print("   成功!")

    print("7. 创建 ContactManagerDialog...")
    dialog = ContactManagerDialog()
    print("   成功!")

    print()
    print("="*40)
    print("所有测试通过! 正在打开通信簿...")
    print("="*40)

    dialog.show()
    app.exec_()

except Exception as e:
    print()
    print("="*40)
    print(f"错误: {e}")
    print("="*40)
    print()
    traceback.print_exc()

input("\n按回车键退出...")
