import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():
    champ_bringup_launch_path = PathJoinSubstitution(
    [FindPackageShare('champ_config'), 'launch', 'bringup.launch.py']
    )
    champ_teleop_launch_path = PathJoinSubstitution(
    [FindPackageShare('champ_teleop'), 'launch', 'teleop.launch.py']
    )
    return LaunchDescription([
            
        DeclareLaunchArgument(
            name='rviz', 
            default_value='true',
            description='Run rviz'
        ),

        DeclareLaunchArgument(
            name='robot_name', 
            default_value='champ',
            description='Set robot name for multi robot'
        ),

        DeclareLaunchArgument(
            name='sim', 
            default_value='false',
            description='Enable use_sim_time to true'
        ),

        DeclareLaunchArgument(
            name='hardware_connected', 
            default_value='false',
            description='Set to true if connected to a physical robot'
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(champ_bringup_launch_path),
            launch_arguments={
                'robot_name': LaunchConfiguration('robot_name'),
                'rviz': LaunchConfiguration('rviz'),
                'sim': LaunchConfiguration('sim'),
                'hardware_connected': LaunchConfiguration('hardware_connected'),
            }.items()
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(champ_teleop_launch_path),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('sim'),
                'use_joy': 'true',
                'dev': '/dev/input/js0'
            }.items()
        ),
        # Add odrive_can_node
        Node(
            package="odrive_can",
            executable="odrive_can_node",
            name="odrive_can_node0",
            namespace="odrive_axis0",
            parameters=[
            {"node_id": 0},
            {"interface": "can0"}
            ]
        ),
        Node(
            package="odrive_can",
            executable="odrive_can_node",
            name="odrive_can_node1",
            namespace="odrive_axis1",
            parameters=[
            {"node_id": 1},
            {"interface": "can0"}
            ]
        ),
        Node(
            package="odrive_can",
            executable="odrive_can_node",
            name="odrive_can_node2",
            namespace="odrive_axis2",
            parameters=[
            {"node_id": 2},
            {"interface": "can0"}
            ]
        ),
        Node(
            package="pilla_hw",
            executable="odrive_interface",
            name="pilla_odrive_interface",
            namespace="pilla",
        ),
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
