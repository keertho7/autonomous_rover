import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    # ---------- Package Paths ----------
    pkg_description = get_package_share_directory("my_rover_description")
    pkg_bringup = get_package_share_directory("my_rover_bringup")

    urdf_path = os.path.join(pkg_description, "urdf", "my_rover.urdf")
    bridge_config = os.path.join(pkg_bringup, "config", "bridge.yaml")

    # Read URDF file contents
    with open(urdf_path, 'r') as file:
        robot_description_content = file.read()

    # 1. Robot State Publisher (Fixed parameter loading)
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            "use_sim_time": True,
            "robot_description": robot_description_content  # <--- CRITICAL FIX
        }],
    )

    # 2. ROS-Gazebo Parameter Bridge
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        output="screen",
        parameters=[
            {"config_file": bridge_config},
            {"use_sim_time": True},
        ],
    )

    return LaunchDescription([
        robot_state_publisher,
        bridge,
    ])