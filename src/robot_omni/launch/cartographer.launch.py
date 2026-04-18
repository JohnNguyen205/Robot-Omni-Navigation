#!/usr/bin/env python3
"""
Launch file for Cartographer.

This launch file starts the ros_cartographer node which can work better than slam_toolbox for certain simulations
It is used for creating maps from laser scan data. It is designed to be included in a
higher-level launch file.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    """Generate the launch description for the Cartographer node."""

    # Get the path to this package's share directory
    pkg = get_package_share_directory('robot_omni')
    cartographer_config_dir = LaunchConfiguration('cartographer_config_dir', default=os.path.join(
                                                  pkg, 'config'))
    configuration_basename = LaunchConfiguration('configuration_basename',
                                                 default='omni.lua')
    

    # --- Declare Launch Arguments ---
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    # --- Cartographer requires a configuration directory ---
    declare_configuration_directory_cmd = DeclareLaunchArgument(
        'configuration_directory',
        # Cartographer often needs to load assets from its package, so this is crucial.
        default_value=cartographer_config_dir,
        description='Directory containing the Cartographer .lua configuration file'
    )

    # --- Cartographer requires a .lua configuration file ---
    declare_cartographer_config_file_cmd = DeclareLaunchArgument(
        'cartographer_config_file',
        # Set this path to where your new .lua file is located
        # We will use a standard one for now, but you should copy and modify it.
        default_value=configuration_basename,
        description='Full path to the .lua configuration file for Cartographer'
    )
    #dual_laser_scan
    dual_laser_merger_node = Node(
        package='dual_laser_merger',
        executable='dual_laser_merger_node',
        name='dual_laser_merger',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'laser_1_topic': '/scan_front_raw',
            'laser_2_topic': '/scan_rear_raw',
            'merged_topic': '/scan_merged',
            'target_frame': 'base_link',
            'publish_rate': 100.0,
            'angle_increment': 0.0058,
            'scan_time': 0.1,
            'range_min': 0.05,
            'range_max': 25.0,
            'min_height': -1.0,
            'max_height': 1.0,
            'angle_min': -2.356194490192345,
            'angle_max': 2.356194490192345,
            'use_inf': False,
        }]
    )

    # =================== Cartographer Node =================== #

    
    start_cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        namespace='', 
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        arguments=[
            '-configuration_directory', LaunchConfiguration('configuration_directory'),
            '-configuration_basename', LaunchConfiguration('cartographer_config_file')
        ],
        remappings=[
            ('odom', '/mobile_base_controller/odometry'),
            ('scan', '/merged')
        ],
    )

    
    # =================== Cartographer Occupancy Grid Node  =================== #
    
    start_occupancy_grid_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node', # <--- FIXED EXECUTABLE NAME
        name='occupancy_grid_node',
        namespace='',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        arguments=[
            '-resolution', '0.05',
            '-publish_period_sec', '1.0'
        ],
    )



    # --- Create Launch Description ---
    ld = LaunchDescription()

    # Add the launch arguments to the launch description (UNCHANGED)
    ld.add_action(dual_laser_merger_node)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_cartographer_config_file_cmd)
    ld.add_action(declare_configuration_directory_cmd)

    # Add the Cartographer nodes to the launch description
    ld.add_action(start_cartographer_node)
    ld.add_action(start_occupancy_grid_node)

    return ld