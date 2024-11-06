from flask import Flask, send_from_directory, render_template_string, request
import multiprocessing
import time
import os

multiprocessing.set_start_method("spawn", force=True)

app = Flask(__name__, static_folder='../webui', template_folder='../webui')

# 定义 index 路由
@app.route('/')
def index():
    index_path = os.path.join(os.path.dirname(__file__), '../webui/index.html')
    return render_template_string(open(index_path, encoding="utf-8").read())

# 用于处理静态文件 (JS, CSS)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

server_process = None
server_port = None

def is_running():
    global server_process
    if server_process is None:
        return False
    alive = server_process.is_alive()
    if not alive:
        server_process = None
    return alive

def get_server_thread():
    global server_process
    return server_process

def webui_thread(port):
    app.run(host='0.0.0.0', port=port)

def start_server(port):
    global server_process, server_port
    if server_process:
        return False
    server_process = multiprocessing.Process(target=webui_thread, args=(port,))
    server_process.start()
    time.sleep(1)
    return True

def stop_server():
    global server_process, server_port
    if server_process is None:
        return False
    server_process.terminate()
    server_process.join()
    server_process = None
    return True
    