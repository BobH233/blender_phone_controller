try:
    import bpy
except Exception as e:
    print('Warning: Not in blender env!')
from .operators import get_qr_icon_preview
from .server import get_current_latency_avg
from .camera_control import get_controlling_camera, get_cache_dequeue_size

class BOBH_PT_main_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    bl_category = 'BobHTool'
    bl_label = 'PhoneController'
    bl_idname = 'BOBH_PT_blender_phone_controller'

    def camera_control_sub_panel(self, context, layout):
        scene = context.scene

        row = layout.row()
        row.label(text='请举起手机，然后按下快捷键或者点击下面按钮开始控制')
        row = layout.row()
        
        selected_objects = bpy.context.selected_objects
        controlling_camera = get_controlling_camera()
        if len(selected_objects) == 1 and selected_objects[0].type == 'CAMERA':
            row.label(text=f'当前控制摄像机: {selected_objects[0].name}', icon='OUTLINER_OB_CAMERA')
        elif controlling_camera:
            row.label(text=f'当前控制摄像机: {controlling_camera.name}', icon='OUTLINER_OB_CAMERA')
        else:
            row.label(text=f'没有选中受控摄像机', icon='OUTLINER_OB_CAMERA')

        row = layout.row()
        row.operator('bobh.start_camera_control', text='开始控制摄像机')
        row.operator('bobh.stop_camera_control', text='停止控制摄像机')
        row = layout.row()
        row.operator('bobh.reset_camera_pose', text='重置摄像机姿态')
        row = layout.row()
        row.prop(scene, 'record_camera_keyframe', text='录制摄像机关键帧', toggle=True, icon='DECORATE_KEYFRAME')
        row = layout.row()
        row.prop(scene, 'camera_control_orient', expand=False)
        row = layout.row()
        row.prop(scene, "use_stabilizer_smoothing", toggle=True, icon='SURFACE_NCIRCLE')
        if bpy.context.scene.use_stabilizer_smoothing:
            row = layout.row()
            row.prop(scene, "stabilizer_smoothing_strength")


    def armature_control_sub_panel(self, context, layout):
        row = layout.row()
        row.label(text='骨骼控制')
    
    def object_control_sub_panel(self, context, layout):
        row = layout.row()
        row.label(text='物体控制')
    
    def server_setting_sub_panel(self, context, layout):
        scene = context.scene

        row = layout.row()
        row.prop(scene, 'default_ws_ip')
        row = layout.row()
        row.prop(scene, 'default_ws_port')
        row = layout.row()
        row.operator('bobh.start_websocket_server', text='启动WS服务')
        row = layout.row()
        row.operator('bobh.stop_websocket_server', text='关闭WS服务')

    def control_input_web_sub_panel(self, context, layout):
        qr_icon_preview = get_qr_icon_preview()
        scene = context.scene


        row = layout.row()
        row.label(text='注意: 网页端不要多台设备连接, 只支持单设备', icon='ERROR')
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

    def control_input_app_sub_panel(self, context, layout):
        row = layout.row()
        row.label(text='app设定正在开发...')

    def control_input_joystick_sub_panel(self, context, layout):
        row = layout.row()
        row.label(text='手柄设定正在开发...')

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        row = box.row()
        row.label(text='根服务器设置', icon='SHADING_WIRE')
        self.server_setting_sub_panel(context, box)
        row = box.row()
        row.label(text=f'通信时间偏差: {get_current_latency_avg():.2f}ms', icon='TIME')
        row = box.row()
        row.label(text=f'姿态缓存队列大小: {get_cache_dequeue_size()}', icon='COLLAPSEMENU')

        box = layout.box()
        row = box.row()
        row.label(text='控制输入设定', icon='FRAME_NEXT')
        row = box.row()
        row.prop(scene, 'input_control_option', expand=True)

        if scene.input_control_option == 'WebSetting':
            self.control_input_web_sub_panel(context, box)
        elif scene.input_control_option == 'AppSetting':
            self.control_input_app_sub_panel(context, box)
        elif scene.input_control_option == 'JoystickSetting':
            self.control_input_joystick_sub_panel(context, box)

        box = layout.box()
        row = box.row()
        row.label(text='控制输出设定', icon='TOOL_SETTINGS')
        row = box.row()
        row.prop(scene, 'work_mode_option', expand=True)

        if scene.work_mode_option == 'CameraMode':
            self.camera_control_sub_panel(context, box)
        elif scene.work_mode_option == 'ObjectMode':
            self.object_control_sub_panel(context, box)
        elif scene.work_mode_option == 'ArmatureMode':
            self.armature_control_sub_panel(context, box)