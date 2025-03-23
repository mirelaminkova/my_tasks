import sys
import random
import string
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QListWidget,
                             QListWidgetItem, QStackedWidget)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

#connect to the database
from db import init_db
from db import init_db, add_group, add_task, get_tasks
init_db()

# create a random invite code for testing
def generate_invite_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

class LoginPage(QWidget):
    def __init__(self, parent=None):
        super(LoginPage, self).__init__(parent)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        # add logo image
        self.logo_label = QLabel()
        from PyQt5.QtGui import QPixmap
        pixmap = QPixmap('./pics/the_logo.png')
        

        mask = pixmap.createMaskFromColor(Qt.white)
        pixmap.setMask(mask)
        
        
        pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)
        self.setLayout(layout)
        
        
        title = QLabel("Welcome to The Chores App")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # username input
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter your username")
        layout.addWidget(self.username_edit)
        
        # Buttons for creating or joining a group
        btn_layout = QHBoxLayout()
        self.create_group_btn = QPushButton("Create Group")
        self.join_group_btn = QPushButton("Join Group")
        btn_layout.addWidget(self.create_group_btn)
        btn_layout.addWidget(self.join_group_btn)
        layout.addLayout(btn_layout)
        
class GroupCreationPage(QWidget):
    def __init__(self, parent=None):
        super(GroupCreationPage, self).__init__(parent)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Group creation title
        title = QLabel("Create a Group")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Input for group name
        self.group_name_edit = QLineEdit()
        self.group_name_edit.setPlaceholderText("Enter group name")
        layout.addWidget(self.group_name_edit)
        
        # Create group button
        self.create_btn = QPushButton("Create")
        layout.addWidget(self.create_btn)

class JoinGroupPage(QWidget):
    def __init__(self, parent=None):
        super(JoinGroupPage, self).__init__(parent)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Join an Existing Group")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Input for invite code
        self.invite_code_edit = QLineEdit()
        self.invite_code_edit.setPlaceholderText("Enter invite code")
        layout.addWidget(self.invite_code_edit)

        # Join group button
        self.join_btn = QPushButton("Join")
        layout.addWidget(self.join_btn)

class TaskManagerPage(QWidget):
    def __init__(self, parent=None):
        super(TaskManagerPage, self).__init__(parent)
        self.group_name = ""
        self.invite_code = ""
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # adding the optiion to go back to the login page
        self.back_btn = QPushButton("← Back")
        self.back_btn.setFixedWidth(80)
        layout.insertWidget(0, self.back_btn)
        
        # display group info
        self.group_info_label = QLabel("")
        self.group_info_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.group_info_label)
        
        # display invite code
        self.invite_label = QLabel("")
        layout.addWidget(self.invite_label)
        
        # task list widget to show tasks
        self.task_list = QListWidget()
        layout.addWidget(self.task_list)
        # toggle task completion on double-click
        self.task_list.itemDoubleClicked.connect(self.toggle_task_done)
        
        # layout to add new tasks
        add_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter new task")
        self.add_task_btn = QPushButton("Add Task")
        add_layout.addWidget(self.task_input)
        add_layout.addWidget(self.add_task_btn)
        layout.addLayout(add_layout)
        
    def toggle_task_done(self, item):
        # Toggle strike-through to mark task as completed
        font = item.font()
        font.setStrikeOut(not font.strikeOut())
        item.setFont(font)
        
    def update_group_info(self, group_name, invite_code, group_id=None):
        self.group_name = group_name
        self.invite_code = invite_code
        self.group_info_label.setText(f"Group: {group_name}")
        self.invite_label.setText(f"Invite Code: {invite_code}")
        if group_id is not None:
            self.group_id = group_id
            self.task_list.clear()
            tasks = get_tasks(group_id)
            for task in tasks:
                item = QListWidgetItem(task[1])
                if task[2]:
                    font = item.font()
                    font.setStrikeOut(True)
                    item.setFont(font)
                self.task_list.addItem(item)
        
class MainWindow(QStackedWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Initialize pages
        self.login_page = LoginPage()
        self.group_creation_page = GroupCreationPage()
        self.join_group_page = JoinGroupPage()  # NEW
        self.task_manager_page = TaskManagerPage()
        
        # Add pages to the stacked widget
        self.addWidget(self.login_page)
        self.addWidget(self.group_creation_page)
        self.addWidget(self.join_group_page)  # NEW
        self.addWidget(self.task_manager_page)
        
        # Initialize previous page tracker
        self.previous_page = self.login_page
        
        # Connect signals
        self.login_page.create_group_btn.clicked.connect(self.goto_group_creation)
        self.login_page.join_group_btn.clicked.connect(self.goto_join_group)  # UPDATED
        self.group_creation_page.create_btn.clicked.connect(self.create_group)
        self.task_manager_page.add_task_btn.clicked.connect(self.add_task)
        
        # Connect the join group page's join button
        self.join_group_page.join_btn.clicked.connect(self.handle_join_group)
        
        # Connect back button signal to a new go_back method
        self.task_manager_page.back_btn.clicked.connect(self.go_back)
        
        # Apply baby pink theme with style sheet
        self.setStyleSheet("""
            QWidget {
                background-color: #FFB6C1; /* baby pink */
                color: #333;
                font-family: Arial;
            }
            QLineEdit, QListWidget {
                background-color: #FFFFFF;
                border: 1px solid #ccc;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #FF69B4;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #FF1493;
            }
        """)
    
    def goto_group_creation(self):
        username = self.login_page.username_edit.text().strip()
        if username:
            self.previous_page = self.login_page
            self.setCurrentWidget(self.group_creation_page)
        else:
            self.login_page.username_edit.setPlaceholderText("Please enter a username!")

    def goto_join_group(self):
        username = self.login_page.username_edit.text().strip()
        if username:
            self.previous_page = self.login_page
            self.setCurrentWidget(self.join_group_page)
        else:
            self.login_page.username_edit.setPlaceholderText("Please enter a username!")

    def create_group(self):
        group_name = self.group_creation_page.group_name_edit.text().strip()
        if group_name:
            invite_code = generate_invite_code()
            # Save group to the database
            group_id = add_group(group_name, invite_code)
            # Update the task manager page with group info and load tasks
            self.task_manager_page.update_group_info(group_name, invite_code, group_id)
            self.current_group_id = group_id
            self.previous_page = self.group_creation_page
            self.setCurrentWidget(self.task_manager_page)
        else:
            self.group_creation_page.group_name_edit.setPlaceholderText("Enter a valid group name!")
    def handle_join_group(self):
        invite_code = self.join_group_page.invite_code_edit.text().strip()
        if invite_code:
            import sqlite3
            conn = sqlite3.connect('chores.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, group_name FROM groups WHERE invite_code = ? COLLATE NOCASE', (invite_code,))
            row = cursor.fetchone()
            conn.close()
            if row:
                group_id, group_name = row
                self.task_manager_page.update_group_info(group_name, invite_code, group_id)
                self.current_group_id = group_id
                self.previous_page = self.join_group_page
                self.setCurrentWidget(self.task_manager_page)
            else:
                self.join_group_page.invite_code_edit.clear()
                self.join_group_page.invite_code_edit.setPlaceholderText("Invalid code. Try again.")
        else:
            self.join_group_page.invite_code_edit.setPlaceholderText("Please enter an invite code!")

    def add_task(self):
        task_text = self.task_manager_page.task_input.text().strip()
        if task_text and hasattr(self, "current_group_id"):
            add_task(self.current_group_id, task_text)
            # Refresh the task list: clear and reload tasks from the DB
            self.task_manager_page.task_list.clear()
            tasks = get_tasks(self.current_group_id)
            for task in tasks:
                item = QListWidgetItem(task[1])
                if task[2]:
                    font = item.font()
                    font.setStrikeOut(True)
                    item.setFont(font)
                self.task_manager_page.task_list.addItem(item)
            self.task_manager_page.task_input.clear()

    def go_back(self):
        # Go back to the previous page
        self.setCurrentWidget(self.previous_page)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("The Chores App")
    window.resize(400, 600)
    window.show()
    sys.exit(app.exec_())