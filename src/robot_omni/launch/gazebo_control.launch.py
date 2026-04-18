import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import SetEnvironmentVariable
from launch_ros.actions import Node

def generate_launch_description():

    pkg = get_package_share_directory('robot_omni')

    urdf_file = os.path.join(pkg, 'urdf', 'omni_base.urdf')
    world_file = os.path.join(pkg, 'worlds', 'hospital_full.world')
    bridge_config = os.path.join(pkg, 'config', 'bridge_config.yaml')
    controller_config = os.path.join(pkg, 'config', 'configuration.yaml')
    model_path = os.path.expanduser('~/ros2_ws_project_demo/src/robot_omni/models')

    # Read URDF
    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    # Meshes
    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=':'.join([
        os.path.dirname(pkg),     
        os.path.join(model_path),
    ])
    )
    
    # Controller YAML passed     # to gz_ros2_control
    set_ros_args = SetEnvironmentVariable(
        name='GZ_SIM_SYSTEM_PLUGIN_ARGS',
        value=f'--ros-args --params-file {controller_config}'
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': True}
        ],
        output='screen'
    )
    # Start Gazebo

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items(),
    )

    # Spawn robot
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'omni_base',
            '-x', '0.0',
            '-y', '12.0',
            '-z', '0.1',
            '-Y', '-1.57'

        ],
        output='screen'
    )

    delayed_spawn = TimerAction(
        period=15.0,
        actions=[spawn_robot]
    )

    # ROS <-> Gazebo Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_config}],
        output='screen'
    )

    delayed_bridge = TimerAction(
        period=16.0,
        actions=[bridge]
    )

    # ros2_control Controllers
    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager',
            '/controller_manager'
        ],
        output='screen'
    )

    mobile_base_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'mobile_base_controller',
            '--controller-manager',
            '/controller_manager'
        ],
        output='screen'
    )
    rviz = Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            parameters=[{'use_sim_time': True}]
    )

    delayed_controllers = TimerAction(
        period=18.0,
        actions=[
            joint_state_broadcaster,
            mobile_base_controller
        ]
    )
    delayed_rviz = TimerAction(
        period=20.0,
        actions=[
            rviz,
        ]
    )

    # Launch everything
    return LaunchDescription([
        set_gz_resource_path,
        set_ros_args,
        robot_state_publisher,
        gz_sim,
        delayed_spawn,
        delayed_bridge,
        delayed_controllers,
        delayed_rviz

    ])