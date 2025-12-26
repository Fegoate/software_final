@echo off
chcp 65001 >nul
echo ========================================
echo    邮件客户端打包脚本
echo ========================================
echo.

echo [1/3] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3
    pause
    exit /b 1
)

echo.
echo [2/3] 安装依赖...
pip install PyQt5 PyInstaller -q
if errorlevel 1 (
    echo 错误: 安装依赖失败
    pause
    exit /b 1
)

echo.
echo [3/3] 打包程序...
pyinstaller --onefile --windowed --name "邮件客户端" --clean main.py
if errorlevel 1 (
    echo 错误: 打包失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo    打包完成！
echo    可执行文件位于: dist\邮件客户端.exe
echo ========================================
pause
