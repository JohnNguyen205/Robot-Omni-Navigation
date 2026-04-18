import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # 1. Khai báo đường dẫn đến package của bạn (Thay 'your_package_name' bằng tên package thật)
    
    pkg_share = get_package_share_directory('robot_omni')

    # 2. Định nghĩa các file launch con
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_share, 'launch', 'gazebo_control.launch.py'))
    )

    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_share, 'launch', 'localization.launch.py'))
    )

    navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_share, 'launch', 'navigation.launch.py'))
    )

    # 3. Tạo chuỗi thực thi có Delay
    # Launch Gazebo ngay lập tức
    # Sau 5 giây launch Localization
    delay_localization = TimerAction(
        period=5.0,
        actions=[localization_launch]
    )

    # Sau 10 giây (5s của Gazebo + 5s của Loc) launch Navigation
    delay_navigation = TimerAction(
        period=10.0,
        actions=[navigation_launch]
    )

    return LaunchDescription([
        gazebo_launch,
        delay_localization,
        delay_navigation
    ])
"""
colcon build --packages-select robot_omni
source install/setup.bash
ros2 launch robot_omni master_launch.py
./move.sh
"""    