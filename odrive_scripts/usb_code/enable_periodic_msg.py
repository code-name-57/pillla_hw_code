def set_periodic_message(odrv0):
    """Enable periodic messages for the ODrive motor controller.
    This allows the controller to send periodic updates on
    its status, which can be useful for monitoring and debugging.
    """
    odrv0.axis0.config.can.heartbeat_rate_ms = 100

    odrv0.axis0.config.can.encoder_rate_ms = 10
    odrv0.axis0.config.can.bus_vi_rate_ms = 10
    odrv0.axis0.config.can.iq_rate_ms = 10

    odrv0.axis0.config.can.motor_error_rate_ms = 500
    odrv0.axis0.config.can.encoder_error_rate_ms = 500
    odrv0.axis0.config.can.controller_error_rate_ms = 500

    odrv0.axis0.config.can.sensorless_error_rate_ms = 0
    odrv0.axis0.config.can.encoder_count_rate_ms = 0
    odrv0.axis0.config.can.sensorless_rate_ms = 0

import odrive
import time

odrv0 = odrive.find_any()

set_periodic_message(odrv0)

odrv0.save_configuration()