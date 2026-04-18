import sys
import yaml
import math
import random
import threading
import time

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QLabel, QPushButton, QListWidget, 
                             QGroupBox, QScrollArea, QFrame, QGridLayout)
from PyQt5.QtGui import QPixmap, QColor, QPalette
from PyQt5.QtCore import Qt, pyqtSignal, QObject, pyqtSlot

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose

# ---------------------------------------------------------
# Plot Canvas
# ---------------------------------------------------------
class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.patch.set_facecolor('#1e1e2e')
        self.axes = fig.add_subplot(111)
        self.axes.set_facecolor('#1e1e2e')
        self.axes.tick_params(colors='#cdd6f4')
        self.axes.xaxis.label.set_color('#cdd6f4')
        self.axes.yaxis.label.set_color('#cdd6f4')
        self.axes.title.set_color('#cdd6f4')
        for spine in self.axes.spines.values():
            spine.set_edgecolor('#45475a')
        super(PlotCanvas, self).__init__(fig)

# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------
def euler_to_quaternion(yaw, pitch=0, roll=0):
    qx = math.sin(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) - math.cos(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
    qy = math.cos(roll/2) * math.sin(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.cos(pitch/2) * math.sin(yaw/2)
    qz = math.cos(roll/2) * math.cos(pitch/2) * math.sin(yaw/2) - math.sin(roll/2) * math.cos(pitch/2) * math.cos(yaw/2)
    qw = math.cos(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
    return [qx, qy, qz, qw]

def optimize_room_order(selected_rooms, rooms_data):
    num_points = len(selected_rooms)
    if num_points <= 1:
        return selected_rooms, 0.0

    start_pos = (0.0, 12.0)

    def get_coords(room_name):
        p = rooms_data[room_name].get('center', rooms_data[room_name].get('door', {'x':0, 'y':0}))
        return (float(p['x']), float(p['y']))

    def total_cost(route):
        first_p = get_coords(selected_rooms[route[0]])
        cost = math.sqrt((start_pos[0] - first_p[0])**2 + (start_pos[1] - first_p[1])**2)
        for i in range(num_points - 1):
            p1 = get_coords(selected_rooms[route[i]])
            p2 = get_coords(selected_rooms[route[i+1]])
            cost += math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        return cost

    population_size = 50
    population = [random.sample(range(num_points), num_points) for _ in range(population_size)]
    
    start_time = time.time()
    while (time.time() - start_time) < 2.0:
        population.sort(key=total_cost)
        new_pop = population[:10]
        while len(new_pop) < population_size:
            p1, p2 = random.sample(population[:25], 2)
            child = p1[:num_points//2] + [g for g in p2 if g not in p1[:num_points//2]]
            if random.random() < 0.1:
                idx1, idx2 = random.sample(range(num_points), 2)
                child[idx1], child[idx2] = child[idx2], child[idx1]
            new_pop.append(child)
        population = new_pop
        QApplication.processEvents()

    population.sort(key=total_cost)
    best_route = population[0]
    return [selected_rooms[i] for i in best_route], total_cost(best_route)

# ---------------------------------------------------------
# ROS 2 Operations Node
# ---------------------------------------------------------
class NavNode(Node, QObject):
    goal_status_signal = pyqtSignal(str, bool)
    sequence_finished_signal = pyqtSignal()

    def __init__(self):
        Node.__init__(self, 'navigation_gui_node')
        QObject.__init__(self)
        self.nav_to_pose_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.goals_queue = []
        self.is_navigating = False

    def start_navigation(self, sequence):
        self.goals_queue = sequence.copy()
        if not self.is_navigating and self.goals_queue:
            self.is_navigating = True
            self.send_next_goal()

    def send_next_goal(self):
        if not self.goals_queue:
            self.is_navigating = False
            self.sequence_finished_signal.emit()
            return

        goal_name, goal_pose = self.goals_queue.pop(0)
        if not self.nav_to_pose_client.wait_for_server(timeout_sec=5.0):
            self.goal_status_signal.emit("Server Error", False)
            self.is_navigating = False
            return

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = float(goal_pose['x'])
        goal_msg.pose.pose.position.y = float(goal_pose['y'])
        q = euler_to_quaternion(float(goal_pose.get('yaw', 0.0)))
        goal_msg.pose.pose.orientation.x, goal_msg.pose.pose.orientation.y, \
        goal_msg.pose.pose.orientation.z, goal_msg.pose.pose.orientation.w = q

        self.goal_status_signal.emit(f"Đang tới: {goal_name}", True)
        send_goal_future = self.nav_to_pose_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.is_navigating = False
            return
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(lambda f: self.send_next_goal())

# ---------------------------------------------------------
# Main GUI Window
# ---------------------------------------------------------
class NavigationWindow(QMainWindow):
    def __init__(self, ros_node, rooms_data, image_path):
        super().__init__()
        self.ros_node = ros_node
        self.rooms_data = rooms_data
        self.image_path = image_path
        self.selected_rooms = []
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        self.setWindowTitle("ROS 2 Robot Path Planning - Final Center Stop")
        self.setMinimumSize(1400, 850)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.image_label = QLabel()
        self.image_label.setStyleSheet("border: 2px solid #45475a; background: #181825; border-radius: 10px;")
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap.scaled(700, 700, Qt.KeepAspectRatio))
        main_layout.addWidget(self.image_label, 4)

        mid_panel = QGroupBox("🏨 Rooms & Queue")
        mid_layout = QVBoxLayout(mid_panel)
        self.queue_list = QListWidget()
        mid_layout.addWidget(self.queue_list)
        
        self.clear_btn = QPushButton("🗑️ XÓA HÀNG ĐỢI")
        self.clear_btn.setStyleSheet("background-color: #f38ba8; color: #11111b; margin-bottom: 10px;")
        self.clear_btn.clicked.connect(self.clear_queue)
        mid_layout.addWidget(self.clear_btn)

        btn_grid = QGridLayout()
        for i, (name, _) in enumerate(self.rooms_data.items()):
            btn = QPushButton(name.replace('_', ' ').title())
            btn.clicked.connect(lambda ch, n=name: self.add_room(n))
            btn_grid.addWidget(btn, i // 2, i % 2)
        mid_layout.addLayout(btn_grid)
        main_layout.addWidget(mid_panel, 3)

        right_panel = QVBoxLayout()
        self.ga_canvas = PlotCanvas(self)
        right_panel.addWidget(self.ga_canvas, 4)
        
        self.status_label = QLabel("Status: Idle")
        self.status_label.setWordWrap(True) # Cho phép Status hiển thị nhiều dòng
        self.status_label.setStyleSheet("font-weight: bold; color: #f9e2af; font-size: 14px;")
        right_panel.addWidget(self.status_label)

        self.start_btn = QPushButton("🚀 CHẠY LỘ TRÌNH")
        self.start_btn.setMinimumHeight(60)
        self.start_btn.clicked.connect(self.start_navigation)
        right_panel.addWidget(self.start_btn)
        
        main_layout.addLayout(right_panel, 5)

    def add_room(self, name):
        if name not in self.selected_rooms:
            self.selected_rooms.append(name)
            self.queue_list.addItem(f"📍 {name.replace('_', ' ').title()}")

    def clear_queue(self):
        self.selected_rooms.clear()
        self.queue_list.clear()
        self.ga_canvas.axes.clear()
        self.ga_canvas.draw()
        self.status_label.setText("Status: Queue Cleared")

    def plot_optimized_path(self, optimized_rooms, total_dist):
        ax = self.ga_canvas.axes
        ax.clear()
        self.queue_list.clear()
        for i, room in enumerate(optimized_rooms):
            self.queue_list.addItem(f"✅ Bước {i+1}: {room.replace('_', ' ').title()}")

        rx, ry = 0.0, 12.0
        x_pts, y_pts = [rx], [ry]
        for room in optimized_rooms:
            pos = self.rooms_data[room].get('center', {'x':0, 'y':0})
            x_pts.append(float(pos['x']))
            y_pts.append(float(pos['y']))

        ax.plot(x_pts, y_pts, color='#f9e2af', marker='o', markersize=8, markerfacecolor='#89b4fa', linewidth=2)
        ax.plot(rx, ry, 'r*', markersize=15, label='Start')
        ax.set_title(f"Lộ trình tối ưu (Tổng: {total_dist:.2f}m)", color='#cdd6f4')
        ax.grid(True, color='#45475a', linestyle='--')
        self.ga_canvas.draw()

    def start_navigation(self):
        if not self.selected_rooms: return
        
        self.status_label.setText("Status: Đang tối ưu lộ trình...")
        QApplication.processEvents()
        
        optimized, dist = optimize_room_order(self.selected_rooms, self.rooms_data)
        self.plot_optimized_path(optimized, dist)
        
        # Tạo chuỗi văn bản thông báo lộ trình
        path_str = " -> ".join([r.replace('_', ' ').title() for r in optimized])
        self.status_label.setText(f"Lộ trình: {path_str}\n(Tổng: {dist:.2f}m)")
        
        waypoint_seq = []
        num_rooms = len(optimized)
        
        for index, r in enumerate(optimized):
            r_data = self.rooms_data[r]
            name = r.replace('_', ' ').title()
            is_last_room = (index == num_rooms - 1)
            
            # 1. ĐI VÀO PHÒNG
            if 'door' in r_data:
                waypoint_seq.append((f"{name} (Vào - Door)", r_data['door']))
            if 'inside' in r_data:
                waypoint_seq.append((f"{name} (Vào - Inside)", r_data['inside']))
            if 'center' in r_data:
                waypoint_seq.append((f"{name} (Dừng - Center)", r_data['center']))
            
            # 2. ĐI RA KHỎI PHÒNG (Trừ phòng cuối)
            if not is_last_room:
                if 'inside' in r_data:
                    waypoint_seq.append((f"{name} (Ra - Inside)", r_data['inside']))
                if 'door' in r_data:
                    waypoint_seq.append((f"{name} (Ra - Door)", r_data['door']))
        
        # Cập nhật Status sau 2 giây để hiện thông báo bắt đầu di chuyển
        QTimer.singleShot(2000, lambda: self.ros_node.start_navigation(waypoint_seq))

    def connect_signals(self):
        self.ros_node.goal_status_signal.connect(lambda msg, nav: self.status_label.setText(f"Trạng thái: {msg}"))

from PyQt5.QtCore import QTimer

def main():
    rclpy.init()
    nav_node = NavNode()
    threading.Thread(target=rclpy.spin, args=(nav_node,), daemon=True).start()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    app.setStyleSheet("""
        QWidget { background: #1e1e2e; color: #cdd6f4; font-size: 13px; } 
        QPushButton { background: #89b4fa; color: #11111b; border-radius: 5px; padding: 5px; font-weight: bold; } 
        QPushButton:hover { background: #b4befe; }
        QListWidget { background: #313244; border: 1px solid #45475a; border-radius: 5px; }
    """)

    rooms_filepath = '/home/tof/ros2_ws_project_demo/room1.txt'
    image_filepath = '/home/tof/ros2_ws_project_demo/room1.jpeg'

    try:
        rooms_data = yaml.safe_load(open(rooms_filepath, 'r')).get('rooms', {})
    except:
        rooms_data = {}

    win = NavigationWindow(nav_node, rooms_data, image_filepath)
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()