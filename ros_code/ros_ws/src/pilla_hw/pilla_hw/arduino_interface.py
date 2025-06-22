import rclpy
from rclpy.node import Node
import serial
import json
from sensor_msgs.msg import Imu

class ArduinoInterfaceNode(Node):
    def __init__(self):
        super().__init__('arduino_node')

        # PUBLISHING (to odrive node)
        self.publisher_arduino = self.create_publisher(
            Imu,
            '/imu2/data', #topic
            10
        )
        try:
            self.ser = serial.Serial(
                port='/dev/ttyACM0',  # Replace with your serial port
                baudrate=9600,
                timeout=1
            )
            self.get_logger().info(f"Serial port {self.ser.name} opened successfully.")

        except serial.SerialException as e:
            self.get_logger().error(f"Error opening serial port: {e}")

        self.read_serial_data()
    
    def read_serial_data(self):
        while rclpy.ok():
            try:
                line = self.ser.readline()
                if line:
                    data = json.loads(line)
                    self.get_logger().info(f"Published IMU data: {data}")

                    imu_msg = Imu()
                    imu_msg.header.stamp = self.get_clock().now().to_msg()
                    imu_msg.angular_velocity.x = float(data['Gx'])
                    imu_msg.angular_velocity.y = float(data['Gy'])
                    imu_msg.angular_velocity.z = float(data['Gz'])
                    imu_msg.linear_acceleration.x = float(data['Ax'])
                    imu_msg.linear_acceleration.y = float(data['Ay'])
                    imu_msg.linear_acceleration.z = float(data['Az'])

                    self.publisher_arduino.publish(imu_msg)

            except serial.SerialException as e:
                self.get_logger().error(f"Error opening serial port: {e}")
            finally:
                if 'ser' in locals() and self.ser.is_open:
                    self.ser.close()
                    self.get_logger().info("Serial port closed.")


def main(args=None):

    rclpy.init(args=args)
    node = ArduinoInterfaceNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Node stopped by user.")
    finally:
        rclpy.shutdown()