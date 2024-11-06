import subprocess
import sys

# 检查 websocket-client 是否已经安装
try:
    import ws4py
    import flask
    import qrcode
    import PIL
except ImportError:
    # 如果没有安装，则安装
    python_executable = sys.executable
    subprocess.check_call([python_executable, "-m", "ensurepip"])
    subprocess.check_call([python_executable, "-m", "pip", "install", "ws4py", '-i', 'https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple'])
    subprocess.check_call([python_executable, "-m", "pip", "install", "flask", '-i', 'https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple'])
    subprocess.check_call([python_executable, "-m", "pip", "install", "requests", '-i', 'https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple'])
    subprocess.check_call([python_executable, "-m", "pip", "install", "qrcode", '-i', 'https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple'])
    subprocess.check_call([python_executable, "-m", "pip", "install", "pillow", '-i', 'https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple'])
    
# 再次导入确认安装成功
try:
    import ws4py
    import flask
    import requests
    import qrcode
    import PIL
    print("依赖项已安装成功")
except ImportError:
    print("依赖项安装失败，检查控制台报错!")
