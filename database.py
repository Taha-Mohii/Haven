import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

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
    import uuid
    token = str(uuid.uuid4())
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO legacy 
        (patient_id, type, recipient_name, recipient_email, recipient_phone, title, content, scheduled_date,access_token)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, access_token
    """, (patient_id, type, recipient_name, recipient_email, recipient_phone, title, content, scheduled_date,token))
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result

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

def get_legacy_by_token(token):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.*, p.name as patient_name
        FROM legacy l
        JOIN haven_patients p ON l.patient_id = p.id
        WHERE l.access_token = %s
    """, (token,))
    row = cursor.fetchone()
    conn.close()
    return row

def delete_legacy(entry_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM legacy WHERE id = %s", (entry_id,))
    conn.commit()
    conn.close()

def update_legacy(entry_id, type, recipient_name, recipient_email, recipient_phone, title, content, scheduled_date=None):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE legacy
        SET type = %s,
            recipient_name = %s,
            recipient_email = %s,
            recipient_phone = %s,
            title = %s,
            content = %s,
            scheduled_date = %s
        WHERE id = %s
    """, (type, recipient_name, recipient_email, recipient_phone, title, content, scheduled_date, entry_id))
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

#dashboard
def get_dashboard_stats(patient_id):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM legacy WHERE patient_id = %s", (patient_id,))
    letter_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM conversations WHERE patient_id = %s", (patient_id,))
    message_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT score, note FROM moods 
        WHERE patient_id = %s 
        ORDER BY timestamp DESC LIMIT 1
    """, (patient_id,))
    last_mood = cursor.fetchone()

    cursor.execute("SELECT last_seen FROM activity_log WHERE patient_id = %s", (patient_id,))
    activity = cursor.fetchone()
    if activity:
        days_active = (datetime.now() - activity[0]).days
    else:
        days_active = 0

    conn.close()
    return {
        "letter_count"  : letter_count,
        "message_count" : message_count,
        "last_mood"     : last_mood,
        "days_active"   : days_active
    }

def update_patient(patient_id, name, age, condition):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE haven_patients
        SET name = %s , age = %s, condition = %s
        WHERE id = %s    
    """, (name, age, condition, patient_id))
    conn.commit()
    conn.close()

def update_password(patient_id, password_hash):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE haven_patients
        SET password_hash = %s
        WHERE id = %s
    """, (password_hash, patient_id))
    conn.commit()
    conn.close()