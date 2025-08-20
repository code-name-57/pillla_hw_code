# Three Control Modes
After completing the necessary preparation work and parameter configuration mentioned above, you can try controlling the motor in different modes. The 6010-8 motor supports position control, velocity control, torque control, and motion control modes.

In the position control mode, it supports filtered position control, trajectory control, and circular position control.

In the velocity control mode, it supports direct velocity control and ramped velocity control.

In the torque control mode, it supports direct torque control and ramped torque control.

The motion control mode is a comprehensive control mode that combines position, velocity, and torque control. It is usually used in scenarios that require strong instantaneous force, such as robot knee joints. Some users in the industry also refer to it as the MIT control mode, which comes from the MIT open-source robotic dog that uses this motion control mode to control the motor.

In the subsequent detailed descriptions of each control mode, this document uses USB control commands as examples. However, the same control can also be achieved using communication protocols like CAN, and the logic remains the same.

## Filtered Position Control
If the user wants to generate their own position curve and send position control commands at a certain frequency, it is recommended to use filtered position control. This mode smoothly connects these commands for execution. If trapezoidal position control is used in this case, it may cause jerky or granular motion of the motor.

In this mode, the filter bandwidth needs to be adjusted based on the frequency of the sent commands. A good practice is to set the bandwidth to half of the command frequency (in Hz). For example, if commands are sent at a frequency of 50Hz:

    odrv0.axis0.controller.config.input_filter_bandwidth = 25

Enable filtered position control:

    odrv0.axis0.controller.config.control_mode = 3
    odrv0.axis0.controller.config.input_mode = 3

Then perform position control:

    odrv0.axis0.controller.input_pos = 10 # units of turns


## Trajectory Control

This mode allows the user to set acceleration, velocity limit, and deceleration to smoothly move the motor from one position to another. The term "trajectory" refers to the velocity profile that looks like a trapezoid, as shown in the following graph, where orange represents velocity and blue represents position:

    odrv0.axis0.trap_traj.config.vel_limit # Maximum velocity limit in turns/s
    odrv0.axis0.trap_traj.config.accel_limit # Maximum acceleration limit in turns/s^2
    odrv0.axis0.trap_traj.config.decel_limit # Maximum deceleration limit in turns/s^2
    odrv0.axis0.controller.config.inertia # Inertia in Nm/(turn/s^2)

### Adjustable control parameters:

Please note that inertia x acceleration = torque, and the default value for inertia is 0. This value can improve system response, but it is directly related to the motor load. All four values mentioned above are greater than or equal to 0. Also, please note that the previously mentioned current limit and velocity limit still apply globally. For example, if the maximum velocity limit is set higher than the system-level vel_limit, the global vel_limit will take effect.

    odrv0.axis0.controller.config.control_mode = 3
    odrv0.axis0.controller.config.input_mode = 5

To enable trapezoidal trajectory control mode, first:
Then perform position control:


## Circular Position Control

    odrv0.axis0.controller.input_pos = 10 # in turns

This mode is suitable for continuous incremental position control, such as rotating the robot wheel in one direction for a period of time, or continuously running a conveyor belt. If the usual position control mode is used, the target position will gradually increase to a large value, resulting in positioning errors due to floating point precision issues.

    odrv0.axis0.controller.config.circular_setpoints = 1

Enable:

In this mode, each small step is within one revolution, and the range of input_pos is [0,1). If input_pos increases beyond this range, it will be converted to a value within one revolution. If the user wants a single step to exceed one revolution, the following parameter can be set to a value greater than 1:

    odrv0.axis0.controller.config.circular_setpoint_range = <N>

## Direct Velocity Control

    odrv0.axis0.controller.config.control_mode = 2
    odrv0.axis0.controller.config.input_mode = 1

This mode is the simplest velocity control mode. Enable it as follows:
Then input the target velocity for control:

    odrv0.axis0.controller.input_vel = 10 # units of turns/s

## Ramped Velocity Control

Ramped velocity control mode gradually increases the velocity to the target value according to a certain slope. It is smoother than direct velocity control. Enable it as follows:

    odrv0.axis0.controller.config.control_mode = 2
    odrv0.axis0.controller.config.input_mode = 2

Adjust the slope to control the acceleration:

    odrv0.axis0.controller.config.vel_ramp_rate = 0.5 # slope unit is turns/s^2

Then input the target velocity for control:

    odrv0.axis0.controller.input_vel = 10 # units of turns/s

## Direct Torque Control

    odrv0.axis0.controller.config.control_mode = 1
    odrv0.axis0.controller.config.input_mode = 1

This is the simplest torque (current) control mode. Enable it as follows:
The torque control unit is Nm, while the current unit in the driver firmware is A. Therefore, it is necessary to set the torque constant to allow the driver to convert Nm to current and drive the motor to output the desired torque.

    # Torque constant is approximately 8.23 Nm/A
    odrv0.axis0.motor.config.torque_constant = 8.23/12.3

    odrv0.axis0.controller.input_torque = 1.2 # units of Nm

Then input the target velocity for control:
Also, please note that if the user wants to limit the maximum velocity in torque mode, they can enable enable_torque_mode_vel_limit and set vel_limit as follows:

    odrv0.axis0.controller.config.enable_torque_mode_vel_limit = 1
    odrv0.axis0.controller.config.vel_limit = 30 # units of turns/s

## Ramped Torque Control

    odrv0.axis0.controller.config.control_mode = 1
    odrv0.axis0.controller.config.input_mode = 6

Ramped torque control is very similar to ramped velocity control. Enable it as follows:
Adjust the slope as follows:

    odrv0.axis0.controller.config.torque_ramp_rate = 0.1 # slope unit is Nm/s

## Motion Control (MIT Control)

Motion control mode controls the motor to move to the target position by comprehensively controlling position, velocity, and torque. It can be represented by the following formula:

    𝑛𝑒𝑤𝑡𝑜𝑟𝑞𝑢𝑒 = 𝐾𝑝 × 𝑒𝑟𝑟𝑜𝑟 + 𝐾𝑑 × 𝑒𝑟𝑟𝑜𝑟 + 𝐹𝑓𝑓
    𝑒𝑟𝑟𝑜𝑟 = 𝑛𝑒𝑤𝑡𝑜𝑟𝑞𝑢𝑒 − 𝑟𝑒𝑎𝑙𝑖𝑧𝑒𝑑
    𝑒𝑟𝑟𝑜𝑟 = 𝑛𝑒𝑤𝑡𝑜𝑟𝑞𝑢𝑒 − 𝑟𝑒𝑎𝑙𝑖𝑧𝑒𝑑

Where 𝑛𝑒𝑤𝑡𝑜𝑟𝑞𝑢𝑒 is the target torque, 𝑒𝑟𝑟𝑜𝑟 is the position error, 𝑒𝑟𝑟𝑜𝑟 is the velocity error, 𝐾𝑝 is the position control gain, 𝐾𝑑 is the velocity control gain (or damping coefficient), and 𝐹𝑓𝑓 is the feedforward torque.

    odrv0.axis0.controller.config.input_mode=9

Enable motion control mode as follows:
Adjust the gains:
Then perform motion control by inputting input_pos, input_vel, and input_torque:

    odrv0.axis0.controller.input_mit_kp=<float> # position gain, unit is Nm/turn
    odrv0.axis0.controller.input_mit_kd=<float> # damping coefficient, unit is Nm/turn/s

    odrv0.axis0.controller.input_pos=5 # units of turns
    odrv0.axis0.controller.input_vel=30 # units of turns/s
    odrv0.axis0.controller.input_torque=2 # units of Nm
