from flask import Flask, send_from_directory, render_template_string, request
from flask_socketio import SocketIO
import multiprocessing
import time
import os
from ws4py.client.threadedclient import WebSocketClient

multiprocessing.set_start_method('spawn', force=True)

app = Flask(__name__, static_folder='../webui', template_folder='../webui')
socketio = SocketIO(app, cors_allowed_origins='*') 

ws_opened = False

class MyWebSocketClient(WebSocketClient):
    def opened(self):
        global ws_opened
        ws_opened = True
        print('Connection opened')

    def closed(self, code, reason=None):
        global ws_opened
        ws_opened = False
        print('Connection closed, Code:', code, 'Reason:', reason)

    def received_message(self, message):
        pass


# 定义 index 路由
@app.route('/')
def index():
    index_path = os.path.join(os.path.dirname(__file__), '../webui/index.html')
    return render_template_string(open(index_path, encoding='utf-8').read())

# 用于处理静态文件 (JS, CSS)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

ws_client = None

# 兼容ws无法连接的问题
@app.route('/ws_connect', methods=['POST'])
def ws_connect():
    global ws_client, ws_opened
    if ws_opened:
        return 'Already opened'
    data = request.get_json()
    port = data['port']
    ws_client = MyWebSocketClient(f'ws://127.0.0.1:{port}')
    ws_client.connect()
    return 'OK'

# 兼容ws无法连接的问题
@app.route('/ws_report', methods=['POST'])
def ws_report():
    global ws_client
    if ws_client is None:
        return 'Not connected'
    data = request.get_data().decode('utf-8')
    ws_client.send(data)
    return 'OK'

@socketio.on('json_data')
def handle_json_data(data):
    global ws_client, ws_opened
    if not ws_opened:
        return
    ws_client.send(data)

@socketio.on('connect')
def handle_connect():
    print('客户端已连接')

@socketio.on('disconnect')
def handle_disconnect():
    print('客户端已断开连接')


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
    cert_path = os.path.join(os.path.dirname(__file__), '../addon/cert')
    crt_path = os.path.join(cert_path, './myserver.crt')
    key_path = os.path.join(cert_path, './myserver.key')
    app.run(host='0.0.0.0', port=port, ssl_context=(crt_path, key_path))

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
    