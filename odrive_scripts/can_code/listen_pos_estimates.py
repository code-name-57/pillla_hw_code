# Libraries
import math
import can
import cantools
import time
from can_joint import CanJoint #get CanJoint node class


# CODE FOR GETTING MOTOR POSITION ESTIMATE

# setup
can_bus = can.Bus("can0", bustype="socketcan")
joint = CanJoint(can_bus=can_bus, can_node_id=0, gear_ratio=8, offset=0)
time.sleep(0.01)

# cycle through each message type from all 12 motors in loop
for msg in can_bus:
    for i in range(0,12):
        # check if message ID matches encoder message (0x009) from motor i
        if msg.arbitration_id == (0x09 | i << 5):
            AxisPosEstimate = 'Axis' + str(i) + '_Get_Encoder_Estimates'
            ID_number = i
            print("\nReceived Axis", ID_number, " encoder message:")
            # create and print Encoder message
            msg_dec2 = joint.can_db.decode_message(AxisPosEstimate, msg.data)
            print(msg_dec2)

    time.sleep(0.1)
   
# Finish
can_bus.shutdown()