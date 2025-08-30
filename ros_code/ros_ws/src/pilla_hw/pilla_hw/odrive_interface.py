# LIBRARIES
import rclpy
from trajectory_msgs.msg import JointTrajectory  # for subscriber (to champ)
from odrive_can.msg import ControlMessage  # for publisher (to odrive)
from odrive_can.msg import ControllerStatus  # for subscriber (to odrive)
from sensor_msgs.msg import JointState  # for publisher (to champ)
from odrive_can.srv import AxisState  # for service (as client)
from rclpy.node import Node
from std_srvs.srv import SetBool
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from rclpy.executors import MultiThreadedExecutor

class PillaHardwareInterfaceNode(Node):
    """Node that interfaces between CHAMP and ODrive motor controllers."""

    def __init__(self):
        """Initializes pilla_node with joint parameters and sets up publishers, subscribers, services."""
        super().__init__('pilla_node') 

        self.numJoints = 12
        self.queue_size = 10
        self.gear_ratios = [
            1.27,  # hip joint
            1.27,  # upper leg joint
            2.26,  # knee joint
            1.27,  # hip joint
            1.27,  # upper leg joint
            2.26,  # knee joint
            1.27,  # hip joint
            1.27,  # upper leg joint
            2.26,  # knee joint
            1.27,  # hip joint
            1.27,  # upper leg joint
            2.26   # knee joint
        ]

        self.directions = [
            1,   # hip joint
            -1,  # upper leg joint
            -1,  # knee joint
            1,   # hip joint
            1,   # upper leg joint
            1,   # knee joint
            1,   # hip joint
            -1,  # upper leg joint
            -1,  # knee joint
            1,   # hip joint
            1,   # upper leg joint
            1    # knee joint
        ]

        self.joint_names = [
            "lf_hip_joint",
            "lf_upper_leg_joint",
            "lf_lower_leg_joint",
            "rf_hip_joint",
            "rf_upper_leg_joint",
            "rf_lower_leg_joint",
            "lh_hip_joint",
            "lh_upper_leg_joint",
            "lh_lower_leg_joint",
            "rh_hip_joint",
            "rh_upper_leg_joint",
            "rh_lower_leg_joint"
        ]

        self.active_ = [
            0, 1, 1,
            0, 1, 1,
            0, 1, 1,
            0, 1, 1
        ]
        
        # Default positions array - each row is a complete position set for all 12 joints
        self.default_positions = [
            # Position 0: Neutral standing position
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            # Position 1: Sitting position (knees bent)
            [0.0, 0.5, -1.0, 0.0, 0.5, -1.0, 0.0, 0.5, -1.0, 0.0, 0.5, -1.0],
            # Position 2: Low crouch position
            [0.0, 0.8, -1.6, 0.0, 0.8, -1.6, 0.0, 0.8, -1.6, 0.0, 0.8, -1.6],
            # Position 3: High stand position
            [0.0, -0.3, 0.6, 0.0, -0.3, 0.6, 0.0, -0.3, 0.6, 0.0, -0.3, 0.6],
            # Position 4: Test position with spread legs
            [0.3, 0.0, 0.0, -0.3, 0.0, 0.0, 0.3, 0.0, 0.0, -0.3, 0.0, 0.0],
        ]
        
        self.armed_state = [False] * self.numJoints
        self.connection_status = [False] * self.numJoints
        self.last_encoder_positions = [0.0] * self.numJoints
        
        self.pilla_armed = False  # Overall armed state
        # Initialize publishers, subscribers, services
        self.setup_publishers()
        self.setup_subscribers()
        self.setup_services()
        
        self.get_logger().info('Pilla Hardware Interface Node initialized')

    def setup_publishers(self):
        """Setup all publishers for joint states and diagnostics."""
        # Publisher for joint states back to CHAMP
        self.joint_state_publisher = self.create_publisher(
            JointState,
            '/joint_states',
            self.queue_size
        )
        
        # Publishers for ODrive control commands
        self.odrive_publishers = []
        for i in range(self.numJoints):
            joint_command_topic = f'/odrive_axis{i}/control_message'
            pub = self.create_publisher(
                ControlMessage,
                joint_command_topic,
                self.queue_size
            )
            self.odrive_publishers.append(pub)
        
        # Diagnostics publisher
        self.diagnostics_publisher = self.create_publisher(
            DiagnosticArray,
            '/diagnostics',
            self.queue_size
        )

    def setup_subscribers(self):
        """Setup subscribers for joint trajectory commands and ODrive feedback."""
        # Subscriber for joint trajectory commands from CHAMP
        self.trajectory_subscription = self.create_subscription(
            JointTrajectory,
            '/joint_group_effort_controller/joint_trajectory',
            self.trajectory_callback,
            self.queue_size
        )
        
        # Subscribers for ODrive position feedback
        self.odrive_status_subscribers = []
        for i in range(self.numJoints):
            topic = f'/odrive_axis{i}/controller_status'
            sub = self.create_subscription(
                ControllerStatus,
                topic,
                lambda msg, axis=i: self.odrive_status_callback(msg, axis),
                self.queue_size
            )
            self.odrive_status_subscribers.append(sub)

    def setup_services(self):
        """Setup services for arm/disarm and calibration operations."""
        # Service clients for ODrive axis state control
        self.axis_state_clients = []
        for i in range(self.numJoints):
            service_name = f'/odrive_axis{i}/request_axis_state'
            client = self.create_client(AxisState, service_name)
            self.axis_state_clients.append(client)
        
        # Service servers for external control
        self.arm_motors_service = self.create_service(
            SetBool, 'arm_motors', self.arm_motors_callback
        )
        self.disarm_motors_service = self.create_service(
            SetBool, 'disarm_motors', self.disarm_motors_callback
        )
        
        # Service for engaging/disengaging trajectory forwarding
        self.engage_service = self.create_service(
            SetBool, 'engage', self.engage_callback
        )
        
        # Service for going to zero position
        self.go_to_zero_pos_service = self.create_service(
            SetBool, 'go_to_zero_pos', self.go_to_zero_pos_callback
        )
        
        # Timer for periodic diagnostics publishing
        self.diagnostics_timer = self.create_timer(
            1.0, self.publish_diagnostics
        )

    def engage_callback(self, request, response):
        """Service callback to engage/disengage trajectory forwarding."""
        self.pilla_armed = request.data
        
        if self.pilla_armed:
            response.success = True
            response.message = "Pilla engaged - trajectory commands will be forwarded to ODrives"
            self.get_logger().info("Pilla engaged - ready to forward trajectory commands")
        else:
            response.success = True
            response.message = "Pilla disengaged - trajectory commands will be ignored"
            self.get_logger().info("Pilla disengaged - trajectory commands will be ignored")
        
        return response

    def trajectory_callback(self, msg):
        """Handle incoming joint trajectory commands from CHAMP."""
        if not msg.points:
            # self.get_logger().warn('Received empty trajectory message')
            return
        
        if self.pilla_armed is False:
            # self.get_logger().warn('Pilla is not armed. Ignoring trajectory command.')
            return
        
        point = msg.points[0]
        control_msg = ControlMessage()
        control_msg.control_mode = 3  # Position control
        control_msg.input_mode = 1
        control_msg.input_vel = 0.0
        control_msg.input_torque = 0.0

        for i in range(min(self.numJoints, len(point.positions))):
            if not self.active_[i]:
                continue
            if not self.armed_state[i]:
                # self.get_logger().warn(f'Axis {i} is not armed. Skipping.')
                continue
            
            # Apply gear ratio and direction
            control_msg.input_pos = (point.positions[i] * 
                                   self.gear_ratios[i] * 
                                   self.directions[i])
            self.odrive_publishers[i].publish(control_msg)

    def odrive_status_callback(self, msg, axis_id):
        """Handle ODrive status feedback."""
        self.connection_status[axis_id] = True
        self.last_encoder_positions[axis_id] = msg.pos_estimate
        
        # Publish joint state feedback to CHAMP
        self.publish_joint_states()

    def publish_joint_states(self):
        """Publish current joint states back to CHAMP."""
        joint_state = JointState()
        joint_state.header.stamp = self.get_clock().now().to_msg()
        joint_state.name = self.joint_names

        # Convert encoder positions back to joint angles
        positions = []
        for i in range(self.numJoints):
            pos = (self.last_encoder_positions[i] / 
                  (self.gear_ratios[i] * self.directions[i]))
            positions.append(pos)
        
        joint_state.position = positions
        joint_state.velocity = [0.0] * self.numJoints
        joint_state.effort = [0.0] * self.numJoints
        
        self.joint_state_publisher.publish(joint_state)
    def arm_motors_callback(self, request, response):
        """Service callback to arm all motors."""
        # Store the response object to populate later
        self.pending_arm_response = response
        self.pending_arm_count = 0
        self.pending_arm_total = sum(self.active_)
        
        for i in range(self.numJoints):
            if self.active_[i]:
                self.send_axis_state_request_async(i, 8)  # CLOSED_LOOP_CONTROL
        
        # Note: This sets individual motor armed states, not the overall pilla_armed flag
        # Use the separate 'engage' service to enable trajectory forwarding
        response.success = True
        response.message = "Arming individual motors... Use 'engage' service to enable trajectory forwarding"
        self.get_logger().info("Motor arming initiated - use 'engage' service to enable trajectory forwarding")
        return response
    
    def send_axis_state_request_async(self, axis_id, state):
        """Send axis state request to ODrive asynchronously."""
        if not self.axis_state_clients[axis_id].wait_for_service(timeout_sec=2.0):
            self.get_logger().error(f'ODrive axis {axis_id} service not available')
            return
        
        request = AxisState.Request()
        request.axis_requested_state = state
        
        try:
            future = self.axis_state_clients[axis_id].call_async(request)
            future.add_done_callback(
                lambda f, axis=axis_id, req_state=state: self.handle_axis_state_response(f, axis, req_state)
            )
        except Exception as e:
            self.get_logger().error(f'Exception during service call: {e}')
    
    def handle_axis_state_response(self, future, axis_id, requested_state):
        """Handle the response from axis state service call."""
        try:
            if future.done() and not future.cancelled():
                result = future.result()
                if result is not None:
                    self.get_logger().info(f'Axis {axis_id} service response - state: {result.axis_state}, errors: {result.active_errors}, procedure: {result.procedure_result}')
                    
                    if result.axis_state == requested_state and result.active_errors == 0:
                        self.armed_state[axis_id] = True
                        self.get_logger().info(f'Successfully armed axis {axis_id}')
                    else:
                        self.get_logger().warn(f'Axis {axis_id} state request incomplete - requested: {requested_state}, actual: {result.axis_state}, errors: {result.active_errors}')
                else:
                    self.get_logger().error(f'Service returned None result for axis {axis_id}')
            else:
                self.get_logger().error(f'Service call failed for axis {axis_id}')
        except Exception as e:
            self.get_logger().error(f'Exception handling service response: {e}')
    def disarm_motors_callback(self, request, response):
        """Service callback to disarm all motors."""
        success = True
        for i in range(self.numJoints):
            if self.active_[i]:
                if self.send_axis_state_request(i, 1):  # IDLE
                    self.armed_state[i] = False
                else:
                    success = False
                    self.get_logger().error(f'Failed to disarm axis {i}')
        
        # Automatically disengage when disarming motors for safety
        self.pilla_armed = False
        
        response.success = success
        if success:
            response.message = "Disarmed all motors and disengaged Pilla"
            self.get_logger().info("All motors disarmed and Pilla automatically disengaged")
        else:
            response.message = "Failed to disarm some motors, but Pilla disengaged for safety"
            self.get_logger().warn("Some motors failed to disarm, but Pilla disengaged for safety")
        
        return response

    def send_axis_state_request(self, axis_id, state):
        """Send axis state request to ODrive."""
        if not self.axis_state_clients[axis_id].wait_for_service(timeout_sec=2.0):
            self.get_logger().error(f'ODrive axis {axis_id} service not available')
            return False
        
        request = AxisState.Request()
        request.axis_requested_state = state
        
        try:
            future = self.axis_state_clients[axis_id].call_async(request)
            rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)

            # Check the result directly instead of checking done/cancelled status
            if future.result() is not None:
                result = future.result()
                self.get_logger().info(f'Axis {axis_id} service response - state: {result.axis_state}, errors: {result.active_errors}, procedure: {result.procedure_result}')
                
                # Check if the axis reached the requested state and has no active errors
                if result.axis_state == state and result.active_errors == 0:
                    return True
                else:
                    self.get_logger().warn(f'Axis {axis_id} state request incomplete - requested: {state}, actual: {result.axis_state}, errors: {result.active_errors}')
                    return False
            else:
                self.get_logger().error(f'Service returned None result for axis {axis_id}')
                return False
        except Exception as e:
            self.get_logger().error(f'Exception during service call: {e}')
            return False

    def publish_diagnostics(self):
        """Publish diagnostics information."""
        diag_array = DiagnosticArray()
        diag_array.header.stamp = self.get_clock().now().to_msg()
        diag_array.header.frame_id = ""
        
        # Overall node health
        node_status = DiagnosticStatus()
        node_status.name = "pilla_hardware_interface"
        node_status.hardware_id = "pilla_quadruped"
        
        active_count = sum(self.active_)
        armed_count = sum(self.armed_state[i] for i in range(self.numJoints) 
                         if self.active_[i])
        connected_count = sum(self.connection_status[i] for i in range(self.numJoints) 
                             if self.active_[i])
        
        if connected_count == active_count and armed_count == active_count:
            node_status.level = DiagnosticStatus.OK
            node_status.message = "All systems operational"
        elif connected_count < active_count:
            node_status.level = DiagnosticStatus.ERROR
            node_status.message = f"Connection lost to {active_count - connected_count} ODrives"
        elif armed_count < active_count:
            node_status.level = DiagnosticStatus.WARN
            node_status.message = f"{active_count - armed_count} motors not armed"
        else:
            node_status.level = DiagnosticStatus.OK
            node_status.message = "Operational"
        
        node_status.values = [
            KeyValue(key="active_joints", value=str(active_count)),
            KeyValue(key="armed_joints", value=str(armed_count)),
            KeyValue(key="connected_joints", value=str(connected_count)),
        ]
        
        diag_array.status.append(node_status)
        
        # Individual ODrive status
        for i in range(self.numJoints):
            if self.active_[i]:
                odrive_status = DiagnosticStatus()
                odrive_status.name = f"odrive_axis_{i}"
                odrive_status.hardware_id = f"odrive_{i//2}"
                
                if not self.connection_status[i]:
                    odrive_status.level = DiagnosticStatus.ERROR
                    odrive_status.message = "No connection"
                elif not self.armed_state[i]:
                    odrive_status.level = DiagnosticStatus.WARN
                    odrive_status.message = "Not armed"
                else:
                    odrive_status.level = DiagnosticStatus.OK
                    odrive_status.message = "Operational"
                
                odrive_status.values = [
                    KeyValue(key="position", value=str(self.last_encoder_positions[i])),
                    KeyValue(key="gear_ratio", value=str(self.gear_ratios[i])),
                    KeyValue(key="direction", value=str(self.directions[i])),
                    KeyValue(key="armed", value=str(self.armed_state[i])),
                    KeyValue(key="connected", value=str(self.connection_status[i])),
                ]
                
                diag_array.status.append(odrive_status)
        
        self.diagnostics_publisher.publish(diag_array)

    def go_to_default_pos_callback(self, request, response):
        """Service callback to move robot to a predefined default position."""
        position_index = request.data
        
        # Validate position index
        if position_index < 0 or position_index >= len(self.default_positions):
            response.success = False
            response.message = f"Invalid position index {position_index}. Valid range: 0-{len(self.default_positions)-1}"
            self.get_logger().error(response.message)
            return response
        
        # Check if robot is armed
        if not self.pilla_armed:
            response.success = False
            response.message = "Robot is not armed. Please arm motors first."
            self.get_logger().warn(response.message)
            return response
        
        # Get the target positions
        target_positions = self.default_positions[position_index]
        
        # Send position commands to all active joints
        success_count = 0
        total_active = sum(self.active_)
        
        control_msg = ControlMessage()
        control_msg.control_mode = 3  # Position control
        control_msg.input_mode = 1
        control_msg.input_vel = 0.0
        control_msg.input_torque = 0.0
        
        for i in range(self.numJoints):
            if not self.active_[i]:
                continue
                
            if not self.armed_state[i]:
                self.get_logger().warn(f'Axis {i} is not armed. Skipping.')
                continue
            
            try:
                # Apply gear ratio and direction to convert joint angle to motor position
                control_msg.input_pos = (target_positions[i] * 
                                       self.gear_ratios[i] * 
                                       self.directions[i])
                
                self.odrive_publishers[i].publish(control_msg)
                success_count += 1
                self.get_logger().info(f'Sent position command to axis {i}: {control_msg.input_pos:.3f} (joint angle: {target_positions[i]:.3f})')
                
            except Exception as e:
                self.get_logger().error(f'Failed to send command to axis {i}: {e}')
        
        # Prepare response
        if success_count == total_active:
            response.success = True
            response.message = f"Successfully sent commands to move to position {position_index} ({success_count}/{total_active} joints)"
            self.get_logger().info(response.message)
        else:
            response.success = False
            response.message = f"Partial success: commanded {success_count}/{total_active} active joints to position {position_index}"
            self.get_logger().warn(response.message)
        
        return response

    def go_to_zero_pos_callback(self, request, response):
        """Service callback to move robot to zero position (neutral standing)."""
        # Check if robot is armed
        # if not self.pilla_armed:
        #     response.success = False
        #     response.message = "Robot is not armed. Please arm motors first."
        #     self.get_logger().warn(response.message)
        #     return response
        
        # Zero position - all joints at 0.0
        target_positions = [0.0] * self.numJoints
        
        # Send position commands to all active joints
        success_count = 0
        total_active = sum(self.active_)
        
        control_msg = ControlMessage()
        control_msg.control_mode = 3  # Position control
        control_msg.input_mode = 1
        control_msg.input_vel = 0.0
        control_msg.input_torque = 0.0
        
        for i in range(self.numJoints):
            if not self.active_[i]:
                continue
                
            if not self.armed_state[i]:
                self.get_logger().warn(f'Axis {i} is not armed. Skipping.')
                continue
            
            try:
                # Apply gear ratio and direction to convert joint angle to motor position
                control_msg.input_pos = (target_positions[i] * 
                                       self.gear_ratios[i] * 
                                       self.directions[i])
                
                self.odrive_publishers[i].publish(control_msg)
                success_count += 1
                self.get_logger().info(f'Sent zero position command to axis {i}: {control_msg.input_pos:.3f}')
                
            except Exception as e:
                self.get_logger().error(f'Failed to send command to axis {i}: {e}')
        
        # Prepare response
        if success_count == total_active:
            response.success = True
            response.message = f"Successfully sent commands to move to zero position ({success_count}/{total_active} joints)"
            self.get_logger().info(response.message)
        else:
            response.success = False
            response.message = f"Partial success: commanded {success_count}/{total_active} active joints to zero position"
            self.get_logger().warn(response.message)
        
        return response

def main(args=None):
    """Entry point for initializing and spinning the Pilla hardware interface node."""
    rclpy.init(args=args)
    pilla_node = PillaHardwareInterfaceNode()
    executor = MultiThreadedExecutor()
    executor.add_node(pilla_node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'Error: {e}')
    finally:
        executor.shutdown()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
