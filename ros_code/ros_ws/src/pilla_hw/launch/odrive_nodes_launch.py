from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    num_axes = 12
    nodes = [
        Node(
            package="odrive_can",
            executable="odrive_can_node",
            name=f"odrive_can_node{i}",
            namespace=f"odrive_axis{i}",
            parameters=[
                {"node_id": i},
                {"interface": "can0"},
            ]
        )
        for i in range(num_axes)
    ]
    return LaunchDescription(nodes)

