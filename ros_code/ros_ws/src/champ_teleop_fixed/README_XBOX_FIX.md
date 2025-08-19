# Xbox Gamepad Fix for Champ Teleop

This directory contains the fixed version of the champ_teleop package that resolves the issue where Xbox style USB gamepads don't output cmd_vel messages.

## Problem
The original champ_teleop node had several issues preventing Xbox gamepad input:
1. Missing `import math` statement causing runtime errors
2. Keyboard polling blocking joystick callbacks 
3. Parameter name mismatch between launch file and Python code
4. Missing conditional logic for joystick vs keyboard modes

## Solution
The fixed version includes:
1. Added `import math` statement
2. Made keyboard polling conditional on `use_joy=False`
3. Fixed parameter name consistency (`use_joy` everywhere)
4. Proper main function handling for joystick mode

## Usage
To use Xbox gamepad:
```bash
ros2 launch champ_teleop teleop.launch.py use_joy:=true
```

To use keyboard (default):
```bash
ros2 launch champ_teleop teleop.launch.py use_joy:=false
```

## Changes Made

### champ_teleop.py
- Added `import math` 
- Added `self.declare_parameter("use_joy", False)`
- Added `self.use_joy = self.get_parameter("use_joy").value`
- Made `poll_keys()` conditional: `if not self.use_joy: self.poll_keys()`
- Updated main function to handle joystick mode with `rclpy.spin()`

### launch/teleop.launch.py
- Fixed parameter: `"use_joy": use_joy` (was `"joy": use_joy`)

## Installation
Replace the original champ_teleop package with this fixed version, or apply the patch to the original code.