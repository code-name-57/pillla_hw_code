import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():
    this_package_name = 'pilla_hw'
    this_package = FindPackageShare(this_package_name)
    odrive_launch_path = PathJoinSubstitution(
        [this_package, 'launch', 'odrive_nodes_launch.py']
    )
    pilla_arduino_imu_launch_path = PathJoinSubstitution(
        [this_package, 'launch', 'champ_arduino_imu_launch.py']
    )
    champ_bringup_launch_path = PathJoinSubstitution(
    [FindPackageShare('champ_config'), 'launch', 'bringup.launch.py']
    )
    champ_teleop_launch_path = PathJoinSubstitution(
    [FindPackageShare('pilla_teleop'), 'launch', 'teleop.launch.py']
    )
    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(odrive_launch_path),
        ),

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
        
        Node(
            package="pilla_hw",
            executable="odrive_interface",
            name="pilla_odrive_interface",
            namespace="pilla",
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(pilla_arduino_imu_launch_path),
        ),
        
])
