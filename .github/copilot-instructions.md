# Pilla Hardware Interface

Quadruped robot hardware interface combining ROS 2, ODrive motor controllers, and Arduino IMU sensors. This repository provides the software bridge between the CHAMP quadruped controller and the physical hardware components.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Build Steps
- Initialize git submodules: `git submodule update --init --recursive` -- takes 2 seconds. NEVER CANCEL.
- Install Python dependencies: `pip3 install colcon-common-extensions cantools pyserial flake8`  
- Build main package only: `cd ros_code/ros_ws && colcon build --packages-select pilla_hw` -- takes 1 second. NEVER CANCEL.
- **CRITICAL**: Full workspace build requires ROS 2 ament_cmake which may not be available in all environments. The build will fail with "Could not find a package configuration file provided by 'ament_cmake'" error. This is expected in non-ROS environments.

### Testing and Validation  
- Run Python linting: `cd ros_code/ros_ws/src/pilla_hw && python3 -m flake8 pilla_hw/ --count --statistics` -- takes 1 second. Expect 112+ style violations in current code.
- Test CAN infrastructure: `cd odrive_scripts/can_code && python3 -c "from can_joint import CanJoint; import cantools; print('CAN libraries work')"` -- takes <1 second.
- **VALIDATION SCENARIOS**: After making changes to CAN scripts, always test imports and basic class instantiation as CAN hardware (can0 interface) is not available in most development environments.

### Running Applications
- **CAN Scripts**: Scripts in `odrive_scripts/can_code/` require physical CAN hardware (can0 interface) and will fail with "No such device" error in development environments. This is expected behavior.
- **Arduino Code**: The IMU sketch in `arduino_sketches/imu_over_serial/` requires Arduino CLI for compilation, which may not be available due to network restrictions.
- **ROS 2 Nodes**: The hardware interface nodes require a full ROS 2 environment with ament packages for execution.

## Validation Requirements

### NEVER CANCEL Operations
- Git submodule initialization: Maximum 2 minutes timeout
- Package builds: Maximum 5 minutes timeout for individual packages
- Python linting: Maximum 2 minutes timeout

### Manual Testing Scenarios
- **Always verify CAN library imports work** after modifying ODrive scripts
- **Always run flake8 linting** before committing Python changes - expect style violations but ensure no import errors
- **Always test that pilla_hw package builds successfully** after modifying ROS code
- **Cannot test hardware functionality** without physical CAN bus, ODrive controllers, and Arduino hardware

## Important Project Structure

### Key Files and Directories
```
ros_code/ros_ws/src/pilla_hw/          # Main ROS 2 hardware interface package
├── pilla_hw/odrive_interface.py      # ODrive motor controller interface  
├── pilla_hw/arduino_interface.py     # Arduino IMU sensor interface
└── setup.py                          # Package configuration

odrive_scripts/can_code/               # ODrive CAN bus control scripts
├── can_joint.py                      # CanJoint class for motor control
├── clock_example.py                  # Position control example
├── disable_can.py                    # Motor disable script (has import bug: should be 'can_joint' not 'can_test')
└── odrive-cansimple.dbc              # CAN database definition (216 messages)

arduino_sketches/imu_over_serial/      # Arduino IMU sensor code
└── imu_over_serial.ino               # LSM6DS3 IMU data collection at 50Hz
```

### Dependencies Summary
- **ROS 2 Submodules** (git submodules): champ, champ_teleop, imu_tools, ros_odrive  
- **Python Libraries**: cantools, pyserial, colcon-common-extensions, flake8
- **Hardware Requirements**: CAN interface, ODrive motor controllers, Arduino with LSM6DS3 IMU
- **Build Tools**: colcon (works), ament_cmake (may not be available)

## Known Limitations
- **ROS 2 Environment**: Full ROS 2 installation with ament_cmake required for complete build
- **Hardware Dependencies**: CAN scripts fail without physical hardware - this is normal for development
- **Network Dependencies**: Arduino CLI installation may fail due to network restrictions
- **Style Issues**: Current codebase has 112+ flake8 style violations - focus on functional correctness over style

## Common Issues and Solutions
- **Import Error in disable_can.py**: Change `from can_test import CanJoint` to `from can_joint import CanJoint`
- **Build Failures**: ament_cmake missing is expected in non-ROS environments
- **CAN Device Errors**: "No such device can0" is expected without physical hardware
- **Arduino Compilation**: Arduino CLI may not be installable due to network restrictions

## Quick Development Workflow
Run this complete validation sequence after making any changes:
```bash
cd /home/runner/work/pillla_hw_code/pillla_hw_code
git submodule update --init --recursive
pip3 install colcon-common-extensions cantools pyserial flake8
cd ros_code/ros_ws && colcon build --packages-select pilla_hw
cd ../../odrive_scripts/can_code && python3 -c "from can_joint import CanJoint; import cantools; print('CAN libraries work')"
cd ../../ros_code/ros_ws/src/pilla_hw && python3 -m flake8 pilla_hw/ --count --statistics
```
Expected results: Build succeeds (~1 second), CAN imports work, flake8 shows 112+ violations but no import errors.