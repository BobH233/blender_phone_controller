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