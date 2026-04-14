from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from config import users_col, schools_col

auth = Blueprint('auth', __name__)


# -----------------------
# Student Registration
# -----------------------
@auth.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        email = request.form['email'].strip()
        name = request.form['name'].strip()
        role_id = request.form['role_id'].strip()
        password = request.form['password'].strip()
        school = request.form.get("school")
        department = request.form.get("department")

        if users_col.find_one({"email": email}):
            flash("⚠️ Email already registered", "error")
            return redirect('/auth/register_student')

        users_col.insert_one({
            "name": name,
            "email": email,
            "password": generate_password_hash(password),
            "role": "student",
            "role_id": role_id,
            "school": school,
            "department": department
        })

        flash("✅ Registration successful!", "success")
        return redirect('/auth/login')

    schools = list(schools_col.find({}, {"_id": 0}))
    return render_template('register_student.html', schools=schools)


# -----------------------
# Lecturer Registration
# -----------------------
@auth.route('/register_lecturer', methods=['GET', 'POST'])
def register_lecturer():
    if request.method == 'POST':
        if users_col.find_one({"email": request.form['email']}):
            flash("⚠️ Email already registered", "error")
            return redirect('/auth/register_lecturer')

        users_col.insert_one({
            "name": request.form['name'],
            "email": request.form['email'],
            "password": generate_password_hash(request.form['password']),
            "role": "lecturer",
            "role_id": request.form['role_id'],
            "school": request.form['school'],
            "departments": request.form.getlist('departments'),
        })

        flash("✅ Lecturer registered successfully!", "success")
        return redirect('/auth/login')

    schools = list(schools_col.find())
    for school in schools:
        school['_id'] = str(school['_id'])
    return render_template('register_lecturer.html', schools=schools)


# -----------------------
# Login Route (Student & Lecturer)
# -----------------------
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        user = users_col.find_one({"email": email})

        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['email'] = user['email']
            session['role'] = user['role']
            session['name'] = user['role_id']

            if user['role'] == 'lecturer':
                return redirect('/lecturer_dashboard')
            else:
                return redirect('/student_dashboard')

        flash("❌ Invalid email or password", "error")
        return redirect('/auth/login')

    return render_template('login.html')


# -----------------------
# Logout Route
# -----------------------
@auth.route('/logout')
def logout():
    session.clear()
    flash("✅ You have been logged out", "success")
    return redirect('/auth/login')