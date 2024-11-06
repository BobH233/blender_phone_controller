import bpy
import mathutils
from mathutils import Euler, Quaternion, Matrix
import math

def contains_none(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if value is None:
                return True
            if contains_none(value):
                return True
    elif isinstance(data, list):
        for item in data:
            if contains_none(item):
                return True
    else: 
        return data is None
    
    return False

def try_insert_keyframe(obj: bpy.types.Object, data_path):
    if bpy.context.screen.is_animation_playing and bpy.context.scene.tool_settings.use_keyframe_insert_auto:
        obj.keyframe_insert(data_path=data_path, frame=bpy.context.scene.frame_current)

def update_phone_pose_callback(msg):
    param = msg['param']
    if contains_none(param):
        print('Ignore Empty Message')
    if bpy.context.active_object:
        obj = bpy.context.active_object
        alpha = param['alpha']
        beta = param['beta']
        gamma = param['gamma']
        alpha_rad = math.radians(alpha)
        beta_rad = math.radians(beta)
        gamma_rad = math.radians(gamma)
        R_z = Matrix.Rotation(alpha_rad, 4, 'Z')
        R_x = Matrix.Rotation(beta_rad, 4, 'X')
        R_y = Matrix.Rotation(gamma_rad, 4, 'Y')
        rotation_matrix = R_z @ R_x @ R_y
        rotation_quaternion = rotation_matrix.to_quaternion()
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = rotation_quaternion
        try_insert_keyframe(obj, 'rotation_quaternion')

def update_phone_acc_callback(msg):
    # print(msg)
    pass

cmd_callbacks = {
    'update_phone_acc': update_phone_acc_callback,
    'update_phone_pose': update_phone_pose_callback,
}