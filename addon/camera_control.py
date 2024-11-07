import bpy
import math
import bpy
from mathutils import Euler, Matrix, Quaternion
import time

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
    control_target.rotation_mode = camera_rot_mode
    if camera_rot_mode == 'QUATERNION':
        control_target.rotation_quaternion = camera_rot
    else:
        control_target.rotation_euler = camera_rot

prev_q = None

def set_camera_rotation(alpha, beta, gamma, orient):
    global prev_q
    deg_to_rad = math.pi / 180.0
    alpha_rad = (alpha + orient) * deg_to_rad
    beta_rad = beta * deg_to_rad
    gamma_rad = gamma * deg_to_rad
    eul = Euler((beta_rad, gamma_rad, -alpha_rad), 'YXZ')
    q = eul.to_quaternion()
    if prev_q and q.dot(prev_q) < 0:
        q = -q
    control_target.rotation_mode = 'QUATERNION'
    q = q @ Quaternion((0, 0, 1), math.radians(-orient))
    control_target.rotation_quaternion = q
    prev_q = q



def try_insert_keyframe(obj: bpy.types.Object, data_path):
    if bpy.context.screen.is_animation_playing and bpy.context.scene.tool_settings.use_keyframe_insert_auto:
        obj.keyframe_insert(data_path=data_path, frame=bpy.context.scene.frame_current)

"""处理一帧位姿消息"""
def pose_msg_handler(param):
    global is_controlling_camera, control_target
    if not is_controlling_camera:
        return
    if control_target is None:
        return
    alpha = param['alpha']
    beta = param['beta']
    gamma = param['gamma']

    orient = 0
    if bpy.context.scene.camera_control_orient == 'Portrait':
        orient = 0
    elif bpy.context.scene.camera_control_orient == 'Landscape_1':
        orient = 90
    elif bpy.context.scene.camera_control_orient == 'Landscape_2':
        orient = -90

    set_camera_rotation(-alpha, beta, gamma, orient)

    if bpy.context.scene.record_camera_keyframe:
        try_insert_keyframe(control_target, 'rotation_quaternion')


"""处理一帧加速度消息"""
def acc_msg_handler(param):
    pass