try:
    import bpy
except Exception as e:
    print('Warning: Not in blender env!')
from .server import start_server as start_ws_server, stop_server as stop_ws_server
from .utils import show_message_box, get_local_ip, generate_qr_code
from .server import get_wsserver
from .webui import start_server as start_web_server, stop_server as stop_web_server, is_running

class BOBH_OT_start_websocket_server(bpy.types.Operator):
    bl_label = '启动Websocket服务'
    bl_idname = 'bobh.start_websocket_server'

    default_ip = '0.0.0.0'
    default_port = 8867

    @classmethod
    def poll(cls, context):
        return get_wsserver() is None

    def execute(self, context):
        self.default_ip = context.scene.default_ws_ip
        self.default_port = int(context.scene.default_ws_port)

        if not start_ws_server(self.default_ip, self.default_port):
            show_message_box(message='服务器已经启动', title='错误', icon='ERROR')
            return {'CANCELLED'}
        show_message_box(message=f'服务器启动成功({self.default_ip}:{self.default_port})', title='信息', icon='INFO')
        return {'FINISHED'}

class BOBH_OT_stop_websocket_server(bpy.types.Operator):
    bl_label = '结束Websocket服务'
    bl_idname = 'bobh.stop_websocket_server'

    @classmethod
    def poll(cls, context):
        return get_wsserver() is not None

    def execute(self, context):
        if not stop_ws_server():
            show_message_box(message='服务器已经关闭', title='错误', icon='ERROR')
            return {'CANCELLED'}
        show_message_box(message='服务器关闭成功', title='信息', icon='INFO')
        return {'FINISHED'}

qr_icon_preview = bpy.utils.previews.new()

def get_qr_icon_preview():
    return qr_icon_preview

class BOBH_OT_start_webui_server(bpy.types.Operator):
    bl_label = '启动WebUI服务'
    bl_idname = 'bobh.start_webui_server'

    default_port = 8863

    @classmethod
    def poll(cls, context):
        return not is_running()

    def execute(self, context):
        global qr_icon_preview
        self.default_port = context.scene.default_web_port
        if not start_web_server(self.default_port):
            show_message_box(message='服务器已经启动', title='错误', icon='ERROR')
            return {'CANCELLED'}
        locip = get_local_ip()
        url = f"http://{locip}:{self.default_port}"
        qr_path = generate_qr_code(url)
        qr_icon_preview.clear()
        qr_icon_preview.load('qr_image', qr_path, 'IMAGE')
        show_message_box(message=f'服务器启动成功({url})', title='信息', icon='INFO')
        return {'FINISHED'}

class BOBH_OT_stop_webui_server(bpy.types.Operator):
    bl_label = '结束WebUI服务'
    bl_idname = 'bobh.stop_webui_server'

    @classmethod
    def poll(cls, context):
        return is_running()

    def execute(self, context):
        global qr_icon_preview
        if not stop_web_server():
            show_message_box(message='服务器已经关闭', title='错误', icon='ERROR')
            return {'CANCELLED'}
        show_message_box(message='服务器关闭成功', title='信息', icon='INFO')
        qr_icon_preview.clear()
        return {'FINISHED'}