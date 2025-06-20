import math
import can
import cantools
import time

class CanJoint:
    def __init__(self, can_bus, can_node_id, gear_ratio, offset):
        self.node_id = can_node_id
        self.can_db = cantools.database.load_file("odrive-cansimple.dbc")
        self.can_bus = can_bus
        self.axisID = can_node_id
        self.gear_ratio = gear_ratio
        self.offset = offset
        # self.get_position_estimate()

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

    def disarm(self):
        print("\nPutting axis",self.axisID,"into AXIS_STATE_IDLE (0x01)...")
        data = self.can_db.encode_message('Axis0_Set_Axis_State', {'Axis_Requested_State': 0x01})
        msg = can.Message(arbitration_id=0x07 | self.axisID << 5, is_extended_id=False, data=data)
        print(msg)
        try:
            self.can_bus.send(msg)
            print("Message sent on {}".format(self.can_bus.channel_info))
        except can.CanError:
            print("Message NOT sent!")

    def move_to_zero(self):
        self.clear_errors()
        self.arm_closed_loop()
        self.set_limits()
        time.sleep(1)
        data = self.can_db.encode_message('Axis0_Set_Input_Pos', {'Input_Pos':self.offset, 'Vel_FF':0.0, 'Torque_FF':0.0})
        msg = can.Message(arbitration_id=self.axisID << 5 | 0x00C, data=data, is_extended_id=False)
        self.can_bus.send(msg)

    def clear_errors(self):
        data = self.can_db.encode_message('Axis0_Clear_Errors', {})
        msg = can.Message(arbitration_id=self.axisID << 5 |  0x18, is_extended_id=False, data=data)
        self.can_bus.send(msg)
         
    def get_position_estimate(self):
        # data = self.can_db.encode_message('Axis0_Get_Encoder_Estimates', {'Pos_Estimate':0.0, 'Vel_Estimate':0.0})
        # msg = can.Message(arbitration_id=self.axisID << 5 | 0x009, is_extended_id=False, data=data)
        # self.can_bus.send(msg)

        # Wait for the response
        while True:
            response = self.can_bus.recv(timeout=1.0)
            if response and response.arbitration_id == (self.axisID << 5 | 0x009):
                position_estimate = self.can_db.decode_message('Axis0_Get_Encoder_Estimates', response.data)['Pos_Estimate']
                print("Position Estimate:", position_estimate)
                # return position_estimate
            else:
                print("Failed to get position estimate")
                # return None
        
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

    def inputPos( self, degrees_to_move ):
        setpoint = degrees_to_move*(self.gear_ratio / 360.0)
        data = self.can_db.encode_message('Axis0_Set_Input_Pos', {'Input_Pos':setpoint, 'Vel_FF':0.0, 'Torque_FF':0.0})
        msg = can.Message(arbitration_id=self.axisID << 5 | 0x00C, data=data, is_extended_id=False)
        self.can_bus.send(msg)

    def disable_can(self):
            msg = can.Message(arbitration_id=self.axisID << 5 | 0x01E, is_extended_id=False)
            self.can_bus.send(msg)
            msg = can.Message(arbitration_id=self.axisID << 5 | 0x01F, is_extended_id=False)
            self.can_bus.send(msg)