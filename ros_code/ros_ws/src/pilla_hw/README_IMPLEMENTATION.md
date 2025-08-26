# Pilla Hardware Interface Node Implementation

This document describes the implementation of the ROS 2 node for locomotion-to-ODrive communication.

## Overview

The `PillaHardwareInterfaceNode` class provides a complete interface between a locomotion algorithm (such as CHAMP) and ODrive motor controllers for a quadruped robot.

## Key Features Implemented

### 1. Joint Command Processing
- Accepts joint trajectory commands from locomotion algorithms
- Supports 12 joint angles, velocities, or torques
- Applies gear ratios and direction corrections per joint
- Publishes control messages to individual ODrive nodes

### 2. Encoder Feedback
- Receives encoder positions from ODrive controllers
- Converts encoder data back to joint angles
- Publishes joint states to locomotion algorithm via `/joint_states` topic

### 3. Motor Control Services
- **Arm Motors**: Service to put all active motors into closed-loop control mode
- **Disarm Motors**: Service to put all motors into idle state

### 4. Diagnostics Publishing
- Publishes comprehensive diagnostics to `/diagnostics` topic
- Reports connection status, calibration status, and error states
- Provides individual ODrive status monitoring
- Publishes at 1Hz for real-time monitoring

## Topics and Services

### Subscribed Topics
- `/joint_group_effort_controller/joint_trajectory` - Joint trajectory commands from CHAMP
- `/odrive_axis{N}/controller_status` - Encoder feedback from each ODrive (N = 0-11)

### Published Topics
- `/joint_states` - Joint state feedback to CHAMP
- `/diagnostics` - System diagnostics and health status
- `/odrive_axis{N}/control_message` - Control commands to each ODrive (N = 0-11)

### Services Provided
- `arm_motors` - Arm all active motors (SetBool)
- `disarm_motors` - Disarm all motors (SetBool)

## Configuration

### Joint Configuration
- **12 joints total** (3 per leg × 4 legs)
- **Active joints**: Currently joints 1,2,4,5,7,8,10,11 (8 total active)
- **Gear ratios**: 1.27 for hip/upper leg joints, 2.26 for knee joints
- **Directions**: Individual direction multipliers per joint

### ODrive Mapping
- Each joint maps to a corresponding ODrive axis
- Service clients created for each ODrive axis state control
- Position feedback synchronized from all active ODrives

## Error Handling and Status Monitoring

The node tracks several status indicators:
- **Connection Status**: Whether each ODrive is responding
- **Armed Status**: Whether each motor is in closed-loop control
- **Position Feedback**: Last known encoder positions

## Integration with CHAMP

The node is designed for seamless integration with the CHAMP locomotion stack:
- Compatible topic names and message types
- Proper joint state feedback for closed-loop control
- Configurable for different quadruped configurations

## Usage

1. **Launch the node**: `ros2 run pilla_hw odrive_interface`
2. **Arm motors**: `ros2 service call /arm_motors std_srvs/srv/SetBool "data: true"`
3. **Start locomotion**: Launch CHAMP nodes
4. **Monitor status**: `ros2 topic echo /diagnostics`

*Note: ODrive motor and encoder calibration should be performed separately before robot assembly.*

## Future Extensibility

The node is structured for easy extension:
- Additional service implementations can be added to the `setup_services()` method
- New diagnostic parameters can be added to the `publish_diagnostics()` method
- Support for additional ODrive features can be integrated into the control message handling