# Libraries
import math
import can
import cantools
import time
from can_joint import CanJoint #get CanJoint node class


# CODE FOR DETECTING MOTORS ON CAN VIA HEARTBEAT AND PRINT OUT DETERMINED CAN ID

# setup
can_bus = can.Bus("can0", bustype="socketcan")
joint = CanJoint(can_bus=can_bus, can_node_id=0, gear_ratio=8, offset=0)
time.sleep(0.01)

# Dictionary to store latest message from each motor ID
latest_messages = {}

# cycle through each message type from all 12 motors in loop
for msg in can_bus:
    # print("Received message with ID:", hex(msg.arbitration_id))
    for i in range(0,12):
        # check if message ID matches heartbeat message (0x001) from motor i
        if msg.arbitration_id == (0x01 | i << 5):
            AxisHeartbeat = 'Axis' + str(0) + '_Heartbeat'
            ID_number = i
            
            # decode message
            msg_dec2 = joint.can_db.decode_message(AxisHeartbeat, msg.data)
            
            # store/update latest message for this ID
            latest_messages[ID_number] = msg_dec2
            
            # clear terminal and print all latest messages
            print("\033[2J\033[H", end="")  # clear screen and move cursor to top
            print("Latest heartbeat messages from detected motors:")
            print("=" * 50)
            
            for motor_id in sorted(latest_messages.keys()):
                print(f"\nAxis {motor_id} heartbeat:")
                print(latest_messages[motor_id])

    time.sleep(0.01)
   
# Finish
can_bus.shutdown()