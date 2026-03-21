import rclpy
from rclpy.node import Node
import serial
import json
from sensor_msgs.msg import Imu


class ArduinoInterfaceNode(Node):
    def __init__(self):
        super().__init__('arduino_node')

        self.declare_parameter('serial_port', '/dev/ttyACM0')
        self.declare_parameter('baud_rate', 9600)

        serial_port = self.get_parameter('serial_port').value
        baud_rate = self.get_parameter('baud_rate').value

        # PUBLISHING
        self.publisher_arduino = self.create_publisher(
            Imu,
            'imu/data_raw',
            10
        )

        self.ser = None
        try:
            self.ser = serial.Serial(
                port=serial_port,
                baudrate=baud_rate,
                timeout=1
            )
            self.get_logger().info(f"Serial port {self.ser.name} opened successfully.")
        except serial.SerialException as e:
            self.get_logger().error(f"Error opening serial port: {e}")

        self.create_timer(0.02, self.read_serial_data)

    def read_serial_data(self):
        if self.ser is None or not self.ser.is_open:
            return
        try:
            line = self.ser.readline()
            if not line:
                return
            data = json.loads(line)

            imu_msg = Imu()
            imu_msg.header.stamp = self.get_clock().now().to_msg()
            imu_msg.header.frame_id = "imu_link"

            imu_msg.angular_velocity.x = float(data['Gx'])
            imu_msg.angular_velocity.y = float(data['Gy'])
            imu_msg.angular_velocity.z = float(data['Gz'])
            imu_msg.linear_acceleration.x = float(data['Ax'])
            imu_msg.linear_acceleration.y = float(data['Ay'])
            imu_msg.linear_acceleration.z = float(data['Az'])

            imu_msg.orientation_covariance[0] = -1  # Mark orientation as unknown
            imu_msg.orientation_covariance[4] = 1e6
            imu_msg.orientation_covariance[8] = 1e6

            imu_msg.orientation.x = 0.0
            imu_msg.orientation.y = 0.0
            imu_msg.orientation.z = 0.0
            imu_msg.orientation.w = 1.0

            imu_msg.angular_velocity_covariance[0] = 1e-6
            imu_msg.angular_velocity_covariance[4] = 1e-6
            imu_msg.angular_velocity_covariance[8] = 1e-6

            imu_msg.linear_acceleration_covariance[0] = 1e-6
            imu_msg.linear_acceleration_covariance[4] = 1e-6
            imu_msg.linear_acceleration_covariance[8] = 1e-6

            self.publisher_arduino.publish(imu_msg)
            self.get_logger().debug(f"Published IMU data: {data}")

        except json.JSONDecodeError as e:
            self.get_logger().warning(f"Failed to parse IMU JSON: {e}")
        except serial.SerialException as e:
            self.get_logger().error(f"Serial port error: {e}")
            if self.ser and self.ser.is_open:
                self.ser.close()

    def destroy_node(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.get_logger().info("Serial port closed.")
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ArduinoInterfaceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Node stopped by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()
