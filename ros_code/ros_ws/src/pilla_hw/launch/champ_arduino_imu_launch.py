import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():
    
    return LaunchDescription([
        Node(
            package="pilla_hw",
            executable="arduino_interface",
            name="pilla_arduino_interface",
            namespace="pilla",
        ),
        
        Node(
            package="imu_filter_madgwick",
            executable="imu_filter_madgwick_node",
            name="imu_filter_madgwick",
            namespace="pilla",
            parameters=[
                {"use_mag": False},
                {"fixed_frame": 'odom'},
                {"publish_tf": False},
            ]
        ),
])
