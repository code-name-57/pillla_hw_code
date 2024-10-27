#!/usr/bin/env python3

import rospy
import can

from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory

def talker():
        cmd_subscriber = rospy.Subscriber('/joint_group_position_controller/command', JointTrajectory, joy_callback)
	rospy.init_node('talker', anonymous=True)
	rospy.spin()

def joy_callback(data):
	print(data)

if __name__ == '__main__':
	try:
		talker()
	except rospy.ROSInterruptException:
		pass
