from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    teleop = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_keyboard',
        prefix='xterm -e',  
        output='screen'
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

    return LaunchDescription([
        teleop,
        twist_stamper
    ])