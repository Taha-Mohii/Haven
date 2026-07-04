import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DB_URL)

#patients
def create_patient(name,age,condition,username,password_hash,medivault_patient_id=None):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO haven_patients
        (name,age,condition,username,password_hash,medivault_patient_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (name, age, condition,username, password_hash, medivault_patient_id))
    patient_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return patient_id

def get_patient_by_username(username):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM haven_patients WHERE username = %s", (username,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_patient_by_id(patient_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM haven_patients WHERE id = %s", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    return row

#conversations
def save_message(patient_id,role,message):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conversations (patient_id, role, message)
        VALUES (%s, %s, %s)
    """, (patient_id, role, message))
    conn.commit()
    conn.close()

def get_conversations(patient_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, message FROM conversations
        WHERE patient_id = %s
        ORDER BY timestamp ASC
    """, (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

#moods

def save_mood(patient_id, score, note):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO moods (patient_id, score, note)
        VALUES (%s, %s, %s)
    """, (patient_id,score,note))
    conn.commit()
    conn.close()

def get_moods(patient_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT score, note, timestamp FROM moods
        WHERE patient_id = %s
        ORDER BY timestamp DESC
        LIMIT 10
    """, (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

#legacy

def save_legacy(patient_id, type, recipient_name, recipient_email, recipient_phone,title, content, scheduled_date=None):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO legacy 
        (patient_id, type, recipient_name, recipient_email, recipient_phone, title, content, scheduled_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (patient_id, type, recipient_name, recipient_email, recipient_phone, title, content, scheduled_date))
    conn.commit()
    conn.close()

def get_legacy(patient_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM legacy WHERE patient_id = %s
        ORDER BY created_at DESC
    """, (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_legacy_entry(entry_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM legacy WHERE id = %s", (entry_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def delete_legacy(entry_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM legacy WHERE id = %s", (entry_id,))
    conn.commit()
    conn.close()

#Activity log

def update_activity(patient_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO activity_log (patient_id, last_seen)
        VALUES (%s, NOW())
        ON CONFLICT (patient_id) DO UPDATE
        SET last_seen = NOW() , reminder_sent = FALSE
    """, (patient_id,))
    conn.commit()
    conn.close()

def get_activity(patient_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM activity_log WHERE patient_id = %s",(patient_id,))
    row = cursor.fetchone()
    conn.close()
    return row
