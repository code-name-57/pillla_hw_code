import math
import can
import cantools
import time
import roslibpy
from can_test import CanJoint

# can_bus = can.Bus("can0", bustype="socketcan")

# hip_roll_joint = CanJoint(can_bus, 9, 8)
# hip_pitch_joint = CanJoint(can_bus, 10, 8)
# knee_joint = CanJoint(can_bus, 11, 24)
# # test_joint.disable_can()
# hip_roll_joint.arm_closed_loop()
# hip_roll_joint.set_limits()

# hip_pitch_joint.arm_closed_loop()
# hip_pitch_joint.set_limits()

# knee_joint.arm_closed_loop()
# knee_joint.set_limits()

rosClient = roslibpy.Ros(host='ros-bridge-server', port=9090)
rosClient.run()

print('Is ROS Connected : ', rosClient.is_connected)

def handle_joint_cmd(message):
    print(str(message))
    # hip_roll_angle_in_rad = message['points'][0]['positions'][0]
    # hip_pitch_angle_in_rad = message['points'][0]['positions'][1]
    # knee_angle_in_rad = message['points'][0]['positions'][2]
    # # print(angle_in_rad)
    # hip_roll_joint.goto(hip_roll_angle_in_rad)
    # hip_pitch_joint.goto(hip_pitch_angle_in_rad)
    # knee_joint.goto(knee_angle_in_rad)
    # test_joint.goto(angle_in_rad)

listener = roslibpy.Topic(rosClient, '/joint_group_position_controller/command', 'trajectory_msgs/JointTrajectory', queue_length=1, throttle_rate=50)
listener.subscribe(handle_joint_cmd)

# listener2 = roslibpy.Topic(rosClient, '/joint_states', 'sensor_msgs/JointState')
# listener2.subscribe()

# talker = roslibpy.Topic(client, '/joint_states', 'sensor_msgs/JointState')
try:
    while rosClient.is_connected:
        pass
        # talker.publish(roslibpy.Message())
except KeyboardInterrupt:
    rosClient.terminate()
