import math
import can
import cantools
import time
# import roslibpy
from can_test import CanJoint
import json

can_bus = can.Bus("can0", bustype="socketcan")

# Go through all 12 motors and disable them
for can_id in range(0,12):
        joint = CanJoint(can_bus=can_bus, can_node_id=can_id, gear_ratio=8, offset=0)
        joint.disable_can()
        time.sleep(2)