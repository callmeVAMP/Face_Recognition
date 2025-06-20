import mysql.connector
from datetime import datetime

db_config={
    'host':'localhost',
    'user':'root',
    'password':'Varsha@123',
    'database':'FaceAttendance'
}

def get_connection():
    return mysql.connector.connect(**db_config)

def add_student_to_db(name,roll_no,image_path):
    conn  = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO students (name,roll_no,image_path) VALUES (%s,%s,%s)",
            (name,roll_no,image_path)
        )
        conn.commit()
    except mysql.connector.IntegrityError:
        print(f"[!]Roll number '{roll_no}' already exists")
    finally:
        cursor.close()
        conn.close()


def mark_attendance(roll_no):
    conn = get_connection()
    cursor =conn.cursor()

    try:
        cursor.execute("SELECT id FROM students WHERE roll_no = %s",(roll_no,))
        result = cursor.fetchone()
        if result is None:
            print(f"[!] No student found with roll_no: {roll_no}")
            return 
        student_id = result[0]
        today = datetime.now().date()
        cursor.execute(
            "SELECT * from attendance WHERE student_id = %s AND date =%s",(student_id,today)
        )
        already_marked = cursor.fetchone()

        if not already_marked:
            now = datetime.now()
            cursor.execute(
                "INSERT INTO attendance (student_id, date, time) VALUES (%s, %s, %s)",
                (student_id, now.date(), now.time())
            )
            conn.commit()
            print(f"[✔] Attendance marked for {roll_no} at {now.time()}")
        else:
            print(f"[ℹ] Already marked today for {roll_no}")
    finally:
        cursor.close()
        conn.close()


def fetch_attendance():
    conn  = get_connection()
    cursor= conn.cursor()
    cursor.execute("""
        SELECT s.roll_no, a.date, a.time 
        FROM attendance a 
        JOIN students s ON a.student_id = s.id 
        ORDER BY a.date DESC, a.time DESC
    """)
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return records