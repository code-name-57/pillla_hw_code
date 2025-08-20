def set_can_id(odrv0, can_id):
    """Set the CAN ID for the ODrive motor controller.
    This allows the controller to be identified on the CAN bus.
    """
    odrv0.axis0.config.can.node_id = can_id

def set_zero_offset(odrv0):
    """Set the zero offset for the ODrive motor controller.
    This is used to calibrate the motor position.
    """
    odrv0.axis0.encoder.config.index_offset = odrv0.axis0.encoder.pos_estimate

def enable_can(odrv0):
    """Enable CAN communication for the ODrive motor controller."""
    odrv0.config.enable_can_a = True

def get_clockwise_direction(odrv0):
    """Get the pos_estimate sign when motor moves to clockwise direction."""
    return 1 if odrv0.axis0.encoder.pos_estimate >= 0 else -1

def get_clockwise_end_stop_position(odrv0):
    """Check if the motor has reached the clockwise end stop."""
    return odrv0.axis0.encoder.pos_estimate

def get_counter_clockwise_direction(odrv0):
    """Get the pos_estimate sign when motor moves to counter-clockwise direction."""
    return -1 if odrv0.axis0.encoder.pos_estimate <= 0 else 1

def get_counter_clockwise_end_stop_position(odrv0):
    """Check if the motor has reached the counter-clockwise end stop."""
    return odrv0.axis0.encoder.pos_estimate

import odrive
import time

odrv0 = odrive.find_any()

can_id = int(input("Enter the desired CAN ID for the ODrive: "))
set_can_id(odrv0, can_id)

input("Move the joint to the neutral position and press Enter to continue...")
# set_zero_offset(odrv0)
# odrv0.save_configuration()

# time.sleep(10)  # Wait for the configuration to be saved

# odrv0 = odrive.find_any()

input("Move the joint clockwise to the end stop and press Enter to continue...")
clockwise_pos_est = get_clockwise_end_stop_position(odrv0)
clockwise_direction = get_clockwise_direction(odrv0)

print(f"Clockwise end stop position: {clockwise_pos_est}, Direction: {clockwise_direction}")

input("Move the joint counter-clockwise to the end stop and press Enter to continue...")
counter_clockwise_pos_est = get_counter_clockwise_end_stop_position(odrv0)
counter_clockwise_direction = get_counter_clockwise_direction(odrv0)

print(f"Counter-clockwise end stop position: {counter_clockwise_pos_est}, Direction: {counter_clockwise_direction}")

# Confirm user to proceed with enableing CAN, USB communication will be disabled
confirm = input("Do you want to enable CAN ? This will disable USB communication. Proceed? (yes/no): ")
# if confirm.lower() == "yes":
    # enable_can(odrv0)

