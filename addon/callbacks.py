def update_phone_pose_callback(msg):
    print(msg)
    pass
def update_phone_acc_callback(msg):
    print(msg)
    pass

cmd_callbacks = {
    'update_phone_acc': update_phone_acc_callback,
    'update_phone_pose': update_phone_pose_callback,
}