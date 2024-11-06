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

    def camera_control_sub_panel(self, context, layout):
        row = layout.row()
        row.label(text='摄像机控制')

    def armature_control_sub_panel(self, context, layout):
        row = layout.row()
        row.label(text='骨骼控制')
    
    def object_control_sub_panel(self, context, layout):
        row = layout.row()
        row.label(text='物体控制')
    
    def server_setting_sub_panel(self, context, layout):
        qr_icon_preview = get_qr_icon_preview()
        scene = context.scene

        row = layout.row()
        row.prop(scene, 'default_ws_ip')
        row = layout.row()
        row.prop(scene, 'default_ws_port')
        row = layout.row()
        row.operator('bobh.start_websocket_server', text='启动WS服务')
        row = layout.row()
        row.operator('bobh.stop_websocket_server', text='关闭WS服务')
        row = layout.row()
        row.prop(scene, 'default_web_port')
        row = layout.row()
        row.operator('bobh.start_webui_server', text='启动Web服务')
        row = layout.row()
        row.operator('bobh.stop_webui_server', text='关闭Web服务')
        if qr_icon_preview.get('qr_image'):
            row = layout.row()
            row.label(text='扫描二维码:')
            row = layout.row()
            row.template_icon(icon_value=qr_icon_preview['qr_image'].icon_id, scale=6)

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        row = box.row()
        row.label(text='服务器设置', icon='SHADING_WIRE')
        self.server_setting_sub_panel(context, box)


        box = layout.box()
        row = box.row()
        row.label(text='工作模式设定', icon='TOOL_SETTINGS')
        row = box.row()
        row.prop(scene, 'work_mode_option', expand=True)

        if scene.work_mode_option == 'CameraMode':
            self.camera_control_sub_panel(context, box)
        elif scene.work_mode_option == 'ObjectMode':
            self.object_control_sub_panel(context, box)
        elif scene.work_mode_option == 'ArmatureMode':
            self.armature_control_sub_panel(context, box)