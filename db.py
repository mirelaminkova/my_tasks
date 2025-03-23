import sqlite3

DB_NAME = 'chores.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create table for groups
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL,
            invite_code TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Create table for tasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            task_text TEXT NOT NULL,
            is_done INTEGER DEFAULT 0,
            FOREIGN KEY(group_id) REFERENCES groups(id)
        )
    ''')
    
    # Create table for user_groups
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            group_id INTEGER,
            FOREIGN KEY(group_id) REFERENCES groups(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_group(group_name, invite_code):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO groups (group_name, invite_code)
        VALUES (?, ?)
    ''', (group_name, invite_code))
    conn.commit()
    group_id = cursor.lastrowid
    conn.close()
    return group_id

def add_task(group_id, task_text):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (group_id, task_text)
        VALUES (?, ?)
    ''', (group_id, task_text))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id

def get_tasks(group_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, task_text, is_done FROM tasks WHERE group_id = ?', (group_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def update_task_status(task_id, new_state):
    import sqlite3
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET is_done = ? WHERE id = ?', (new_state, task_id))
    conn.commit()
    conn.close()