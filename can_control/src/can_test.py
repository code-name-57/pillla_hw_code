import math
import can
import cantools
import time

class CanJoint:
    def __init__(self, can_bus, can_node_id, gear_ratio):
        self.node_id = can_node_id
        self.can_db = cantools.database.load_file("odrive-cansimple.dbc")
        self.can_bus = can_bus
        self.axisID = can_node_id
        self.gear_ratio = gear_ratio

    def arm_closed_loop(self):
        print("\nPutting axis",self.axisID,"into AXIS_STATE_CLOSED_LOOP_CONTROL (0x08)...")
        data = self.can_db.encode_message('Axis0_Set_Axis_State', {'Axis_Requested_State': 0x08})
        msg = can.Message(arbitration_id=0x07 | self.axisID << 5, is_extended_id=False, data=data)
        print(msg)
        try:
            self.can_bus.send(msg)
            print("Message sent on {}".format(self.can_bus.channel_info))
        except can.CanError:
            print("Message NOT sent!")

        # for msg in self.can_bus:
        #     if msg.arbitration_id == 0x01 | self.axisID << 5:
        #         print("\nReceived Axis heartbeat message:")
        #         msg = self.can_db.decode_message('Axis0_Heartbeat', msg.data)
        #         print(msg)
        #         if msg['Axis_State'] == 0x8:
        #             print("Axis has entered closed loop")
        #         else:
        #             print("Axis failed to enter closed loop")
        #         break

    def set_limits(self):
        data = self.can_db.encode_message('Axis0_Set_Limits', {'Velocity_Limit':10.0, 'Current_Limit':10.0})
        msg = can.Message(arbitration_id=self.axisID << 5 | 0x00F, is_extended_id=False, data=data)
        self.can_bus.send(msg)

    def test_movement(self):
        target = 0
        t0 = time.monotonic()
        for i in range(1,50):
            setpoint = 4.0 * math.sin((time.monotonic() - t0)*2)
            print("goto " + str(setpoint))
            data = self.can_db.encode_message('Axis0_Set_Input_Pos', {'Input_Pos':setpoint, 'Vel_FF':0.0, 'Torque_FF':0.0})
            msg = can.Message(arbitration_id=axisID << 5 | 0x00C, data=data, is_extended_id=False)
            self.can_bus.send(msg)
            time.sleep(0.01)

    def goto(self, angle_in_radians):
            setpoint = math.degrees(angle_in_radians)*(self.gear_ratio / 360.0)
            data = self.can_db.encode_message('Axis0_Set_Input_Pos', {'Input_Pos':setpoint, 'Vel_FF':0.0, 'Torque_FF':0.0})
            msg = can.Message(arbitration_id=self.axisID << 5 | 0x00C, data=data, is_extended_id=False)
            self.can_bus.send(msg)

    def disable_can(self):
            msg = can.Message(arbitration_id=self.axisID << 5 | 0x01E, is_extended_id=False)
            self.can_bus.send(msg)
            msg = can.Message(arbitration_id=self.axisID << 5 | 0x01F, is_extended_id=False)
            self.can_bus.send(msg)
            

