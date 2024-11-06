import math
# import can
# import cantools
# import time
# import roslibpy
# from can_test import CanJoint
import json

def read_joints_map(path):
    with open(path, 'r') as file:
        data = json.load(file)
    return data
    
joints_map = read_joints_map('can_control/src/joints_map.json')
print(joints_map)
# can_bus = can.Bus("can0", bustype="socketcan")

def create_can_joints(joints_map):
    can_joints = {}
    for joint in joints_map["joints"]:
        print(joint)
        # can_joints[joint] = CanJoint(can_bus, joints_map[joint]['id'], joints_map[joint]['gear_ratio'])
    return can_joints

can_joints = create_can_joints(joints_map)

def arm_can_joints(can_joints):
    for joint in can_joints:
        print(joint)
        can_joints[joint].arm_closed_loop()
        can_joints[joint].set_limits()

arm_can_joints(can_joints)


# rosClient = roslibpy.Ros(host='ros-bridge-server', port=9090)
# rosClient.run()

# print('Is ROS Connected : ', rosClient.is_connected)

def handle_joint_cmd(message):
    print(str(message))
#     # pass
    message = json.loads(str(message))

    joint_names = message['joint_names']
    joint_positions = message['points'][0]['positions']

    joint_commands = {}
    for name, position in zip(joint_names, joint_positions):
        joint_commands[name] = position
    print(joint_commands)

    for joint in joint_names:
        can_joints[joint].set_position(joint_commands[joint])
        
# listener = roslibpy.Topic(rosClient, '/joint_group_position_controller/command', 'trajectory_msgs/JointTrajectory', queue_length=1, throttle_rate=50)
# listener.subscribe(handle_joint_cmd)

# # listener2 = roslibpy.Topic(rosClient, '/joint_states', 'sensor_msgs/JointState')
# # listener2.subscribe()

# # talker = roslibpy.Topic(client, '/joint_states', 'sensor_msgs/JointState')
# try:
#     while rosClient.is_connected:
#         pass
#         # talker.publish(roslibpy.Message())
# except KeyboardInterrupt:
#     rosClient.terminate()
