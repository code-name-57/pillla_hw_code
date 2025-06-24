# LIBRARIES
import rclpy
from trajectory_msgs.msg import JointTrajectory #for subscriber
from odrive_can.msg import ControlMessage #for publisher
from odrive_can.srv import AxisState #for service (as client)
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.task import Future
import functools

class PillaHardwareInterfaceNode(Node):
    def __init__(self):
        super().__init__('pilla_node') 

        self.numJoints = 3

        # SUBCRIBING (to simulation joint movement)
        self.subscription = self.create_subscription(
            JointTrajectory,
            '/joint_group_effort_controller/joint_trajectory', #topic
            self.listener_callback,
            10
        )
        self.subscription 

        # PUBLISHING & SERVICE CLIENT (to odrive node)
        self.publishers_ = []
        self.pos_publish = []
        self.clients_ = []
        self.futures_ = [Future] * self.numJoints

        for i in range(0,self.numJoints):
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
        
        for i in range(0, self.numJoints):
            while not self.clients_[i].wait_for_service(timeout_sec=1.0):
                self.get_logger().info('service not available, waiting again...')
            self.futures_[i] = self.clients_[i].call_async(req)
            self.futures_[i].add_done_callback(functools.partial(self.service_done_callback, i))

    def service_done_callback(self, i, future_):
        self.get_logger().info('In the callback function')
        self.get_logger().info('future ')
        response = future_.result()
        self.get_logger().info('Motor id : ' + str(i) + '  future response :: Active Errors : ' + str(response))
                            #    + '  ;  axis state : ' + str(response.axis_state) 
                            #    + '  ;  procedure_result : ' + str(response.procedure_result))



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
