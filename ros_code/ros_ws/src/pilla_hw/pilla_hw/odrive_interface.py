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

        self.numJoints = 12
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
            1,  # hip joint
            -1,  # upper leg joint
            -1, # knee joint
            1,  # hip joint
            1,  # upper leg joint
            1, # knee joint
            1,  # hip joint
            -1,  # upper leg joint
            -1, # knee joint
            1,  # hip joint
            1,  # upper leg joint
            1  # knee joint
        ]


        self.active_ = [
            0,
            1,
            1,
            0,
            1,
            1,
            0,
            1,
            1,
            0,
            1,
            1
        ]
        self.armed_state = [False] * self.numJoints # for each odrive axis
        # SUBCRIBING (to simulation joint movement)
        self.subscription = None
        self.futures_ = [None] * self.numJoints
        # PUBLISHING & SERVICE CLIENT (to odrive node)
        self.publishers_ = []
        self.clients_ = []


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


        # while not self.cli.wait_for_service(timeout_sec=1.0):
        #     self.get_logger().info('service not available, waiting again...')
        self.req = AxisState.Request()
        self.get_logger().info('Pilla Hardware Interface Node may not have been started.')
        self.send_request(8) # make sure motor is in CLC before starting


    # For Service
    def send_AxisState_request(self, axis_requested_state):
        """Send a request to set the axis state (closed loop control) for all ODrive motors."""
        
        req = AxisState.Request()
        req.axis_requested_state = axis_requested_state
        
        # self.axis_state_service_timeouts = [None] * self.numJoints  # Track timers

        for i in range(0, self.numJoints):
            while not self.clients_[i].wait_for_service(timeout_sec=2.0):
                self.get_logger().info('odrive service not available, waiting again...')
            self.futures_[i] = self.clients_[i].call_async(self.req)
            rclpy.spin_until_future_complete(self, self.futures_[i], timeout_sec=1.0)
            self.armed_state[i] = True
            # self.futures_[i].result()  # This will raise an exception if the service call failed
            # if self.futures_[i].result() is not None:
            #     self.get_logger().info(f'Response from odrive axis {i}: {self.futures_[i].result().axis_state}')
            #     self.armed_state[i] = (self.futures_[i].result().axis_state == axis_requested_state)
            # else:
            #     self.get_logger().error(f'Error calling service for odrive axis {i}')

        self.subscription = self.create_subscription(
            JointTrajectory,
            '/joint_group_effort_controller/joint_trajectory', #topic
            self.listener_callback,
            10
        )
        # return self.future.result()

    # For subscriber (get position from simulation)
    def listener_callback(self, msg):
        # for i in range(0,self.numJoints):
        #     self.get_logger().info('I heard: "%s"' % msg.points[0].positions[i])
        send_msg = ControlMessage()
        send_msg.control_mode = 3
        send_msg.input_mode = 1
        send_msg.input_vel = 0.0
        send_msg.input_torque = 0.0

        for i in range(0,self.numJoints):
            if not self.active_[i]:
                # self.get_logger().warn(f'Axis {i} is not active. Skipping control message.')
                continue
            if not self.armed_state[i]:
                self.get_logger().warn(f'Axis {i} is not armed. Skipping control message.')
                continue
            multValue = 1.27 # for gear ratio multiplication
            if( i % 3 == 2 ):
                multValue = 2.26 # different for knee joint
            send_msg.input_pos = msg.points[0].positions[i] * self.gear_ratios[i] * self.directions[i]
            self.publishers_[i].publish(send_msg)
        # Note: 
        # -> for knee joint (position 2), must multiply by 0.7854 -> now 2.26
        # -> for upper leg (position 1), 1.27 
        # -> for hip joint (position 0), 1.27


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
