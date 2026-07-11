import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from database import get_conn
from delivery import send_email
from dotenv import load_dotenv

load_dotenv()

def check_activity():
    print(f"[{datetime.now()}] Running activity check...")
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id, p.name, p.username,
               a.last_seen, a.reminder_sent, a.letters_sent
        FROM haven_patients p
        JOIN activity_log a ON p.id = a.patient_id
    """)
    patients = cursor.fetchall()

    now = datetime.now()

    for patient in patients:
        patient_id = patient[0]
        patient_name = patient[1]
        last_seen = patient[3]
        reminder_sent = patient[4]
        letters_sent = patient[5]

        days_inactive = (now-last_seen).days

        if days_inactive >= 7 and not reminder_sent:
            cursor.execute("SELECT username FROM haven_patients WHERE id = %s", (patient_id,))
            row = cursor.fetchone()
            send_email(
                recipient_name = patient_name,
                recipient_email= row[0],
                patient_name="Haven",
                title = "We miss you",
                content = f"Dear {patient_name},\n\nHaven is here whenever you are ready. Take your time."
            )

            cursor.execute("UPDATE activity_log SET reminder_sent = TRUE WHERE patient_id = %s", (patient_id,))
            conn.commit()
            print(f"Reminder sent to {patient_name}")

            if days_inactive >= 14 and not letters_sent:
                deliver_all_legacy(cursor, conn, patient_id, patient_name)

        check_scheduled_letters(cursor, conn)

        conn.close()
        print("Activity check complete.")

def deliver_all_legacy(cursor, conn, patient_id, patient_name):
    cursor.execute("""
        SELECT id, recipient_name, recipient_email, recipient_phone, title, content
        FROM legacy
        WHERE patient_id = %s AND delivered = FALSE
    """, (patient_id,))
    entries = cursor.fetchall()

    for entry in entries:
        entry_id        = entry[0]
        recipient_name  = entry[1]
        recipient_email = entry[2]
        recipient_phone = entry[3]
        title           = entry[4]
        content         = entry[5]
        access_token    = entry[6]

        delivered = False

        if recipient_email:
            success = send_email(recipient_name, recipient_email, patient_name, title, content)
            if success:
                delivered = True

        if recipient_phone:
            from delivery import send_whatsapp
            success = send_whatsapp(recipient_phone, patient_name, title)
            if success:
                delivered = True

        if delivered:
            cursor.execute("UPDATE legacy SET delivered = TRUE WHERE id = %s", (entry_id,))
            conn.commit()
            print(f"Legacy letter '{title}' delivered.")

    cursor.execute("UPDATE activity_log SET letters_sent = TRUE WHERE patient_id = %s", (patient_id,))
    conn.commit()


def check_scheduled_letters(cursor, conn):
    today = datetime.now().date()
    cursor.execute("""
    SELECT l.id, l.recipient_name, l.recipient_email,
           l.recipient_phone, l.title, l.content, l.access_token, p.name
    FROM legacy l
    JOIN haven_patients p ON l.patient_id = p.id
    WHERE l.scheduled_date = %s AND l.delivered = FALSE
""", (today,))
    entries = cursor.fetchall()

    for entry in entries:
        entry_id        = entry[0]
        recipient_name  = entry[1]
        recipient_email = entry[2]
        recipient_phone = entry[3]
        title           = entry[4]
        content         = entry[5]
        access_token    = entry[6]
        patient_name    = entry[7]

        delivered = False

        if recipient_email:
            access_token = entry[6] if len(entry) > 6 else None
            success = send_email(recipient_name, recipient_email, patient_name, title, content, access_token)
            if success:
                delivered = True

        if recipient_phone:
            from delivery import send_whatsapp
            success = send_whatsapp(recipient_phone, patient_name, title)
            if success:
                delivered = True

        if delivered:
            cursor.execute("UPDATE legacy SET delivered = TRUE WHERE id = %s", (entry_id,))
            conn.commit()
            print(f"Scheduled letter '{title}' delivered.")

            
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_activity, "interval", hours=24)
    scheduler.start()
    print("Scheduler started — checking every 24 hours.")
    return scheduler

