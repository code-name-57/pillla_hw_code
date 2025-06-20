# LIBRARIES
import rclpy
from trajectory_msgs.msg import JointTrajectory #for subscriber
from odrive_can.msg import ControlMessage #for publisher
from odrive_can.srv import AxisState #for service (as client)
from rclpy.node import Node
from std_msgs.msg import String

class PillaHardwareInterfaceNode(Node):
    def __init__(self):
        super().__init__('pilla_node')

        # SUBCRIBING (to simulation joint movement)
        self.subscription = self.create_subscription(
            JointTrajectory,
            '/joint_group_effort_controller/joint_trajectory', #topic
            self.listener_callback,
            10
        )
        self.subscription 

        # PUBLISHING (to odrive node)
        self.publisher_0 = self.create_publisher(
            ControlMessage,
            '/odrive_axis0/control_message', #topic
            10
        )
        self.publisher_1 = self.create_publisher(
            ControlMessage,
            '/odrive_axis1/control_message', #topic
            10
        )
        self.publisher_2 = self.create_publisher(
            ControlMessage,
            '/odrive_axis2/control_message', #topic
            10
        )

        # SERVICE CLIENT

        self.cli_0 = self.create_client(AxisState, '/odrive_axis0/request_axis_state')
        self.cli_1 = self.create_client(AxisState, '/odrive_axis1/request_axis_state')
        self.cli_2 = self.create_client(AxisState, '/odrive_axis2/request_axis_state')
        # while not self.cli.wait_for_service(timeout_sec=1.0):
        #     self.get_logger().info('service not available, waiting again...')
        self.req = AxisState.Request()
        self.send_request(8) # make sure motor is in CLC before starting

    # For Service
    def send_request(self, axis_requested_state):
        self.req.axis_requested_state = axis_requested_state
        self.future = self.cli_0.call_async(self.req)
        self.future = self.cli_1.call_async(self.req)
        self.future = self.cli_2.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

    # For subscriber (get position from simulation)
    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.points[0].positions[0])
        self.get_logger().info('I heard: "%s"' % msg.points[0].positions[1])
        self.get_logger().info('I heard: "%s"' % msg.points[0].positions[2])
        send_msg = ControlMessage()
        send_msg.control_mode = 3
        send_msg.input_mode = 1
        send_msg.input_vel = 0.0
        send_msg.input_torque = 0.0

        send_msg.input_pos = msg.points[0].positions[0] * 1.27 # Different!!
        self.publisher_0.publish(send_msg)
        send_msg.input_pos = msg.points[0].positions[1] * 1.27 # Different!!
        self.publisher_1.publish(send_msg)
        send_msg.input_pos = msg.points[0].positions[2] * 2.26 # Different!!
        self.publisher_2.publish(send_msg)
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

    # Shutdown process
    pilla_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
