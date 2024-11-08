import bpy
import mathutils
from mathutils import Euler, Quaternion, Matrix
import math

from .camera_control import pose_msg_handler as camera_pose_msg_handler, acc_msg_handler as camera_acc_msg_handler

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

def update_phone_pose_callback(msg, reason):
    param = msg['param']
    if contains_none(param):
        print('Ignore Empty Message')
    if bpy.context.scene.work_mode_option == 'CameraMode':
        camera_pose_msg_handler(msg, reason)


def update_phone_acc_callback(msg, reason):
    param = msg['param']
    if contains_none(param):
        print('Ignore Empty Message')
    if bpy.context.scene.work_mode_option == 'CameraMode':
        camera_acc_msg_handler(msg, reason)

cmd_callbacks = {
    'update_phone_acc': update_phone_acc_callback,
    'update_phone_pose': update_phone_pose_callback,
}