import flask
from flask import Flask, request, session, redirect, url_for, render_template, make_response
import hashlib
import json
import os
import random
import time
import datetime
from werkzeug.utils import secure_filename
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
import base64

# Initialize Flask app
app = Flask(__name__)
app.config["UPLOAD"] = "static/img"
DATA_FILE = "data.json"

# Load data from JSON
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as file:
        json.dump({"users": [], "courses": [], "chapters": [], "cookies": []}, file)

def load_data():
    with open(DATA_FILE, "r") as file:
        return json.load(file)

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def cookie_generator():
    return ''.join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(16))

def hash_password(password):
    h = hashlib.sha1()
    h.update(password.encode("utf-8"))
    return h.hexdigest()

def get_user_by_cookie(cookie):
    data = load_data()
    for entry in data["cookies"]:
        if entry["cookie"] == cookie:
            user_id = entry["user_id"]
            return next((u for u in data["users"] if u["id"] == user_id), None)
    return None

@app.route("/", methods=["GET"])
def home():
    return redirect("/about")

@app.route("/about", methods=["GET"])
def about():
    cookie = request.cookies.get("sessionid")
    user = get_user_by_cookie(cookie)

    if not user:
        return redirect("/login")

    return render_template("about.html", username=user["username"])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])

        data = load_data()
        user = next((u for u in data["users"] if u["username"] == username and u["password"] == password), None)

        if user:
            new_cookie = cookie_generator()
            data["cookies"].append({"cookie": new_cookie, "user_id": user["id"], "expires": time.time() + 3600})
            save_data(data)

            resp = make_response(redirect("/index"))
            resp.set_cookie("sessionid", new_cookie)
            return resp

        return "Invalid login. Please try again."

    return render_template("login.html")

@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        email = request.form["email"]
        password = hash_password(request.form["password"])

        data = load_data()
        if any(u["username"] == username for u in data["users"]):
            return "Username already exists."

        new_user = {
            "id": len(data["users"]) + 1,
            "name": name,
            "username": username,
            "email": email,
            "password": password,
        }
        data["users"].append(new_user)
        save_data(data)
        return redirect("/login")

    return render_template("registration.html")

@app.route("/index", methods=["GET"])
def index():
    cookie = request.cookies.get("sessionid")
    user = get_user_by_cookie(cookie)

    if not user:
        return redirect("/login")

    return render_template("index.html", username=user["username"])

@app.route("/logout", methods=["GET"])
def logout():
    cookie = request.cookies.get("sessionid")
    data = load_data()
    data["cookies"] = [c for c in data["cookies"] if c["cookie"] != cookie]
    save_data(data)

    resp = make_response(redirect("/login"))
    resp.set_cookie("sessionid", "", expires=0)
    return resp

@app.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot.html")

    if request.method == "POST":
        email = request.form.get("email")
        if not email:
            flash("Email is required.")
            return redirect("/forgot")

        if find_user_by_email(email):
            # Здесь вы можете отправить письмо для сброса пароля
            flash("A reset link has been sent to your email.")
        else:
            flash("Email not found.")

        return redirect("/forgot")

@app.route("/courses", methods=["GET"])
def courses():
    cookie = request.cookies.get("sessionid")
    user = get_user_by_cookie(cookie)

    if not user:
        return redirect("/login")

    data = load_data()
    return render_template("courses.html", courses=data["courses"], username=user["username"])

@app.route("/add_course", methods=["GET", "POST"])
def add_course():
    cookie = request.cookies.get("sessionid")
    user = get_user_by_cookie(cookie)

    if not user:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]

        data = load_data()
        new_course = {
            "id": len(data["courses"]) + 1,
            "title": title,
            "description": description,
        }
        data["courses"].append(new_course)
        save_data(data)
        return redirect("/courses")

    return render_template("add_course.html", username=user["username"])

@app.route("/add_chapter", methods=["GET", "POST"])
def add_chapter():
    cookie = request.cookies.get("sessionid")
    user = get_user_by_cookie(cookie)

    if not user:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        course_id = int(request.form["course_id"])
        content = request.form["content"]

        data = load_data()
        new_chapter = {
            "id": len(data["chapters"]) + 1,
            "course_id": course_id,
            "title": title,
            "content": content,
        }
        data["chapters"].append(new_chapter)
        save_data(data)
        return redirect(f"/course/{course_id}")

    data = load_data()
    return render_template("add_chapter.html", courses=data["courses"], username=user["username"])

@app.route("/course/<int:course_id>", methods=["GET"])
def course_detail(course_id):
    cookie = request.cookies.get("sessionid")
    user = get_user_by_cookie(cookie)

    if not user:
        return redirect("/login")

    data = load_data()
    course = next((c for c in data["courses"] if c["id"] == course_id), None)
    if not course:
        return "Course not found"

    chapters = [ch for ch in data["chapters"] if ch["course_id"] == course_id]
    return render_template("course_detail.html", course=course, chapters=chapters, username=user["username"])

@app.route('/favicon.ico')
def favicon():
    return '', 204

# Dynamically load remaining templates
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
remaining_templates = [f for f in os.listdir(template_dir) if f.endswith('.html') and f not in ["about.html", "login.html", "registration.html", "index.html", "courses.html", "add_course.html", "add_chapter.html", "course_detail.html"]]

def create_route(template):
    route_name = template.replace('.html', '')

    @app.route(f'/{route_name}', endpoint=route_name)
    def dynamic_template(username=None, template_name=template):
        cookie = request.cookies.get("sessionid")
        user = get_user_by_cookie(cookie)
        if not user:
            return redirect("/login")
        return render_template(template_name, username=user["username"])

for template in remaining_templates:
    create_route(template)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

@app.route("/courses_csh", methods=["GET"])
def courses_csh_section():
    cookie = request.cookies.get("sessionid")
    user = get_user_by_cookie(cookie)

    if not user:
        return redirect("/login")
    pass
    return redirect(url_for('courses') + "#section")

@app.route("/courses_go", methods=["GET"])
def courses_go_section():
    cookie = request.cookies.get("sessionid")
    user = get_user_by_cookie(cookie)

    if not user:
        return redirect("/login")

    return redirect(url_for('courses') + "#section")

@app.route("/courses_backend", methods=["GET"])
def courses_backend_section():
    cookie = request.cookies.get("sessionid")
    user = get_user_by_cookie(cookie)

    if not user:
        return redirect("/login")

    return redirect(url_for('courses') + "#section")

@app.route("/courses_sql", methods=["GET"])
def courses_sql_section():
    cookie = request.cookies.get("sessionid")
    user = get_user_by_cookie(cookie)

    if not user:
        return redirect("/login")

    return redirect(url_for('courses') + "#section")

@app.route("/courses_python", methods=["GET"])
def courses_python_section():
    cookie = request.cookies.get("sessionid")
    user = get_user_by_cookie(cookie)

    if not user:
        return redirect("/login")

    return redirect(url_for('courses') + "#section")
