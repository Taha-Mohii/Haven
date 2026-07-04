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
    return render_template("companion.html")

@app.route("/mood")
@login_required
def mood():
    return render_template("mood.html")

@app.route("/legacy")
@login_required
def legacy():
    return render_template("legacy.html")

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
