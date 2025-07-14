# Advanced

## List of Common Commands

After successful connection, users can control the motor and obtain motor operation parameters using commands. The following table lists commonly used commands, debugging processes, and explanations:

### Basic Commands

#### dump_errors(odrv0)
Print all error messages

#### odrv0.clear_errors()
Clear all error messages

#### odrv0.save_configuration()
After modifying parameters or automatically detecting and calibrating motor parameters, be sure to execute this command to save the modifications. Otherwise, all modifications will be lost after power loss.

#### odrv0.reboot()
Reboot the driver

#### odrv0.vbus_voltage
Get the power supply voltage (V)

#### odrv0.ibus
Get the power supply current (A)

#### odrv0.hw_version_major
Hardware major version number. For 6010-8, the major version number is 3.

#### odrv0.hw_version_minor
Hardware minor version number. For 6010-8, the minor version number is 8.

#### odrv0.hw_version_variant
Different model numbers for the same hardware configuration. For 6010-8, the model number is 1.

#### odrv0.can.config.r120_gpio_num
GPIO number for controlling the 120R matching resistor switch of the CAN interface.

#### odrv0.can.config.enable_r120
Control the 120R matching resistor switch of the CAN interface.

#### odrv0.can.config.baud_rate
CAN baud rate setting.


### Parameter Configuration Instructions

#### odrv0.config.dc_bus_overvoltage_trip_level

Overvoltage alarm threshold (V)

#### odrv0.config.dc_max_positive_current

Maximum positive current value (A)

#### odrv0.config.dc_max_negative_current

Maximum negative charging current value (A)

#### odrv0.axis0.motor.config.resistance_calib_max_voltage

Maximum voltage value during motor parameter identification. Generally, this value is slightly less than half of the power supply voltage. For example, if the power supply is 24V, it can be set to 10.

#### odrv0.axis0.motor.config.calibration_current

Maximum current value during motor parameter identification. This value is generally set to 2~5A, not too large or too small.

#### odrv0.axis0.motor.config.torque_constant

Torque constant of the motor (Nm/A)

#### odrv0.axis0.min_endstop.config/odrv0.axis0.max_endstop.config
 
Configuration of the minimum (LW1)/maximum (LW2) limit switches:
enabled: Enable or disable
gpio_num: Corresponding IO number. Set the IO number of the minimum limit switch to 1 and the IO number of the maximum limit switch to 2.

#### odrv0.axis0.encoder.config.index_offset
User-set zero offset. This value is the offset of the user zero point relative to the encoder zero point. After setting and saving this offset, all user-input position control target values are based on this user zero point.

#### odrv0.axis0.motor.motor_thermistor.config/odrv0.axis0.motor.fet_thermistor.config
Configure motor temperature sensors:
enabled: Enable or disable
temp_limit_lower: Lower temperature limit
temp_limit_upper: Upper temperature limit

#### odrv0.axis0.motor.motor_thermistor.temperature
Motor temperature

#### odrv0.axis0.motor.fet_thermistor.temperature
Driver temperature



### Calibration Commands

#### odrv0.axis0.requested_state=4

Perform motor parameter identification, including identification of phase resistance, phase inductance, and calibration of three-phase current balance. This process takes 3-6 seconds and the motor will emit a sharp sound. After the sound stops or after 6 seconds without sound, run `dump_errors(odrv0)` to check for errors and make sure there are no errors before proceeding with other operations.

#### odrv0.axis0.requested_state=7

Calibrate the encoder. Before performing this operation, make sure the motor output shaft is unloaded and fix the motor with your hand or other device. After this operation, the motor will rotate in both forward and reverse directions for a certain period of time to identify and calibrate the encoder. After the motor stops, run `dump_errors(odrv0)` to check for errors and make sure there are no errors before proceeding with other steps.

#### odrv0.axis0.encoder.config.pre_calibrated=1

Write pre-calibration success, indicating that calibration is not required every time the power is turned on. This parameter can only be written after the above calibration is successful, otherwise the write will fail.

#### odrv0.axis0.controller.config.load_encoder_axis=0

Make sure the current operating motor is the 0th motor. This operation is only necessary in BETA and is not effective in production versions.


### Control Commands

#### odrv0.axis0.requested_state=1

Stop the motor and enter idle state.

#### odrv0.axis0.requested_state=8

Start the motor and enter closed-loop state.

#### odrv0.axis0.motor.config.current_lim

Maximum line current of the motor (A). An overcurrent alarm will be triggered if this value is exceeded. Please note that this value must not be greater than 100.

#### odrv0.axis0.controller.config.vel_limit

Maximum speed of the motor (turn/s). An overspeed alarm will be triggered if the rotor speed of the motor exceeds this value.

#### odrv0.axis0.controller.config.enable_vel_limit

Speed limit switch. When set to True, the above `vel_limit` takes effect. When set to False, it is invalid.

#### odrv0.axis0.controller.config.control_mode

Control mode.
0: Voltage control
1: Torque control
2: Speed control
3: Position control

#### odrv0.axis0.controller.config.input_mode

Input mode. Indicates how the user-input control value controls the motor operation:
0: Idle
1: Direct control
2: Speed ramp
3: Position filtering
5: Trapezoidal curve
6: Torque ramp
9: Motion control (MIT)

#### odrv0.axis0.controller.config.vel_gain

P value of the velocity loop PID control.

#### odrv0.axis0.controller.config.vel_integrator_gain

I value of the velocity loop PID control.

#### odrv0.axis0.controller.input_mit_kp

Position gain for motion control (MIT).

#### odrv0.axis0.controller.input_mit_kd

Velocity gain (damping coefficient) for motion control (MIT).

#### odrv0.axis0.controller.config.pos_gain

P value of the position loop PID control.

#### odrv0.axis0.controller.input_torque

Target torque for torque control, or torque feedforward for speed control/position control (Nm).

#### odrv0.axis0.controller.input_vel

Target speed for speed control, or velocity feedforward for position control (turn/s).

#### odrv0.axis0.controller.input_pos

Target position for position control (turns).

#### odrv0.axis0.encoder.set_linear_count()

Set the absolute position of the encoder. Enter a 32-bit integer in parentheses, and the absolute value of this integer must be less than `odrv0.axis0.encoder.config.cpr`.

#### odrv0.axis0.trap_traj.config

This includes three parameters:
- accel_limit: Maximum acceleration (rev/s^2)
- decel_limit: Maximum deceleration (rev/s^2)
- vel_limit: Maximum velocity (rev/s)
These three parameters are used when `odrv0.axis0.controller.config.input_mode` is set to trapezoidal curve.

#### odrv0.axis0.controller.config.input_filter_bandwidth

Position filtering bandwidth. This parameter is effective when `odrv0.axis0.controller.config.input_mode` is set to position filtering, adjusting the acceleration and deceleration effects of position control.

## Graphical Debugging

During motor debugging, if you need to monitor certain running parameters in real time, you can use Python's powerful computing and graphics libraries, as well as the high-speed throughput capability of the Type-C interface to output motor parameters in real time.

### Environment Setup

Install the computing and graphics libraries:

    pip install numpy matplotlib

### Graphical Parameter Output

In the odrivetool command-line interface, invoke the graphics library to read any motor performance indicators, such as:

    start_liveplotter(lambda:[odrv0.ibus,odrv0.axis0.encoder.pos_estimate,
    odrv0.axis0.controller.input_pos],["ibus","pos","pos_target"])

This command will invoke a graphical interface that outputs the following three indicators in real time: line current, position, and target position. Next, when performing position control on the motor, you will see the real-time position control curve of the motor:

[----------------------FIGURE----------------]

### USB and CAN Compatibility

In the early versions of this product (hardware version less than or equal to 3.7, which can be obtained through the instructions odrv0.hw_version_major and odrv0.hw_version_minor in the next section 3.1.7), USB and CAN are not compatible. You can switch between the two communication modes in the following ways (ignore this section if the hardware version is greater than 3.7):

#### Switching to CAN when using USB Communication

When CAN is disabled, users can communicate using the Type-C interface. At this time, you can switch to CAN using the following commands:

    odrv0.config.enable_can_a = True
    odrv0.axis0.requested_state = AXIS_STATE_IDLE
    odrv0.save_configuration()

#### Switching to USB when using CAN Communication

When CAN is enabled, users first switch the motor to the idle state by sending the Set_Axis_State message (parameter 1, indicating the idle state), and then switch to USB by sending the Disable_Can message (see 4.1.2). Please note that whether switching from USB to CAN or from CAN to USB, the motor must be in the idle state first, otherwise the switch will fail.

#### CAN Matching Resistor Switch

On the driver, there is a built-in 120-ohm impedance matching resistor. Users can open or close it as needed. The command examples are as follows:

    odrv0.can.config.r120_gpio_num = 5
    odrv0.can.config.enable_r120 = True

#### User Zero Point Configuration

By default, the position read by the user from the motor and the input value during position control are all based on the zero point of the absolute value encoder on the driver. However, in user scenarios, the zero point of the encoder is not the user zero point most of the time, so the user needs to manually set this zero point offset.
Generally, users can locate this zero point in two ways: through limit switches or by manually setting the zero point offset, which is the offset of the user zero point relative to the encoder zero point. After rotating to the desired user zero point position manually or through position control, use the following command:

    odrv0.axis0.encoder.config.index_offset = odrv0.axis0.encoder.pos_estimate

#### Limit Switches

The driver supports two limit switches (LW1 and LW2), where LW1 is the minimum position and also the zero position, and LW2 is the maximum position. To use both limit switches, use the following configuration:
When the limit switch is triggered, the system will report the MIN_ENDSTOP_PRESSED or MAX_ENDSTOP_PRESSED error, and the host computer can perform relevant operations at this time.
Please note that hardware version 3.7 does not support the limit switch function.

# Firmware Update Download

Firmware can be burned through the SWD interface (2.4.4) or the Type-C interface (2.4.2), providing the following three methods:

## National Download Software

### USB (DFU) Writing

Please note that the National Download Software can be burned through the Type-C interface or the SWD interface (only supports JLink and DAP). This section mainly uses the Type-C interface as an example.
First, download the USB driver for the National Burning Software (https://www.cyberbeast.cn/filedownload/789489) and install the driver for the corresponding system; then, download the National Burning Software (https://cyberbeast.cn/filedownload/766844), unzip it to any directory, and run it.
Then, connect the Type-C interface, enter odrivetool, and execute the following command to put the driver in DFU mode:

    odrv0.enter_dfu_mode()

Finally, use the National Burning Software for writing, as shown in the figure below. Please note that after the writing is completed, click "Common Operations" and then click "Reset" to restart the driver and connect it normally for debugging through odrivetool.

[---------------FIGURE -----------------------]

### SWD (JLink or DAP) Writing
Using the SWD method for downloading is similar to the DFU mode, but it needs to be connected through the SWD debugging interface (2.4.4), and select the corresponding debugging tool (JLink or DAP) in the figure above.

## pyocd

pyocd is the python version of openOCD, which supports common debugging tools such as STLink, JLink, and DAP for erasing, writing, resetting, and other operations. Please note that the driver must be connected using the SWD interface. For the wiring sequence of the SWD interface, please refer to 2.4.4. There is a 3.3V power supply in the SWD interface, so please do not connect the wires incorrectly to avoid damaging the driver!

    pip install pyocd

1. Installation
2. Writing

    pyocd list

First, list the connected debugging tools:

[---------------------FIGURE----------------]

Then, execute the following command to write the bin file:

    pyocd load .\ODrive_N32G455.bin-a 0x8000000

[---------------------FIGURE----------------]

## Motor Wizard (Coming Soon)

# Communication Protocol and Examples

