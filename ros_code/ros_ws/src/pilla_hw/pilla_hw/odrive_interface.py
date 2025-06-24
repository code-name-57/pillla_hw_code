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
from message_filters import Subscriber, TimeSynchronizer

class PillaHardwareInterfaceNode(Node):
    def __init__(self):
        super().__init__('pilla_node') 

        self.numJoints = 3

        # SUBCRIBING 
        # (to simulation joint movement)
        self.subscription = self.create_subscription(
            JointTrajectory,
            '/joint_group_effort_controller/joint_trajectory', #topic
            self.listener_callback,
            10
        )
        self.subscription 

        # (to odrive pos_estimates)
        self.subscribers = []

        for i in range(2, self.numJoints ):
            topic_string = '/odrive_axis' + str(2) + '/controller_status'
            self.subscribers.append( Subscriber(self, ControllerStatus, topic_string) )

        self.ts = TimeSynchronizer( self.subscribers, queue_size=10)
        self.ts.registerCallback(self.synced_listener_callback)

        # PUBLISHING (to champ algorithm)
        self.sync_publishing = self.create_publisher(
            JointState,
            '/joint_states', #topic
            10
        )

        # PUBLISHING & SERVICE CLIENT (to odrive node)
        self.publishers_ = []
        self.pos_publish = []
        self.clients_ = []
        self.futures_ = [Future] * self.numJoints

        for i in range(0 ,self.numJoints):
            # PUBLISHER
            tempStringP = '/odrive_axis' + str(i) + '/control_message'
            tempP = self.create_publisher(
                ControlMessage,
                tempStringP,
                10
            )
            self.publishers_.append( tempP )
            # SERVICE CLIENT
            tempStringC = '/odrive_axis' + str(i) + '/request_axis_state'
            tempC = self.create_client(
                AxisState,
                tempStringC
            )
            self.clients_.append( tempC)


        self.send_request(8) # make sure motor is in CLC before starting

    # For Service
    def send_request(self, axis_requested_state):
        req = AxisState.Request()
        req.axis_requested_state = axis_requested_state
        
        self._service_timeouts = [None] * self.numJoints  # Track timers

        for i in range(0, self.numJoints):
            while not self.clients_[i].wait_for_service(timeout_sec=1.0):
                self.get_logger().info('service not available, waiting again...')
            self.futures_[i] = self.clients_[i].call_async(req)
            # Start a timer for timeout (e.g., 2 seconds)
            # self._service_timeouts[i] = self.create_timer(
            #     2.0, functools.partial(self.service_timeout_callback, i)
            # )
            self.futures_[i].add_done_callback(functools.partial(self.service_done_callback, i))

    def service_done_callback(self, i, future_):
        # Cancel the timeout timer if response arrives in time
        if self._service_timeouts[i] is not None:
            self._service_timeouts[i].cancel()
            self._service_timeouts[i] = None
        
        self.get_logger().info('In the callback function')
        self.get_logger().info('future ')
        response = future_.result()
        self.get_logger().info('Motor id : ' + str(i) + '  future response :: Active Errors : ' + str(response))
                            #    + '  ;  axis state : ' + str(response.axis_state) 
                            #    + '  ;  procedure_result : ' + str(response.procedure_result))

    def service_timeout_callback(self, i):
        self.get_logger().error(f"Timeout waiting for response from joint {i}")
        self._service_timeouts[i] = None

    # For subscriber (get position from simulation)
    def listener_callback(self, msg):
        # for i in range(0,self.numJoints):
            # self.get_logger().info('I heard: "%s"' % msg.points[0].positions[i])
        send_msg = ControlMessage()
        send_msg.control_mode = 3
        send_msg.input_mode = 1
        send_msg.input_vel = 0.0
        send_msg.input_torque = 0.0

        for i in range(0,self.numJoints):
            multValue = 1.27 # for gear ratio multiplication
            if( i % 3 == 2 ):
                multValue = 2.26 # different for knee joint
            send_msg.input_pos = msg.points[0].positions[i] * multValue
            self.publishers_[i].publish(send_msg)
        # Note: 
        # -> for knee joint (position 2), must multiply by 0.7854 -> now 2.26
        # -> for upper leg (position 1), 1.27 
        # -> for hip joint (position 0), 1.27

    def synced_listener_callback(self, msgs):
        self.get_logger().info('Received synchronized messages:')
        # for i in range(self.numJoints):
        #     self.get_logger().info(f'  Message {i}: {msgs[i]}')

        joint_state_msg = JointState()

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
            gearRatio = 1.27
            if( i % 3 == 2 ):
                gearRatio = 2.26
            joint_state_msg.position[i] = msgs[i].input_pos / gearRatio
            joint_state_msg.velocity[i] = msgs[i].input_vel / gearRatio
            joint_state_msg.effort[i] = None
            
        self.get_logger().info('Joint State Messages:')
        self.get_logger().info( joint_state_msg )
        # self.sync_publishing.publish( joint_state_msg )

# MAIN
def main(args=None):
    # Confirmation of starting
    print('Hi from my_package.')

    # boilerplate setup!
    rclpy.init(args = args)
    pilla_node = PillaHardwareInterfaceNode()
    rclpy.spin( pilla_node )



if __name__ == '__main__':
    main()
