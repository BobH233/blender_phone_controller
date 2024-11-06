import json
import threading
import queue
from wsgiref.simple_server import make_server
from ws4py.websocket import WebSocket as _WebSocket
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication

from .callbacks import cmd_callbacks

wsserver = None
sockets = []
message_queue = queue.Queue()

class WebSocketApp(_WebSocket):
    def opened(self):
        sockets.append(self)
        
    def closed(self, code, reason=None):
        sockets.remove(self)
        
    def received_message(self, message):
        message_queue.put(message.data.decode(message.encoding))

def get_wsserver():
    global wsserver
    return wsserver

def start_server(host, port):
    global wsserver
    if wsserver:
        return False
    wsserver = make_server(host, port,
        server_class=WSGIServer,
        handler_class=WebSocketWSGIRequestHandler,
        app=WebSocketWSGIApplication(handler_cls=WebSocketApp)
    )
    wsserver.initialize_websockets_manager()
    wsserver_thread = threading.Thread(target=wsserver.serve_forever)
    wsserver_thread.daemon = True
    wsserver_thread.start()
    return True

def stop_server():
    global wsserver
    if not wsserver:
        return False
    wsserver.shutdown()
    for socket in sockets:
        socket.close()
    wsserver = None
    return True

def parse_message_json(message):
    ret = json.loads(message)
    if ret.get('cmd') is None:
        raise Exception('No cmd in json')
    if ret.get('param') is None:
        raise Exception('No param in json')
    return ret

def dispatch_cmd(msg_obj):
    callback = cmd_callbacks.get(msg_obj['cmd'])
    if callback:
        callback(msg_obj)
    else:
        raise Exception(f'No callback for cmd {msg_obj["cmd"]}')

def update_timer():
    msg_map = {}
    while not message_queue.empty():
        try:
            msg = message_queue.get()
            msg_obj = parse_message_json(msg)
            msg_map[msg_obj['cmd']] = msg_obj
        except Exception as e:
            print('message parse error', e)
    for msg_obj in msg_map.values():
        dispatch_cmd(msg_obj)
    return 0.01