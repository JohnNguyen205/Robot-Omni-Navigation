import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    pkg = get_package_share_directory('robot_omni')
    nav2_params = os.path.join(pkg, 'config', 'nav2_para.yaml')
    map_file = os.path.join(pkg, 'maps', 'my_map.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    yaml_map_file = LaunchConfiguration('map')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=nav2_params,
        description='Full path to nav2 params file'
    )

    declare_map_cmd = DeclareLaunchArgument(
        'map',
        default_value=map_file,
        description='Full path to map yaml file'
    )

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            params_file,
            {
                'use_sim_time': use_sim_time,
                'yaml_filename': yaml_map_file,
            }
        ]
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            params_file,
            {
                'use_sim_time': use_sim_time,
            }
        ]
    )

    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[
            params_file,
            {'use_sim_time': use_sim_time}
        ]
    )

    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[
            params_file,
            {'use_sim_time': use_sim_time}
        ]
    )

    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[
            params_file,
            {
                'use_sim_time': use_sim_time,
                'default_nav_to_pose_bt_xml': os.path.join(
                    get_package_share_directory('nav2_bt_navigator'),
                    'behavior_trees',
                    'navigate_to_pose_w_replanning_and_recovery.xml'
                ),
                'default_nav_through_poses_bt_xml': os.path.join(
                    get_package_share_directory('nav2_bt_navigator'),
                    'behavior_trees',
                    'navigate_through_poses_w_replanning_and_recovery.xml'
                )
            }
        ]
    )

    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[
            params_file,
            {'use_sim_time': use_sim_time}
        ]
    )

    twist_stamper = Node(
        package='twist_stamper',
        executable='twist_stamper',
        name='twist_stamper',
        remappings=[
            ('cmd_vel_in', '/cmd_vel'),
            ('cmd_vel_out', '/mobile_base_controller/reference')
        ],
        output='screen'
    )

    lifecycle_manager_localization = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': True,
            'node_names': ['map_server', 'amcl']
        }]
    )

    lifecycle_manager_navigation = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': True,
            'node_names': [
                'planner_server',
                'controller_server',
                'bt_navigator',
                'behavior_server'
            ]
        }]
    )

    return LaunchDescription([
        declare_use_sim_time_cmd,
        declare_params_file_cmd,
        declare_map_cmd,

        map_server,
        amcl,
        planner_server,
        controller_server,
        bt_navigator,
        behavior_server,
        twist_stamper,

        lifecycle_manager_localization,
        lifecycle_manager_navigation,
    ])