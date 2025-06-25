# LIBRARIES
import rclpy
from trajectory_msgs.msg import JointTrajectory #for subscriber (to champ)
from odrive_can.msg import ControlMessage #for publisher (to odrive)
from odrive_can.msg import ControllerStatus #for subscriber (to odrive)
from sensor_msgs.msg import JointState #for publisher (to champ)
from odrive_can.srv import AxisState #for service (as client)
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.task import Future
import functools
from message_filters import Subscriber, ApproximateTimeSynchronizer, Cache


class PillaHardwareInterfaceNode(Node):
    """Node that interfaces between CHAMP and ODrive motor controllers."""
    
    # INITIALIZATION (including method calls)
    def __init__(self):
        """"Initializes the pilla_node with joint parameters and sets up publishers, subscribers, services."""
        
        super().__init__('pilla_node') 

        self.numJoints = 3
        self.knee_joint_gear_ratio = 2.26 # position 2
        self.upper_leg_gear_ratio = 1.27 # position 1
        self.hip_joint_gear_ratio = 1.27 # position 0
        self.queue_size = 10

        # Member Variable Definitions
        self.odrive_pos_estimate_sub = []        
        self.odrive_joint_command_publishers = []
        self.odrive_axis_state_clients = []
        self.odrive_axis_state_futures = [Future] * self.numJoints
        self.axis_state_service_timeouts = [None] * self.numJoints  # Track timers

        # Method Calls (with Error Handling)
        try:
            self.create_champ_joint_traj_subscription()
        except Exception as e:
            self.get_logger().error(f"Failed to create CHAMP joint trajectory subscription: {e}")

        try:
            self.create_odrive_pos_estimate_subscription()
        except Exception as e:
            self.get_logger().error(f"Failed to create ODrive Position Estimate subscription: {e}")

        try:
            self.create_champ_joint_state_publisher()
        except Exception as e:
            self.get_logger().error(f"Failed to create CHAMP joint state publisher: {e}")

        try:
            self.create_odrive_publisher_and_service()
        except Exception as e:
            self.get_logger().error(f"Failed to create ODrive publisher and/or ODrive service: {e}")

    
    # SUBCRIPTIONS
    def create_champ_joint_traj_subscription(self):
        """"Creates a ROS2 subscription to the joint trajectory topic for the CHAMP robot."""
        
        self.champ_joint_traj_sub = self.create_subscription(
            JointTrajectory,
            '/joint_group_effort_controller/joint_trajectory', #topic
            self.joint_trajectory_listener_callback,
            self.queue_size
        )
        self.champ_joint_traj_sub

    def create_odrive_pos_estimate_subscription(self):
        """Creates subscriptions to ODrive position estimate topics and synchronizes their messages."""
        
        # self.odrive_pos_estimate_sub = []

        for i in range(0, self.numJoints ):
            pos_estimate_topic_string = '/odrive_axis' + str(1) + '/controller_status'
            pos_estimate_subs = Subscriber(self, ControllerStatus, pos_estimate_topic_string)
            self.odrive_pos_estimate_sub.append( pos_estimate_subs )

        self.ts = ApproximateTimeSynchronizer( self.odrive_pos_estimate_sub, queue_size=self.queue_size, slop=0.1, allow_headerless=True)
        self.ts.registerCallback(lambda *msgs: self.pos_estimates_listener_callback(list(msgs)))
        
    # PUBLISHING (to champ algorithm)
    def create_champ_joint_state_publisher(self):
        """Creates a ROS publisher for publishing joint states to CHAMP algorithm"""

        self.champ_joint_state_publisher = self.create_publisher(
            JointState,
            '/joint_states', #topic
            self.queue_size
        )

    # PUBLISHING & SERVICE CLIENT (to odrive node)
    def create_odrive_publisher_and_service(self):
        """Initialize ODrive joint command publishers and axis state service clients for each joint."""

        # self.odrive_joint_command_publishers = []
        # self.odrive_axis_state_clients = []
        # self.odrive_axis_state_futures = [Future] * self.numJoints

        for i in range(0 ,self.numJoints):
            # PUBLISHER
            joint_command_topic_string = '/odrive_axis' + str(i) + '/control_message'
            joint_command_pub = self.create_publisher(
                ControlMessage,
                joint_command_topic_string,
                self.queue_size
            )
            self.odrive_joint_command_publishers.append( joint_command_pub )
            # SERVICE CLIENT
            axis_state_topic_string = '/odrive_axis' + str(i) + '/request_axis_state'
            axis_state_client = self.create_client(
                AxisState,
                axis_state_topic_string
            )
            self.odrive_axis_state_clients.append( axis_state_client )

        self.send_AxisState_request(8) # make sure motor is in CLC before starting

    # For Service
    def send_AxisState_request(self, axis_requested_state):
        """Send a request to set the axis state (closed loop control) for all ODrive motors."""
        
        req = AxisState.Request()
        req.axis_requested_state = axis_requested_state
        
        # self.axis_state_service_timeouts = [None] * self.numJoints  # Track timers

        for i in range(0, self.numJoints):
            while not self.odrive_axis_state_clients[i].wait_for_service(timeout_sec=1.0):
                self.get_logger().info('service not available, waiting again...')
            self.odrive_axis_state_futures[i] = self.odrive_axis_state_clients[i].call_async(req)
            # Start a timer for timeout (e.g., 2 seconds)
            self.axis_state_service_timeouts[i] = self.create_timer(
                2.0, functools.partial(self.AxisState_service_timeout_callback, i)
            )
            self.odrive_axis_state_futures[i].add_done_callback(functools.partial(self.AxisState_service_done_callback, i))

    def AxisState_service_done_callback(self, i, future_):
        """Callback for handling completion of an axis state (closed loop control) service request."""

        # Cancel the timeout timer if response arrives in time
        if self.axis_state_service_timeouts[i] is not None:
            self.axis_state_service_timeouts[i].cancel()
            self.axis_state_service_timeouts[i] = None
        
        self.get_logger().info('In the callback function')
        self.get_logger().info('future ')
        response = future_.result()
        self.get_logger().info('Motor id : ' + str(i) + '  future response :: Active Errors : ' + str(response))
                            #    + '  ;  axis state : ' + str(response.axis_state) 
                            #    + '  ;  procedure_result : ' + str(response.procedure_result))

    def AxisState_service_timeout_callback(self, i):
        """Handles timeout event for axis state service response."""

        self.get_logger().error(f"Timeout waiting for response from joint {i}")
        self.axis_state_service_timeouts[i] = None

    # For subscriber (organise position information from champ and publish it, 1 -> numJoints)
    def joint_trajectory_listener_callback(self, msg):
        """Callback to process joint trajectory message and publish them as ODrive commands."""

        # for i in range(0,self.numJoints):
            # self.get_logger().info('I heard: "%s"' % msg.points[0].positions[i])
        odrive_command_msg = ControlMessage()
        odrive_command_msg.control_mode = 3
        odrive_command_msg.input_mode = 1
        odrive_command_msg.input_vel = 0.0
        odrive_command_msg.input_torque = 0.0

        for i in range(0,self.numJoints):
            gearRatio = self.hip_joint_gear_ratio
            if( i % 3 == 1 ):
                gearRatio = self.upper_leg_gear_ratio
            elif( i % 3 == 2 ):
                gearRatio = self.knee_joint_gear_ratio
            odrive_command_msg.input_pos = msg.points[0].positions[i] * gearRatio
            self.odrive_joint_command_publishers[i].publish(odrive_command_msg)

    def pos_estimates_listener_callback(self, msgs):
        """Callback to process synchronized joint position messages and publish to CHAMP as single message"""
        
        self.get_logger().info('Received synchronized messages:')
        # for i in range(self.numJoints):
        #     self.get_logger().info(f'  Message {i}: {msgs[i]}')

        joint_state_msg = JointState()

        joint_state_msg.name = [''] * self.numJoints
        joint_state_msg.position = [0.0] * self.numJoints
        joint_state_msg.velocity = [0.0] * self.numJoints
        joint_state_msg.effort = [0.0] * self.numJoints

        joint_state_msg.name[0] = 'lf_lower_leg_joint'
        joint_state_msg.name[1] = 'lf_hip_joint'
        joint_state_msg.name[2] = 'lh_upper_leg_joint'
        joint_state_msg.name[3] = 'lh_lower_leg_joint'
        joint_state_msg.name[4] = 'rf_hip_joint'
        joint_state_msg.name[5] = 'lf_upper_leg_joint'
        joint_state_msg.name[6] = 'rf_lower_leg_joint'
        joint_state_msg.name[7] = 'rh_hip_joint'
        joint_state_msg.name[8] = 'rf_upper_leg_joint'
        joint_state_msg.name[9] = 'rh_upper_leg_joint'
        joint_state_msg.name[10] = 'lh_hip_joint'
        joint_state_msg.name[11] = 'rh_lower_leg_joint'

        for i in range( self.numJoints ):
            gearRatio = self.hip_joint_gear_ratio
            if( i % 3 == 1 ):
                gearRatio = self.upper_leg_gear_ratio
            elif( i % 3 == 2 ):
                gearRatio = self.knee_joint_gear_ratio
            joint_state_msg.position[i] = msgs[i].pos_estimate / gearRatio
            joint_state_msg.velocity[i] = msgs[i].vel_estimate / gearRatio
            joint_state_msg.effort[i] = 0.0
            
        self.get_logger().info('Joint State Messages:')
        # self.get_logger().info( joint_state_msg )
        self.champ_joint_state_publisher.publish( joint_state_msg )


# MAIN
def main(args=None):
    """Entry point for initializing and spinning the Pilla hardware interface node."""

    # Confirmation of starting
    print('Hi from my_package.')

    # boilerplate setup!
    rclpy.init(args = args)
    pilla_node = PillaHardwareInterfaceNode()
    rclpy.spin( pilla_node )


if __name__ == '__main__':
    main()
