from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    # ---------- Robot Description ----------

    urdf = os.path.join(
        get_package_share_directory("my_rover_description"),
        "urdf",
        "my_rover.urdf",
    )

     
    slam_config = os.path.join(
        get_package_share_directory("my_rover_bringup"),
        "config",
        "slam.yaml",
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        arguments=[urdf],
        parameters=[
            {"use_sim_time": True},
        ],
    )

    # ---------- Gazebo Bridge ----------

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        output="screen",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            "/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
           
        ],
    )
# "/tf_static@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
    # ---------- SLAM ----------
    slam = Node(
        package="slam_toolbox",
        executable="async_slam_toolbox_node",
        name="slam_toolbox",
        output="screen",
        parameters=[slam_config],
    )

    return LaunchDescription([
        robot_state_publisher,
        bridge,
        
    ])