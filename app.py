from flask import Flask, render_template, request, redirect, url_for, session
from database import (
    create_patient, get_patient_by_username,
    get_patient_by_id, update_activity
)

from security import hash_password, check_password
import os
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

from scheduler import start_scheduler
start_scheduler()


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "patient_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name   = request.form["name"].strip()
        age    = int(request.form["age"])
        condition= request.form["condition"].strip()
        username = request.form["username"].strip()
        password = request.form["password"]

        if get_patient_by_username(username):
            return render_template("register.html", error="Username already taken.")
        
        password_hash = hash_password(password)
        patient_id = create_patient(name,age,condition, username,password_hash)

        session["patient_id"] = patient_id
        session["patient_name"] = name
        update_activity(patient_id)
        return redirect(url_for("home"))
    
    return render_template("register.html")

@app.route("/login",methods=["GET" , "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        row = get_patient_by_username(username)
        if not row or not check_password(password, row[6]):
            return render_template("login.html", error= "Invalid username or password.")
        
        session["patient_id"] = row[0]
        session["patient_name"] = row[1]
        update_activity(row[0])
        return redirect(url_for("home"))
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/home")
@login_required
def home():
    patient = get_patient_by_id(session["patient_id"])
    update_activity(session["patient_id"])
    return render_template("home.html", patient=patient)

@app.route("/companion")
@login_required
def companion():
    from database import get_conversations
    from ai import get_ai_response
    history = get_conversations(session["patient_id"])
    return render_template("companion.html",history=history)

@app.route("/companion/send", methods=["POST"])
@login_required
def companion_send():
    from database import get_conversations , save_message
    from ai import get_ai_response

    user_message = request.form["message"].strip()
    if not user_message:
        return redirect(url_for("companion"))
    
    patient_id = session["patient_id"]
    save_message(patient_id, "user", user_message)

    history = get_conversations(patient_id)
    patient = get_patient_by_id(patient_id)
    ai_reply = get_ai_response(patient, history)

    save_message(patient_id, "assistant", ai_reply)

    return redirect(url_for("companion"))

@app.route("/mood", methods=["GET", "POST"])
@login_required
def mood():
    from database import save_mood, get_moods
    if request.method == "POST":
        score = int(request.form["score"])
        note  = request.form["note"].strip()
        save_mood(session["patient_id"], score ,note)
        return redirect(url_for("mood"))
    
    moods = get_moods(session["patient_id"])
    return render_template("mood.html",moods=moods)

@app.route("/legacy")
@login_required
def legacy():
    from database import get_legacy
    entries = get_legacy(session["patient_id"])
    return render_template("legacy.html", entries=entries)

@app.route("/legacy/write", methods=["GET" , "POST"])
@login_required
def legacy_write():
    from database import save_legacy
    if request.method == "POST":
        save_legacy(
            patient_id = session["patient_id"],
            type  = request.form["type"],
            recipient_name  = request.form["recipient_name"].strip(),
            recipient_email = request.form["recipient_email"].strip(),
            recipient_phone  = request.form["recipient_phone"].strip(),
            title   = request.form["title"].strip(),
            content  = request.form["content"].strip(),
            scheduled_date  = request.form["scheduled_date"] or None
        )
        return redirect(url_for("legacy"))
    return render_template("write.html")

@app.route("/legacy/view/<int:entry_id>")
@login_required
def legacy_view(entry_id):
    from database import get_legacy_entry
    entry = get_legacy_entry(entry_id)
    return render_template("view.html", entry=entry)


@app.route("/legacy/delete/<int:entry_id>")
@login_required
def legacy_delete(entry_id):
    from database import delete_legacy
    delete_legacy(entry_id)
    return redirect(url_for("legacy"))


@app.route("/settings")
@login_required
def settings():
    patient = get_patient_by_id(session["patient_id"])
    return render_template("settings.html", patient=patient)

@app.route("/")
def landing():
    return render_template("landing.html")

if __name__ == "__main__":
    app.run(debug=True)
