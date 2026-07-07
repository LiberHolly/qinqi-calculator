@echo off
chcp 65001 >nul
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3 并加入 PATH。
    pause
    exit /b 1
)

python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败。
        pause
        exit /b 1
    )
)

python main.py
if errorlevel 1 (
    echo.
    echo [错误] 程序启动失败，请查看上方报错信息。
    pause
    exit /b 1
)
