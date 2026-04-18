# Update this path to where your models folder actually sits
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:~/ros2_ws_project_demo/src/robot_omni/models
cd ~/ros2_ws_project
rm -rf build install log
colcon build --packages-select robot_omni
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch robot_omni gazebo_control.launch.py 