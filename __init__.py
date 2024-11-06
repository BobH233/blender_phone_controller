
try:
    import bpy
    from .addon.server import stop_server as stop_ws_server
    from .addon.webui import stop_server as stop_web_server
    from .addon.panel import BOBH_PT_main_panel
    from .addon.operators import BOBH_OT_start_websocket_server,    BOBH_OT_stop_websocket_server, BOBH_OT_start_webui_server, BOBH_OT_stop_webui_server
    from .addon.server import update_timer
except Exception as e:
    print('Warning: Not in blender env!')


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

def register():
    # 注册所有的 class 和属性
    bpy.utils.register_class(BOBH_PT_main_panel)
    bpy.utils.register_class(BOBH_OT_start_websocket_server)
    bpy.utils.register_class(BOBH_OT_stop_websocket_server)
    bpy.utils.register_class(BOBH_OT_start_webui_server)
    bpy.utils.register_class(BOBH_OT_stop_webui_server)
    register_string_props()
    bpy.app.timers.register(update_timer)

def unregister():
    # 注销所有的 class 和属性
    bpy.utils.unregister_class(BOBH_PT_main_panel)
    bpy.utils.unregister_class(BOBH_OT_start_websocket_server)
    bpy.utils.unregister_class(BOBH_OT_stop_websocket_server)
    unregister_string_props()
    bpy.utils.unregister_class(BOBH_OT_start_webui_server)
    bpy.utils.unregister_class(BOBH_OT_stop_webui_server)
    bpy.app.timers.unregister(update_timer)
    stop_ws_server()
    stop_web_server()

if __name__ == '__main__':
    register()
