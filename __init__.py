
try:
    import bpy
    from .addon.server import stop_server as stop_ws_server
    from .addon.webui import stop_server as stop_web_server
    from .addon.panel import BOBH_PT_main_panel
    from .addon.operators import BOBH_OT_start_websocket_server,    BOBH_OT_stop_websocket_server, BOBH_OT_start_webui_server, BOBH_OT_stop_webui_server
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
        name='WS_IP',
        description='ws服务器IP地址绑定',
        default='0.0.0.0'
    )
    bpy.types.Scene.default_ws_port = bpy.props.StringProperty(
        name='WS_Port',
        description='ws服务器端口绑定',
        default='8867'
    )
    bpy.types.Scene.default_web_port = bpy.props.StringProperty(
        name='Web_Port',
        description='web服务器端口绑定',
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
        default='CameraMode',
        update=update_work_mode_option  # 选项更改时的回调函数
    )

def unregister_enum_props():
    del bpy.types.Scene.work_mode_option

def register():
    # 注册所有的 class 和属性
    bpy.utils.register_class(BOBH_PT_main_panel)
    bpy.utils.register_class(BOBH_OT_start_websocket_server)
    bpy.utils.register_class(BOBH_OT_stop_websocket_server)
    bpy.utils.register_class(BOBH_OT_start_webui_server)
    bpy.utils.register_class(BOBH_OT_stop_webui_server)
    register_string_props()
    register_enum_props()

def unregister():
    # 注销所有的 class 和属性
    bpy.utils.unregister_class(BOBH_PT_main_panel)
    bpy.utils.unregister_class(BOBH_OT_start_websocket_server)
    bpy.utils.unregister_class(BOBH_OT_stop_websocket_server)
    bpy.utils.unregister_class(BOBH_OT_start_webui_server)
    bpy.utils.unregister_class(BOBH_OT_stop_webui_server)
    unregister_string_props()
    unregister_enum_props()
    stop_ws_server()
    stop_web_server()

if __name__ == '__main__':
    register()
