import bpy
import math
import bpy
from mathutils import Euler, Matrix, Quaternion
import time
from collections import deque

control_target: bpy.types.Object = None

is_controlling_camera = False

initial_pose_when_starting = None

def get_is_controlling_camera():
    return is_controlling_camera

"""开始控制摄像机"""
def start_camera_control(camera: bpy.types.Object):
    global initial_pose_when_starting, control_target, is_controlling_camera
    if is_controlling_camera:
        return
    control_target = camera
    init_position = camera.location.copy()
    camera_rot_mode = camera.rotation_mode
    if camera_rot_mode == 'QUATERNION':
        camera_rot = camera.rotation_quaternion.copy()
    else:
        camera_rot = camera.rotation_euler.copy()
    initial_pose_when_starting = (init_position, camera_rot_mode, camera_rot)
    is_controlling_camera = True


"""停止控制摄像机"""
def stop_camera_control():
    global is_controlling_camera, control_target
    is_controlling_camera = False


"""恢复摄像机在开始控制时的姿态"""
def recovery_camera_pose():
    global control_target, initial_pose_when_starting
    if control_target is None:
        return
    if initial_pose_when_starting is None:
        return
    init_position, camera_rot_mode, camera_rot = initial_pose_when_starting
    control_target.location = init_position
    control_target.rotation_mode = 'QUATERNION'
    if camera_rot_mode == 'QUATERNION':
        control_target.rotation_quaternion = camera_rot
    else:
        control_target.rotation_quaternion = camera_rot.to_quaternion()

prev_q = None

def get_camera_rotation_q(alpha, beta, gamma, orient):
    global prev_q
    deg_to_rad = math.pi / 180.0
    alpha_rad = (alpha + orient) * deg_to_rad
    beta_rad = beta * deg_to_rad
    gamma_rad = gamma * deg_to_rad
    eul = Euler((beta_rad, gamma_rad, -alpha_rad), 'YXZ')
    q = eul.to_quaternion()
    q = q @ Quaternion((0, 0, 1), math.radians(-orient))
    if prev_q and q.dot(prev_q) < 0:
        q = -q
    return q



def try_insert_keyframe(obj: bpy.types.Object, data_path):
    if bpy.context.screen.is_animation_playing and bpy.context.scene.tool_settings.use_keyframe_insert_auto:
        obj.keyframe_insert(data_path=data_path, frame=bpy.context.scene.frame_current)

cache_dequeue = deque()
TIME_CACHE = 2000

# 为了保证关键帧记录连续性，确保已经收到所有的关键帧数据，记录当前关键帧的时候是以当前时间减去KEYFRAME_BACKTRACE_TIME的时刻来获取数据的
KEYFRAME_BACKTRACE_TIME = 50
KEYFRAME_TIMEOUT_TH = 1000

def get_current_latency_avg():
    from .server import get_current_latency_avg as get_latency
    return get_latency()

def get_cache_dequeue_size():
    return len(cache_dequeue)

def update_cache_queue(msg):
    global cache_dequeue
    current_timestamp_ws = int(time.time() * 1000) - get_current_latency_avg()
    while cache_dequeue and current_timestamp_ws - cache_dequeue[0]['timestamp'] > TIME_CACHE:
        cache_dequeue.popleft()
    cache_dequeue.append(msg)

def get_nearest_msg_by_time(cmd, timestamp_ws):
    nearest_msg = None
    min_time_diff = float('inf')
    for msg in cache_dequeue:
        if msg.get('cmd') == cmd:
            time_diff = abs(msg['timestamp'] - timestamp_ws)
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                nearest_msg = msg
    # if nearest_msg:
    #     print(f'寻找timestamp={timestamp_ws}, 实际寻得timestamp={nearest_msg["timestamp"]}, diff={min_time_diff}')
    return nearest_msg, min_time_diff

def set_rotation_quaternion_keyframe(obj: bpy.types.Object, frame, quaternion):
    if not obj.animation_data:
        obj.animation_data_create()
    
    if not obj.animation_data.action:
        obj.animation_data.action = bpy.data.actions.new(name=f'{obj.name}_Action_phone_controller')
    
    action = obj.animation_data.action
    
    quaternion_components = ['w', 'x', 'y', 'z']
    for index, component in enumerate(quaternion_components):
        data_path = f"rotation_quaternion"
        fcurve = action.fcurves.find(data_path, index=index)
        if not fcurve:
            fcurve = action.fcurves.new(data_path=data_path, index=index)
        
        keyframe_point = None
        for kf in fcurve.keyframe_points:
            if kf.co[0] == frame:
                keyframe_point = kf
                break
        
        if not keyframe_point:
            keyframe_point = fcurve.keyframe_points.insert(frame, quaternion[index], options={'FAST'})
        
        keyframe_point.co[1] = quaternion[index]
        keyframe_point.interpolation = 'LINEAR'

def get_orient():
    orient = 0
    if bpy.context.scene.camera_control_orient == 'Portrait':
        orient = 0
    elif bpy.context.scene.camera_control_orient == 'Landscape_1':
        orient = 90
    elif bpy.context.scene.camera_control_orient == 'Landscape_2':
        orient = -90
    
    return orient

def can_add_frame():
    if not is_controlling_camera:
        return False
    if control_target is None:
        return False
    if not bpy.context.scene.record_camera_keyframe:
        # 如果没启用关键帧记录，不需要添加关键帧
        return False
    if not bpy.context.screen.is_animation_playing:
        # 如果没有播放，不需要添加关键帧
        return False
    if not bpy.context.scene.tool_settings.use_keyframe_insert_auto:
        # 如果没有启用自动记录关键帧，不需要添加关键帧
        return False
    return True

def frame_change_handler(scene):
    if not can_add_frame():
        return
    current_frame = scene.frame_current
    current_timestamp_ws = int(time.time() * 1000) - get_current_latency_avg()
    true_frame, diff = get_nearest_msg_by_time('update_phone_pose', current_timestamp_ws - KEYFRAME_BACKTRACE_TIME)
    if diff > KEYFRAME_TIMEOUT_TH:
        print('keyframe insert timeout. give up.')
        return
    alpha = true_frame['param']['alpha']
    beta = true_frame['param']['beta']
    gamma = true_frame['param']['gamma']
    
    q = get_camera_rotation_q(-alpha, beta, gamma, get_orient())
    set_rotation_quaternion_keyframe(control_target, current_frame, q)


def get_controlling_camera():
    if not is_controlling_camera:
        return None
    return control_target


"""处理一帧位姿消息"""
def pose_msg_handler(msg, reason):
    global is_controlling_camera, control_target

    if reason == 'queue_msg':
        update_cache_queue(msg)
        return
    
    param = msg['param']
    if not is_controlling_camera:
        return
    if control_target is None:
        return
    if not can_add_frame():
        alpha = param['alpha']
        beta = param['beta']
        gamma = param['gamma']
        
        q = get_camera_rotation_q(-alpha, beta, gamma, get_orient())
        control_target.rotation_mode = 'QUATERNION'
        control_target.rotation_quaternion = q

"""处理一帧加速度消息"""
def acc_msg_handler(msg, reason):
    if reason == 'queue_msg':
        update_cache_queue(msg)
        return
    