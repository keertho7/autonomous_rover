import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    # ---------- Package Paths ----------

    pkg_bringup = get_package_share_directory("my_rover_bringup")
    pkg_description = get_package_share_directory("my_rover_description")

    world = os.path.join(pkg_description, "worlds", "rover_world.sdf")
    model = os.path.join(pkg_description, "models", "model.sdf")
    bringup = os.path.join(pkg_bringup, "launch", "bringup.launch.py")

    # ---------- Gazebo ----------

    gazebo = ExecuteProcess(
        cmd=["gz", "sim", "-r", world],
        output="screen",
    )

    # ---------- Spawn Rover ----------

    spawn_rover = ExecuteProcess(
        cmd=[
            "ros2", "run", "ros_gz_sim", "create",
            "-file", model,
            "-name", "my_rover",
            "-allow_renaming", "false",
        ],
        output="screen",
    )

    # ---------- ROS Bringup ----------

    bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(bringup)
    )

    # ---------- RViz2 ----------

    rviz = ExecuteProcess(
        cmd=["rviz2"],
        output="screen",
    )

    return LaunchDescription([
        gazebo,

        # Wait for Gazebo to start before spawning
        TimerAction(
            period=3.0,
            actions=[spawn_rover],
        ),

        bringup_launch,

        # Start RViz
        TimerAction(
            period=5.0,
            actions=[rviz],
        ),
    ])