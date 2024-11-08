blender_env = False
try:
    import bpy
    from .addon.server import stop_server as stop_ws_server
    from .addon.webui import stop_server as stop_web_server
    from .addon.panel import BOBH_PT_main_panel
    from .addon.operators import BOBH_OT_start_websocket_server,    BOBH_OT_stop_websocket_server, BOBH_OT_start_webui_server, BOBH_OT_stop_webui_server, BOBH_OT_start_camera_control, BOBH_OT_stop_camera_control, BOBH_OT_reset_camera_pose
    from .addon.camera_control import frame_change_handler as camera_control_frame_change_handler
    blender_env = True
except Exception as e:
    print('Warning: Not in blender env!')

bl_info = {
    'name': 'blender_phone_controller',
    'author': 'BobH',
    'version': (0, 1, 0),
    'blender': (3, 6, 0),
    'description': 'Control blender animation with your phone',
    'category': 'Import-Export'
}

def register_string_props():
    bpy.types.Scene.default_ws_ip = bpy.props.StringProperty(
        name='根服务器IP',
        description='根WebSocket服务器IP地址绑定',
        default='0.0.0.0'
    )
    bpy.types.Scene.default_ws_port = bpy.props.StringProperty(
        name='根服务器端口',
        description='根WebSocket服务器端口绑定',
        default='8867'
    )
    bpy.types.Scene.default_web_port = bpy.props.StringProperty(
        name='网页端端口',
        description='Web服务器端口绑定',
        default='8863'
    )

def unregister_string_props():
    del bpy.types.Scene.default_ws_ip
    del bpy.types.Scene.default_ws_port
    del bpy.types.Scene.default_web_port


def update_work_mode_option(self, context):
    print('当前工作模式:', bpy.context.scene.work_mode_option)

def register_enum_props():
    bpy.types.Scene.work_mode_option = bpy.props.EnumProperty(
        name='插件工作模式',
        description='选择插件的工作模式',
        items=[
            ('CameraMode', '摄像机控制', '使用移动设备控制摄像机的位姿', 'OUTLINER_OB_CAMERA', 0),
            ('ArmatureMode', '骨骼控制', '使用移动设备控制骨骼的旋转', 'OUTLINER_OB_ARMATURE', 1),
            ('ObjectMode', '物体', '使用移动设备控制骨骼的位姿', 'MATCUBE', 2),
        ],
        default='CameraMode'
    )
    bpy.types.Scene.input_control_option = bpy.props.EnumProperty(
        name='输入模式设定',
        description='设定插件的输入模式',
        items=[
            ('WebSetting', '网页端输入', '使用带陀螺仪的设备打开网页输入', 'SHADING_WIRE', 0),
            ('AppSetting', 'APP输入', '使用指定APP采集数据输入', 'TOPBAR', 1),
            ('JoystickSetting', '手柄输入', '将游戏手柄连接电脑输入', 'GHOST_ENABLED', 2),
        ],
        default='WebSetting'
    )
    bpy.types.Scene.camera_control_orient = bpy.props.EnumProperty(
        name='手机握持方向',
        description='设定手机握持的方向',
        items=[
            ('Portrait', '竖向握持', '竖向握持设备', 'SORT_DESC', 0),
            ('Landscape_1', '横向握持(正)', '横向握持设备', 'FORWARD', 1),
            ('Landscape_2', '横向握持(反)', '横向反方向握持设备', 'BACK', 2),
        ],
        default='Landscape_1'
    )
    bpy.types.Scene.record_camera_keyframe = bpy.props.BoolProperty(name="录制摄像机关键帧", default=False)
    bpy.types.Scene.relative_pose_control_camera = bpy.props.BoolProperty(name="启用相机相对位姿控制", default=True)
    bpy.types.Scene.use_stabilizer_smoothing = bpy.props.BoolProperty(
        name="摄像机稳定器",
        description="是否启用摄像机稳定器平滑处理",
        default=False
    )
    bpy.types.Scene.stabilizer_smoothing_strength = bpy.props.FloatProperty(
        name="稳定强度",
        description="值越大摄像机越稳定",
        default=0.5,
        min=0.0,
        max=1.0
    )


def unregister_enum_props():
    del bpy.types.Scene.work_mode_option
    del bpy.types.Scene.input_control_option
    del bpy.types.Scene.camera_control_orient
    del bpy.types.Scene.record_camera_keyframe
    del bpy.types.Scene.relative_pose_control_camera
    del bpy.types.Scene.use_stabilizer_smoothing
    del bpy.types.Scene.stabilizer_smoothing_strength

def register_blender_handlers():
    bpy.app.handlers.frame_change_post.append(camera_control_frame_change_handler)

def unregister_blender_handlers():
    if camera_control_frame_change_handler in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(camera_control_frame_change_handler)

if blender_env:
    my_classes = [
        BOBH_PT_main_panel,
        BOBH_OT_start_websocket_server,
        BOBH_OT_stop_websocket_server,
        BOBH_OT_start_webui_server,
        BOBH_OT_stop_webui_server,
        BOBH_OT_start_camera_control,
        BOBH_OT_stop_camera_control,
        BOBH_OT_reset_camera_pose,
    ]

def register():
    # 注册所有的 class 和属性
    for cls in my_classes:
        bpy.utils.register_class(cls)
    register_string_props()
    register_enum_props()
    register_blender_handlers()

def unregister():
    # 注销所有的 class 和属性
    for cls in my_classes:
        bpy.utils.unregister_class(cls)
    unregister_string_props()
    unregister_enum_props()
    unregister_blender_handlers()
    stop_ws_server()
    stop_web_server()

if __name__ == '__main__':
    register()
