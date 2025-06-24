import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,
                             QTableWidget, QTableWidgetItem, QGroupBox, QComboBox)
from PyQt5.QtGui import QFont
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import graph_module as gm
import detection
import resolution
import data

class DeadlockGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deadlock Detection & Resolution System")
        self.setGeometry(100, 100, 1200, 650)
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()
        controls_layout = QVBoxLayout()

        # Set a larger font for all widgets
        font = QFont()
        font.setPointSize(12)
        self.setFont(font)

        # Priority method selection
        self.priority_method = QComboBox()
        self.priority_method.addItems(["Manual", "Runtime-based"])
        self.priority_method.currentIndexChanged.connect(self.toggle_priority_input)
        controls_layout.addWidget(QLabel("Priority Method"))
        controls_layout.addWidget(self.priority_method)

        self.p_input = QLineEdit()
        self.p_input.setPlaceholderText("Enter Process ID (e.g., P1)")
        self.p_priority = QLineEdit()
        self.p_priority.setPlaceholderText("Priority (1-10)")
        self.priority_label = QLabel("Priority (1-10)")

        controls_layout.addWidget(QLabel("Add Process"))
        controls_layout.addWidget(self.p_input)
        controls_layout.addWidget(self.priority_label)
        controls_layout.addWidget(self.p_priority)
        p_btn = QPushButton("Add Process")
        p_btn.clicked.connect(self.add_process)
        controls_layout.addWidget(p_btn)

        self.r_input = QLineEdit()
        self.r_input.setPlaceholderText("Enter Resource ID (e.g., R1)")
        controls_layout.addWidget(QLabel("Add Resource"))
        controls_layout.addWidget(self.r_input)
        r_btn = QPushButton("Add Resource")
        r_btn.clicked.connect(self.add_resource)
        controls_layout.addWidget(r_btn)

        a_btn = QPushButton("Allocate Resource")
        a_btn.clicked.connect(self.allocate)
        q_btn = QPushButton("Request Resource")
        q_btn.clicked.connect(self.request)
        controls_layout.addWidget(a_btn)
        controls_layout.addWidget(q_btn)

        detect_btn = QPushButton("Detect & Resolve Deadlock")
        detect_btn.setStyleSheet("background-color: orange")
        detect_btn.clicked.connect(self.detect)
        controls_layout.addWidget(detect_btn)

        # Show process metadata table
        show_table_btn = QPushButton("Show Process Metadata")
        show_table_btn.clicked.connect(self.show_metadata_table)
        controls_layout.addWidget(show_table_btn)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        # Table for process metadata
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Process ID", "Priority", "Runtime"])
        self.table.setFixedWidth(350)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.canvas)
        right_layout.addWidget(self.table)

        main_layout.addLayout(controls_layout)
        main_layout.addLayout(right_layout, stretch=1)
        self.setLayout(main_layout)

        # Initial toggle for priority input
        self.toggle_priority_input()

    def toggle_priority_input(self):
        if self.priority_method.currentText() == "Manual":
            self.p_priority.show()
            self.priority_label.show()
        else:
            self.p_priority.hide()
            self.priority_label.hide()

    def add_process(self):
        pid = self.p_input.text()
        priority = self.p_priority.text()
        runtime = 5  # Default runtime
        method = self.priority_method.currentText()
        if pid:
            gm.add_process(pid)
            if method == "Manual":
                try:
                    prio = int(priority) if priority else 5
                except ValueError:
                    prio = 5
            else:  # Runtime-based
                prio = max(1, 10 - runtime)
            data.process_metadata[pid] = {
                "priority": prio,
                "runtime": runtime
            }
            self.update_graph()
            self.update_metadata_table()

    def add_resource(self):
        rid = self.r_input.text()
        if rid:
            gm.add_resource(rid)
            self.update_graph()

    def allocate(self):
        pid = self.p_input.text()
        rid = self.r_input.text()
        if pid and rid:
            gm.allocate_resource(pid, rid)
            self.update_graph()

    def request(self):
        pid = self.p_input.text()
        rid = self.r_input.text()
        if pid and rid:
            gm.request_resource(pid, rid)
            self.update_graph()

    def detect(self):
        if detection.detect_deadlock():
            QMessageBox.warning(self, "Deadlock Detected", "Deadlock Detected! Resolving...")
            resolution.resolve_deadlock()
            self.update_graph()
            self.update_metadata_table()
        else:
            QMessageBox.information(self, "Safe", "No Deadlock Detected.")

    def update_graph(self):
        self.figure.clear()
        G = nx.DiGraph()
        for node, neighbors in data.rag.items():
            for neighbor in neighbors:
                G.add_edge(node, neighbor)
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, arrows=True)
        self.canvas.draw()

    def update_metadata_table(self):
        meta = data.process_metadata
        self.table.setRowCount(len(meta))
        for row, (pid, info) in enumerate(meta.items()):
            self.table.setItem(row, 0, QTableWidgetItem(str(pid)))
            self.table.setItem(row, 1, QTableWidgetItem(str(info.get("priority", ""))))
            self.table.setItem(row, 2, QTableWidgetItem(str(info.get("runtime", ""))))

    def show_metadata_table(self):
        self.update_metadata_table()
        self.table.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = DeadlockGUI()
    gui.show()
    sys.exit(app.exec_())