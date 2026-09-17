import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_bringup = get_package_share_directory('my_rover_bringup')
    pkg_nav2 = get_package_share_directory('nav2_bringup')

    default_map = os.path.join(pkg_bringup, 'maps', 'rover_world_map.yaml')
    default_params = os.path.join(pkg_bringup, 'config', 'nav2_params.yaml')
    default_rviz_config = os.path.join(pkg_nav2, 'rviz', 'nav2_default_view.rviz')
    bringup_script = os.path.join(pkg_bringup, 'launch', 'bringup.launch.py')

    map_arg = DeclareLaunchArgument('map', default_value=default_map, description='Full path to map file')
    params_arg = DeclareLaunchArgument('params_file', default_value=default_params, description='Full path to nav2 params')
    sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='true', description='Use simulation time')

    # 1. Hardware Bridges & TF Publisher
    hardware_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(bringup_script)
    )

    # 2. Nav2 Stack
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'params_file': LaunchConfiguration('params_file'),
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'autostart': 'true',
            'use_composition': 'False'
        }.items()
    )

    # 3. Nav2 RViz Window
    nav2_rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2, 'launch', 'rviz_launch.py')
        ),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'rviz_config': default_rviz_config
        }.items()
    )

    return LaunchDescription([
        map_arg,
        params_arg,
        sim_time_arg,
        hardware_bringup,
        nav2_bringup,
        nav2_rviz
    ])