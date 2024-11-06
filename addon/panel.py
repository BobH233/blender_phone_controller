try:
    import bpy
except Exception as e:
    print('Warning: Not in blender env!')
from .operators import get_qr_icon_preview

class BOBH_PT_main_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    bl_category = 'BobHTool'
    bl_label = 'PhoneController'
    bl_idname = 'BOBH_PT_blender_phone_controller'

    def draw(self, context):
        qr_icon_preview = get_qr_icon_preview()
        layout = self.layout
        scene = context.scene

        box = layout.box()
        row = box.row()
        row.label(text='服务器设置', icon='SHADING_WIRE')
        row = box.row()
        row.prop(scene, "default_ws_ip")
        row = box.row()
        row.prop(scene, "default_ws_port")
        row = box.row()
        row.operator('bobh.start_websocket_server', text='启动WS服务')
        row = box.row()
        row.operator('bobh.stop_websocket_server', text='关闭WS服务')
        row = box.row()
        row.prop(scene, "default_web_port")
        row = box.row()
        row.operator('bobh.start_webui_server', text='启动Web服务')
        row = box.row()
        row.operator('bobh.stop_webui_server', text='关闭Web服务')
        if qr_icon_preview.get('qr_image'):
            row = box.row()
            row.label(text="扫描二维码:")
            row = box.row()
            row.template_icon(icon_value=qr_icon_preview['qr_image'].icon_id, scale=6)