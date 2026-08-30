import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

   # ---------- Package Paths ----------

    pkg_description = get_package_share_directory("my_rover_description")
    pkg_bringup = get_package_share_directory("my_rover_bringup")
    pkg_slam = get_package_share_directory("slam_toolbox")

    urdf = os.path.join(pkg_description, "urdf", "my_rover.urdf")
    slam_config = os.path.join(pkg_bringup, "config", "slam.yaml")
    bridge_config = os.path.join(pkg_bringup, "config", "bridge.yaml")

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        arguments=[urdf],
        parameters=[
            {"use_sim_time": True},
        ],
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        output="screen",
        parameters=[
            {"config_file": bridge_config},
            {"use_sim_time": True},
        ],
    )
# "/tf_static@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
    # ---------- SLAM Toolbox (Automated Lifecycle) ----------

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_slam, "launch", "online_async_launch.py")
        ),
        launch_arguments={
            "slam_params_file": slam_config,
            "use_sim_time": "true",
        }.items(),
    )

   
    return LaunchDescription([
        robot_state_publisher,
        bridge,
        slam
    ])