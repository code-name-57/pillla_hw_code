import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([

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
            package="odrive_can",
            executable="odrive_can_node",
            name="odrive_can_node3",
            namespace="odrive_axis3",
            parameters=[
            {"node_id": 3},
            {"interface": "can0"}
            ]
        ),
        Node(
            package="odrive_can",
            executable="odrive_can_node",
            name="odrive_can_node4",
            namespace="odrive_axis4",
            parameters=[
            {"node_id": 4},
            {"interface": "can0"}
            ]
        ),
        Node(
            package="odrive_can",
            executable="odrive_can_node",
            name="odrive_can_node5",
            namespace="odrive_axis5",
            parameters=[
                {"node_id": 5},
                {"interface": "can0"}
            ]
        ),
        Node(
            package="odrive_can",
            executable="odrive_can_node",
            name="odrive_can_node6",
            namespace="odrive_axis6",
            parameters=[
                {"node_id": 6},
                {"interface": "can0"}
            ]
        ),
        Node(
            package="odrive_can",
            executable="odrive_can_node",
            name="odrive_can_node7",
            namespace="odrive_axis7",
            parameters=[
                {"node_id": 7},
                {"interface": "can0"}
            ]
        ),
        Node(
            package="odrive_can",
            executable="odrive_can_node",
            name="odrive_can_node8",
            namespace="odrive_axis8",
            parameters=[
                {"node_id": 8},
                {"interface": "can0"}
            ]
        ),
        Node(
            package="odrive_can",
            executable="odrive_can_node",
            name="odrive_can_node9",
            namespace="odrive_axis9",
            parameters=[
                {"node_id": 9},
                {"interface": "can0"}
            ]
        ),
        Node(
            package="odrive_can",
            executable="odrive_can_node",
            name="odrive_can_node10",
            namespace="odrive_axis10",
            parameters=[
                {"node_id": 10},
                {"interface": "can0"}
            ]
        ),
        Node(
            package="odrive_can",
            executable="odrive_can_node",
            name="odrive_can_node11",
            namespace="odrive_axis11",
            parameters=[
                {"node_id": 11},
                {"interface": "can0"}
            ]
        ),
        
])
