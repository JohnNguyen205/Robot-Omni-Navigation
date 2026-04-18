# ROS 2 Omni-Directional Robot Navigation Project

<div align="center">
  <p>An advanced autonomous navigation system featuring an omni-directional robot exploring a dynamic hospital simulation, heavily powered by ROS 2, Nav2, and custom AI Genetic Algorithms for optimal multi-destination pathing.</p>
</div>

---

## 📖 Overview
This project simulates an **Omni-Directional Autonomous Delivery Robot** navigating within a complex hospital environment. It leverages **ROS 2**, **Gazebo Classic** for physical simulation, and **Nav2 (Navigation 2)** for trajectory planning, behavior trees, and dynamic obstacle avoidance.

The project is further enhanced with a custom **PyQt5 GUI application** that implements a **Genetic Algorithm (GA)**. This resolves the Traveling Salesperson Problem (TSP), allowing the robot to calculate and execute the most optimal route when tasked with visiting multiple rooms sequentially.

---

## 📂 Project Architecture

- **`src/robot_omni/`**: The Core ROS 2 Package:
  - `launch/`: Orchestration scripts (e.g., `master_launch.py`) to sequentially bring up Gazebo, Localization, and Nav2.
  - `urdf/`: The robot's kinematic model and hardware design description.
  - `worlds/`: The 3D hospital environment map for Gazebo.
  - `maps/` & `config/`: The generated 2D grid maps and tuning files for Nav2 controllers/planners.
  - `genetic_Algorithm.ipynb`: A research notebook detailing the Genetic Algorithm implementation.
- **`navGUI.py`**: A PyQt5-based graphical dashboard. Users interactively select target rooms, the app calculates the shortest round-trip path via GA, and directly interfaces with Nav2 `NavigateToPose` actions.
- **`move.sh`**: A bash script designed to dynamically move entities (e.g., *patient wheelchairs, scrub nurses*) inside Gazebo via `cmd_vel` topics, acting as **Dynamic Obstacles** to test the Nav2 Local Planner.
- **`my_nav_recovery.xml`**: A Behavior Tree framework that activates advanced safety fallbacks (like back-up, spin, and wait) when the robot detects imminent collisions or blocked corridors.
- **`room1.txt` & `room1.jpeg`**: Coordinate configurations and the top-down floor plan utilized strictly by the UI.

---

## 📸 System & Visualizations 
*(Drag & drop your provided screenshots into this README file to replace these image blocks)*

### 1. Gazebo Simulation & Workspace
A high-fidelity layout depicting hospitals tracks with dynamic and static obstacles.
> ![Gazebo Simulation showing the Hospital Setup](./gazebo_hospital.png) *(Note: Please save your Gazebo simulation image as "gazebo_hospital.png" in this folder)*

### 2. RViz Mapping & Nav2 Costmaps
Real-time display of the Occupancy Grid Map, Local/Global Costmaps (inflation layers), and trajectory planning arrows.
> ![RViz Nav2 Map and Trajectories](./rviz_map.png) *(Note: Please save your RViz mapping image as "rviz_map.png" in this folder)*

### 3. Path Planning Control Center (GUI)
The dispatcher application displays the `room1.jpeg` map alongside a Matplotlib queue. The internal TSP optimization dynamically renders the optimized connections.
> ![Path Planning Dashboard](./gui_dashboard.png) *(Note: Please save your GUI dashboard image as "gui_dashboard.png" in this folder)*

### 4. Genetic Algorithm Workflow
A visual breakdown (Population -> Crossover -> Mutation -> Selection) deployed inside the interface to bypass brute-force looping overheads. 
> ![Genetic Algorithm Diagram](./algorithm_chart.png) *(Note: Please save your Genetic Algorithm flowchart as "algorithm_chart.png" in this folder)*

---

## 💡 AI Optimization: Genetic Algorithm Routing

When medical staff dispatches the robot to deliver items across multiple locations (e.g., 5 rooms simultaneously), traversing sequentially in the order selected causes terrible time inefficiencies. Inside `navGUI.py`:

1. **Initializes Population**: Creates 50 randomized sequences of room visitations.
2. **Crossover & Mutation**: Splices parent sequences to create faster children paths, slightly mutating to avoid local distance minimums.
3. **Fitness Evaluation**: Evaluates routes based on standard Euclidean distances between mapping nodes (Doors and Room Centers).
4. **Execution**: The winning sequence executes node-by-node. The robot automatically traverses through sequences formatted as: `Entry Door` -> `Room Inside` -> `Target Center`.

---

## 🚀 Setup & Execution Guide

### Step 1: Build the Workspace
Open a fresh terminal, navigate to your workspace root, and build the custom package:
```bash
cd /home/tof/ros2_ws_project_demo
colcon build --symlink-install
source install/setup.bash
```

### Step 2: Launch the Core System
Utilize the built-in Master Launch script to bootstrap the whole simulation setup.
```bash
ros2 launch robot_omni master_launch.py
```
> **Internal Launch Sequence (with delays):**
> - *0 seconds:* Gazebo Simulator engages.
> - *5 seconds:* Localization parameters (Cartographer/AMCL) are deployed.
> - *10 seconds:* The Navigation 2 Server & RViz are fully loaded.

### Step 3: Trigger Dynamic Obstacles (Optional)
To test collision avoidance in real-time, open a **new terminal** and force Gazebo physics models (wheelchair, nurses) to randomly patrol the hallways.
```bash
cd /home/tof/ros2_ws_project_demo
chmod +x move.sh
./move.sh
```
> *You can press `Ctrl + C` in this terminal anytime to halt these entities.*

### Step 4: Run the Navigation Console (GUI)
Open a **third terminal**, source your current ROS 2 distribution variables, and launch the Dispatch App:
```bash
cd /home/tof/ros2_ws_project_demo
# Source ROS environment (ensure you select your matching distro: jazzy/iron/foxy)
source /opt/ros/jazzy/setup.bash  
source install/setup.bash
python3 navGUI.py
```

**Operating the Interface:**
1. Look at the left panel and click on specific rooms to add them to your priority queue.
2. If a mistake is made, press **"🗑️ CLEAR QUEUE"** (*Clear Queue*).
3. Once ready, press **"🚀 START NAVIGATION"** (*Run Path*). The algorithm computes the minimum travel distance within ~2 seconds and seamlessly pushes Nav2 waypoints!
