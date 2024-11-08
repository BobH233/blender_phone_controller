import json
import threading
import queue
import bpy
import time
from collections import deque

from wsgiref.simple_server import make_server
from ws4py.websocket import WebSocket as _WebSocket
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication

from .callbacks import cmd_callbacks

wsserver = None
sockets = []
message_queue = queue.Queue()

latency_queue = deque(maxlen=20)
current_latency_avg = 0

class WebSocketApp(_WebSocket):
    def opened(self):
        sockets.append(self)
        
    def closed(self, code, reason=None):
        sockets.remove(self)
        
    def received_message(self, message):
        global latency_queue, current_latency_avg
        payload = parse_message_json(message.data.decode(message.encoding))
        timestamp = payload.get('timestamp')
        if timestamp:
            message_queue.put(payload)
            current_latency = int(time.time() * 1000) - timestamp
            latency_queue.append(current_latency)
            current_latency_avg = 1.0 * sum(latency_queue) / len(latency_queue)

def get_current_latency_avg():
    return current_latency_avg

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
    try:
        bpy.app.timers.unregister(update_timer)
    except:
        pass
    bpy.app.timers.register(update_timer)
    return True

def stop_server():
    global wsserver
    if not wsserver:
        return False
    wsserver.shutdown()
    for socket in sockets:
        socket.close()
    wsserver = None
    try:
        bpy.app.timers.unregister(update_timer)
    except:
        pass
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
            msg_map[msg['cmd']] = msg
        except Exception as e:
            print('message parse error', e)
    for msg_obj in msg_map.values():
        dispatch_cmd(msg_obj)
    return 0.01