try:
    import bpy
except Exception as e:
    print('Warning: Not in blender env!')

import socket
import qrcode
import tempfile
import os

def show_message_box(message='', title='Message', icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def get_local_ip():
    '''获取本地 IP 地址'''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))  # Google 的公共 DNS
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def generate_qr_code(data):
    '''生成二维码并保存到临时文件中'''
    qr = qrcode.make(data)
    file_path = os.path.join(os.path.dirname(__file__), 'tmp_qr_code.png')
    qr.save(file_path)
    return file_path