🚀 ROS 2 Autonomous Multi-Goal Navigation using Genetic Algorithm
🧠 Intelligent Path Optimization in Complex Indoor Environments
🧩 1. Project Motivation

Traditional robotic navigation systems (e.g., Nav2) are designed to:

Navigate to a single goal at a time
Follow goals in the order provided (no optimization)

👉 Problem:

When multiple destinations are given (e.g., 10 rooms), the robot may follow a non-optimal route, leading to unnecessary time and energy consumption.

🎯 Project Objective

This project aims to build an intelligent navigation system that can:

📍 Accept multiple target locations
🧠 Optimize visiting order using Genetic Algorithm (GA)
🤖 Execute navigation autonomously using ROS 2 Nav2
🗺️ Operate in a realistic indoor simulation environment
🧠 2. Genetic Algorithm (Core Intelligence)
📌 Representation

Each chromosome represents a visiting order of rooms:

[Room4 → Room5 → Room11 → Room12]
🔬 Algorithm Workflow
5
🔄 Steps:
Initialize Population
Generate 50 random paths
Fitness Evaluation
Compute total travel distance
Objective: minimize distance
Selection
Select best-performing individuals
Crossover
Combine two parents to produce offspring
Mutation
Swap positions to avoid local minima
Elitism
Preserve best solutions
⚙️ GA Configuration
Component	Value
Population Size	50
Crossover	32
Mutation	14
Random Injection	4
Selection	Top 50
📈 Output
Optimal visiting sequence
Minimum total distance
🗺️ 3. Simulation Environment
🏥 Gazebo Hospital World
7
Environment: aws_robomaker_hospital
Structured indoor environment
Realistic obstacles and corridors
🧭 RViz Visualization
7

Displays:

Map
Costmap (Obstacle + Inflation)
Robot pose
Planned path
Laser scan data
🖥️ 4. GUI System (Human Interaction Layer)
7
🎮 Features:
Select multiple rooms
Display selected queue
Run Genetic Algorithm
Visualize optimized path
Send sequential goals to Nav2
🧱 5. System Architecture
+--------------------------------------------------+
|                  USER (GUI)                      |
|   Select Rooms → Run GA → Execute Navigation     |
+--------------------------+-----------------------+
                           |
                           v
+--------------------------------------------------+
|             Genetic Algorithm Layer              |
|  - Population Generation                         |
|  - Fitness Evaluation                            |
|  - Crossover / Mutation                          |
+--------------------------+-----------------------+
                           |
                           v
+--------------------------------------------------+
|                NAV2 STACK                        |
|  - Planner Server (NavFn / A*)                   |
|  - Controller Server (DWB)                       |
|  - Behavior Tree Navigator                       |
+--------------------------+-----------------------+
                           |
                           v
+--------------------------------------------------+
|           Robot (Gazebo Simulation)              |
|  - LiDAR                                        |
|  - IMU                                          |
|  - Odometry                                     |
+--------------------------------------------------+
📁 6. Project Structure
ros2_ws_project_demo/
├── src/robot_omni/
│
│   ├── config/
│   │   ├── nav2_para.yaml
│   │   ├── ekf_para.yaml
│   │   └── bridge_config.yaml
│
│   ├── launch/
│   │   ├── master_launch.py
│   │   ├── navigation.launch.py
│   │   ├── localization.launch.py
│   │   └── gazebo_control.launch.py
│
│   ├── maps/
│   │   ├── my_map.yaml
│   │   └── my_map.pgm
│
│   ├── urdf/
│   │   └── omni_base.urdf
│
│   ├── worlds/
│   │   └── hospital_full.world
│
│   ├── navGUI.py
│   ├── genetic_Algorithm.ipynb
│   ├── my_nav_recovery.xml
│
├── build/
├── install/
└── log/
⚙️ 7. Installation & Setup
🔧 Requirements
Ubuntu 24.04
ROS 2 Jazzy
Nav2
Gazebo Sim
🛠️ Build Instructions
git clone <your-repo>
cd ros2_ws_project_demo

colcon build
source install/setup.bash
▶️ 8. Running the System
🚀 Launch full system
ros2 launch robot_omni master_launch.py
🎮 Optional: Teleoperation
ros2 launch robot_omni teleop.launch.py
🧠 Run GUI
python3 navGUI.py
🔬 9. Experimental Results
📊 Example Scenario
Input: Multiple selected rooms
Output: Optimized visiting order
Total path length: ~44.15 meters
🧠 Key Insights
Genetic Algorithm significantly reduces total path length
Nav2 ensures smooth, collision-free navigation
Combination = efficient + intelligent navigation
⚠️ 10. Challenges & Solutions
Issue	Solution
Frequent path updates	Tune planner_frequency
Robot gets stuck	Implement recovery behaviors
TF errors	Ensure full chain: map → odom → base_link
Noisy costmap	Adjust inflation parameters
🚀 11. Future Work
Dynamic obstacle avoidance (AI-based)
Multi-robot coordination
Real-world deployment
Semantic navigation (room labeling)
👨‍💻 12. Author

Designed and implemented with a focus on real-world robotic intelligence and optimization.
