import sys
import random
import string
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QListWidget,
                             QListWidgetItem, QStackedWidget, QStackedLayout, QSizePolicy)
from PyQt5.QtGui import QFont, QPixmap, QMovie
from PyQt5.QtCore import Qt, QSize

# Connect to the database
from db import init_db, add_group, add_task, get_tasks, update_task_status
init_db()

def generate_invite_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

class LoginPage(QWidget):
    def __init__(self, parent=None):
        super(LoginPage, self).__init__(parent)
        self.initUI()
        
    def initUI(self):
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Transparent container for widgets on top of background
        content_widget = QWidget(self)
        content_widget.setAttribute(Qt.WA_TranslucentBackground)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # Logo animation
        self.logo_label = QLabel()
        movie = QMovie('/Users/mirelaminkova/custom_projects/my_chores_app/my_tasks/pics/logo.gif')
        movie.setScaledSize(QSize(500, 500))
        self.logo_label.setMovie(movie)
        movie.start()
        self.logo_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.logo_label)

        # Title
        title = QLabel("Welcome to The Chores App")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title)

        # Username input
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter your username")
        content_layout.addWidget(self.username_edit)

        # Button layout
        btn_layout = QHBoxLayout()
        self.create_group_btn = QPushButton("Create Group")
        self.join_group_btn = QPushButton("Join Group")
        self.my_groups_btn = QPushButton("My Groups")
        btn_layout.addWidget(self.create_group_btn)
        btn_layout.addWidget(self.join_group_btn)
        btn_layout.addWidget(self.my_groups_btn)
        content_layout.addLayout(btn_layout)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(content_widget)
        main_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(main_layout)

class GroupCreationPage(QWidget):
    def __init__(self, parent=None):
        super(GroupCreationPage, self).__init__(parent)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.back_btn = QPushButton("← Back")
        self.back_btn.setFixedWidth(80)
        layout.addWidget(self.back_btn)
        
        title = QLabel("Create a Group")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.group_name_edit = QLineEdit()
        self.group_name_edit.setPlaceholderText("Enter group name")
        layout.addWidget(self.group_name_edit)
        
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
        
        self.invite_code_edit = QLineEdit()
        self.invite_code_edit.setPlaceholderText("Enter invite code")
        layout.addWidget(self.invite_code_edit)
        
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
        
        # Add back button
        self.back_btn = QPushButton("← Back")
        self.back_btn.setFixedWidth(80)
        layout.insertWidget(0, self.back_btn)
        
        self.group_info_label = QLabel("")
        self.group_info_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.group_info_label)
        
        self.invite_label = QLabel("")
        self.invite_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.invite_label)
        
        self.task_list = QListWidget()
        layout.addWidget(self.task_list)
        self.task_list.itemChanged.connect(self.handle_task_changed)
        self.task_list.itemClicked.connect(self.show_remove_button)
        self.remove_task_btn = QPushButton("Remove Task")
        self.remove_task_btn.setVisible(False)
        layout.insertWidget(1, self.remove_task_btn)  # Add it after the Back button
        self.remove_task_btn.clicked.connect(self.handle_remove_clicked)
        self.item_to_remove = None
        
        add_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter new task")
        self.add_task_btn = QPushButton("Add Task")
        add_layout.addWidget(self.task_input)
        add_layout.addWidget(self.add_task_btn)
        layout.addLayout(add_layout)
        
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
                item.setData(Qt.UserRole, task[0])
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                if task[2]:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
                self.task_list.addItem(item)
                
    def handle_task_changed(self, item):
        task_id = item.data(Qt.UserRole)
        new_state = 1 if item.checkState() == Qt.Checked else 0
        update_task_status(task_id, new_state)

    def show_remove_button(self, item):
            if item.checkState() == Qt.Checked:
                self.item_to_remove = item
                self.remove_task_btn.setVisible(True)
            else:
                self.remove_task_btn.setVisible(False)
                self.item_to_remove = None

    def handle_remove_clicked(self):
        if not self.item_to_remove:
            return
        item = self.item_to_remove
        task_id = item.data(Qt.UserRole)
        import sqlite3
        conn = sqlite3.connect('chores.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
        self.task_list.takeItem(self.task_list.row(item))
        self.remove_task_btn.setVisible(False)
        self.item_to_remove = None

class UserGroupsPage(QWidget):
    def __init__(self, parent=None):
        super(UserGroupsPage, self).__init__(parent)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("Existing Groups")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.groups_list = QListWidget()
        layout.addWidget(self.groups_list)
        self.groups_list.itemClicked.connect(self.handle_item_click)
        self.last_clicked_item = None
        self.delete_group_btn = QPushButton("Delete Group")
        self.delete_group_btn.setVisible(False)
        layout.addWidget(self.delete_group_btn)
        
        btn_layout = QHBoxLayout()
        self.open_group_btn = QPushButton("Open Group")
        self.join_group_btn = QPushButton("Join Group")
        self.create_group_btn = QPushButton("Create New Group")
        btn_layout.addWidget(self.open_group_btn)
        btn_layout.addWidget(self.join_group_btn)
        btn_layout.addWidget(self.create_group_btn)
        layout.addLayout(btn_layout)
        
        self.back_btn = QPushButton("← Back")
        layout.addWidget(self.back_btn)
        
    def refresh_groups(self, username):
        self.groups_list.clear()
        import sqlite3
        conn = sqlite3.connect('chores.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ug.group_id, g.group_name, g.invite_code
            FROM user_groups ug JOIN groups g ON ug.group_id = g.id
            WHERE ug.username = ?
        ''', (username,))
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            group_id, group_name, invite_code = row
            item = QListWidgetItem(f"{group_name} ({invite_code})")
            item.setData(Qt.UserRole, (group_id, group_name, invite_code))
            self.groups_list.addItem(item)

    def handle_item_click(self, item):
        if self.last_clicked_item == item:
            self.delete_group_btn.setVisible(True)
            self.current_item_to_delete = item
        else:
            self.delete_group_btn.setVisible(False)
            self.current_item_to_delete = None
        self.last_clicked_item = item

class MainWindow(QStackedWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Initialize pages
        self.login_page = LoginPage()
        self.group_creation_page = GroupCreationPage()
        self.group_creation_page.back_btn.clicked.connect(self.go_back)
        self.join_group_page = JoinGroupPage()
        self.user_groups_page = UserGroupsPage()
        self.task_manager_page = TaskManagerPage()
        
        # Add pages to the stack
        self.addWidget(self.login_page)
        self.addWidget(self.group_creation_page)
        self.addWidget(self.join_group_page)
        self.addWidget(self.user_groups_page)
        self.addWidget(self.task_manager_page)
        
        # Set previous page tracker
        self.previous_page = self.login_page
        
        # Connect signals
        self.login_page.create_group_btn.clicked.connect(self.goto_group_creation)
        self.login_page.join_group_btn.clicked.connect(self.goto_join_group)
        self.login_page.my_groups_btn.clicked.connect(self.goto_user_groups)
        self.group_creation_page.create_btn.clicked.connect(self.create_group)
        self.task_manager_page.add_task_btn.clicked.connect(self.add_task)
        self.join_group_page.join_btn.clicked.connect(self.handle_join_group)
        self.user_groups_page.back_btn.clicked.connect(self.go_back)
        self.task_manager_page.back_btn.clicked.connect(self.go_back)
        self.user_groups_page.create_group_btn.clicked.connect(self.goto_group_creation)
        self.user_groups_page.join_group_btn.clicked.connect(self.goto_join_group)
        self.user_groups_page.open_group_btn.clicked.connect(self.open_selected_group)
        self.user_groups_page.delete_group_btn.clicked.connect(self.delete_selected_group)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #FFB6C1;
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
    
    def goto_user_groups(self):
        username = self.login_page.username_edit.text().strip()
        if username:
            self.current_username = username
            import sqlite3
            conn = sqlite3.connect('chores.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM user_groups WHERE username = ?', (username,))
            count = cursor.fetchone()[0]
            conn.close()
            if count > 0:
                self.user_groups_page.refresh_groups(username)
                self.previous_page = self.login_page
                self.setCurrentWidget(self.user_groups_page)
            else:
                self.previous_page = self.login_page
                self.setCurrentWidget(self.group_creation_page)
        else:
            self.login_page.username_edit.setPlaceholderText("Please enter a username!")
    
    def create_group(self):
        group_name = self.group_creation_page.group_name_edit.text().strip()
        if group_name:
            invite_code = generate_invite_code()
            group_id = add_group(group_name, invite_code)
            import sqlite3
            conn = sqlite3.connect('chores.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO user_groups (username, group_id) VALUES (?, ?)',
                           (self.login_page.username_edit.text().strip(), group_id))
            conn.commit()
            conn.close()
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
            self.task_manager_page.task_list.clear()
            tasks = get_tasks(self.current_group_id)
            for task in tasks:
                item = QListWidgetItem(task[1])
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                if task[2]:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
                item.setData(Qt.UserRole, task[0])
                self.task_manager_page.task_list.addItem(item)
            self.task_manager_page.task_input.clear()
    
    def open_selected_group(self):
        selected_item = self.user_groups_page.groups_list.currentItem()
        if selected_item:
            data = selected_item.data(Qt.UserRole)
            if data:
                group_id, group_name, invite_code = data
                self.previous_page = self.user_groups_page
                self.task_manager_page.update_group_info(group_name, invite_code, group_id)
                self.current_group_id = group_id
                self.setCurrentWidget(self.task_manager_page)

    def delete_selected_group(self):
        item = self.user_groups_page.current_item_to_delete
        if not item:
            return
        group_data = item.data(Qt.UserRole)
        if group_data:
            group_id, _, _ = group_data
            import sqlite3
            conn = sqlite3.connect('chores.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE group_id = ?', (group_id,))
            cursor.execute('DELETE FROM user_groups WHERE group_id = ?', (group_id,))
            cursor.execute('DELETE FROM groups WHERE id = ?', (group_id,))
            conn.commit()
            conn.close()
            self.user_groups_page.groups_list.takeItem(self.user_groups_page.groups_list.row(item))
            self.user_groups_page.delete_group_btn.setVisible(False)
    
    def go_back(self):
        if self.previous_page != self.currentWidget():
            self.setCurrentWidget(self.previous_page)
        else:
            self.setCurrentWidget(self.login_page)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("The Chores App")
    window.resize(200, 550)
    window.show()
    sys.exit(app.exec_())