import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction

def generate_launch_description():
    pkg_description = get_package_share_directory("my_rover_description")

    world = os.path.join(pkg_description, "worlds", "rover_world.sdf")
    model = os.path.join(pkg_description, "models", "model.sdf")

    # 1. Start Gazebo World
    gazebo = ExecuteProcess(
        cmd=["gz", "sim", "-r", world],
        output="screen",
    )

    # 2. Spawn Rover Model
    spawn_rover = ExecuteProcess(
        cmd=[
            "ros2", "run", "ros_gz_sim", "create",
            "-file", model,
            "-name", "my_rover",
            "-allow_renaming", "false",
        ],
        output="screen",
    )

    return LaunchDescription([
        gazebo,
        TimerAction(
            period=3.0,
            actions=[spawn_rover],
        ),
    ])