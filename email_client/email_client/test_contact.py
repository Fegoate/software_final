"""测试通信簿"""
import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("正在导入模块...")
    from ui.contact_dialog import ContactManagerDialog
    from PyQt5.QtWidgets import QApplication
    print("导入成功")

    app = QApplication([])
    print("创建对话框...")
    dialog = ContactManagerDialog()
    print("通信簿对话框创建成功！")
    dialog.show()
    app.exec_()
except Exception as e:
    print(f"错误: {e}")
    traceback.print_exc()
    input("按回车键退出...")
