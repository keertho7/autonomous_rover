from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    rover_ws = os.path.expanduser("~/rover_ws")

    world = os.path.join(
        rover_ws,
        "src",
        "my_rover",
        "rover_world.sdf",
    )

    model = os.path.join(
        rover_ws,
        "src",
        "my_rover",
        "model.sdf",
    )

    bringup = os.path.join(
        get_package_share_directory("my_rover_bringup"),
        "launch",
        "bringup.launch.py",
    )

    # ---------- Gazebo ----------

    gazebo = ExecuteProcess(
        cmd=["gz", "sim", world],
        output="screen",
    )

    # ---------- Spawn Rover ----------

    spawn_rover = ExecuteProcess(
        cmd=[
            "gz", "service",
            "-s", "/world/empty/create",
            "--reqtype", "gz.msgs.EntityFactory",
            "--reptype", "gz.msgs.Boolean",
            "--timeout", "300",
            "--req",
            f'sdf_filename: "{model}", '
            'name: "my_rover", '
            'allow_renaming: false',
        ],
        output="screen",
    )

    # ---------- ROS Bringup ----------

    bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(bringup)
    )

    # ---------- Configure SLAM ----------

    configure_slam = ExecuteProcess(
        cmd=[
            "ros2",
            "lifecycle",
            "set",
            "/slam_toolbox",
            "configure",
        ],
        output="screen",
    )

    # ---------- Activate SLAM ----------

    activate_slam = ExecuteProcess(
        cmd=[
            "ros2",
            "lifecycle",
            "set",
            "/slam_toolbox",
            "activate",
        ],
        output="screen",
    )

    # ---------- RViz ----------

    rviz = ExecuteProcess(
        cmd=["rviz2"],
        output="screen",
    )

    return LaunchDescription([

        gazebo,

        # Wait for Gazebo, then spawn rover
        TimerAction(
            period=8.0,
            actions=[spawn_rover],
        ),

        bringup_launch,

        # Configure SLAM
        TimerAction(
            period=10.0,
            actions=[configure_slam],
        ),

        # Activate SLAM
        TimerAction(
            period=12.0,
            actions=[activate_slam],
        ),

        # Start RViz
        TimerAction(
            period=9.0,
            actions=[rviz],
        ),
    ])