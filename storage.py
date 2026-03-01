import sqlite3
import pandas as pd

DB_NAME = "timetable.db"

def connect():
    return sqlite3.connect(DB_NAME)

def initialize_storage():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        department TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        semester INTEGER NOT NULL,
        hours INTEGER NOT NULL,
        is_lab TEXT NOT NULL,
        lab_hours INTEGER NOT NULL,
        teacher_id INTEGER NOT NULL,
        FOREIGN KEY (teacher_id) REFERENCES teachers(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_name TEXT,
        room_type TEXT
    )
    """)

    conn.commit()
    conn.close()

# ------------------ TEACHERS ------------------

def add_teacher(name, department):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO teachers (name, department) VALUES (?, ?)",
        (name, department)
    )
    conn.commit()
    conn.close()

def get_all_teachers():
    conn = connect()
    df = pd.read_sql_query("SELECT * FROM teachers", conn)
    conn.close()
    return df

# ------------------ SUBJECTS ------------------

def add_subject(subject, semester, hours, is_lab, lab_hours, teacher_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO subjects 
    (subject, semester, hours, is_lab, lab_hours, teacher_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (subject, semester, hours, is_lab, lab_hours, int(teacher_id)))

    conn.commit()
    conn.close()

def get_all_subjects():
    conn = connect()

    query = """
    SELECT 
        s.id,
        s.subject,
        s.semester,
        s.hours,
        s.is_lab,
        s.lab_hours,
        t.name AS teacher
    FROM subjects s
    JOIN teachers t ON s.teacher_id = t.id
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
def delete_teacher(teacher_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
    conn.commit()
    conn.close()