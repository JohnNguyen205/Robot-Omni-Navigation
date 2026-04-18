from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    # Get package path
    pkg_share = get_package_share_directory('robot_omni')
    ekf_config = os.path.join(pkg_share, 'config', 'ekf_para.yaml')

    # EKF node
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config, {'use_sim_time': True}]
    )
    dual_laser_merger_node = Node(
        package='dual_laser_merger',
        executable='dual_laser_merger_node',
        name='dual_laser_merger',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'laser_1_topic': '/scan_front_raw',
            'laser_2_topic': '/scan_rear_raw',
            'merged_topic': '/merged',
            'target_frame': 'base_link',
            'publish_rate': 10.0,
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



    return LaunchDescription([
        ekf_node,

        dual_laser_merger_node
    ])