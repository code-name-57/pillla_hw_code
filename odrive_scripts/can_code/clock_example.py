import math
import can
import cantools
import time

# Setup Variables
can_bus = can.Bus("can0", bustype="socketcan")
can_node_id = 0
#offset = 21
gear_ratio = 8
can_db = cantools.database.load_file("odrive-cansimple.dbc")
axisID = can_node_id

# Functions
def closedLoopControl():
	print("Entering AXIS_STATE_CLOSED_LOOP_CONTROL (0x08)...")
	data = can_db.encode_message('Axis0_Set_Axis_State', {'Axis_Requested_State': 0x08})
	msg = can.Message(arbitration_id=0x07 | axisID << 5, is_extended_id=False, data=data)
	print(msg)
	try:
		can_bus.send(msg)
		print("Message sent on {}".format(can_bus.channel_info))
	except can.CanError:
		print("Message NOT sent!")

def idleControl():
	print("Entering AXIS_STATE_IDLE (0x01)...")
	data = can_db.encode_message('Axis0_Set_Axis_State', {'Axis_Requested_State': 0x01})
	msg = can.Message(arbitration_id=0x07 | axisID << 5, is_extended_id=False, data=data)
	print(msg)
	try:
		can_bus.send(msg)
		print("Message sent on {}".format(can_bus.channel_info))
	except can.CanError:
		print("Message NOT sent!")
	
def inputPos( degrees_to_move ):
	#setpoint = math.degrees(angle_in_radians)*(gear_ratio / 360.0)
	setpoint = degrees_to_move*(gear_ratio / 360.0)
	data = can_db.encode_message('Axis0_Set_Input_Pos', {'Input_Pos':setpoint, 'Vel_FF':(2.0/15), 'Torque_FF':0.0})
	msg = can.Message(arbitration_id=axisID << 5 | 0x00C, data=data, is_extended_id=False)
	can_bus.send(msg)

# MAIN

# Setup
closedLoopControl()
time.sleep(0.01)

curTime = time.time()
difference = 0
curPos = 0

inputPos(0)
time.sleep(4)

print("begin clock movement")

# Clock Movement Loop - Ticks
while True:
	if( time.time() - curTime >=.1 ):
		curPos +=.6
		inputPos( curPos )
		curTime = time.time()
		print("moved to", curPos)

# To-DO
# -> use matplotlib to plot position time (seconds) to check accuracy of clock
	# -> use velocity control mode to move constantly for smoother clock
# -> use matplotlib to plot input position VS position estimate to check accuracy of motor
# -> 

idleControl()
can_bus.shutdown()
