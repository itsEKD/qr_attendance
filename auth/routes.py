from flask import Blueprint, render_template, request, redirect, session, flash
import bcrypt
from config import users_col, schools_col # unified users collection

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

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert new student into users collection
        users_col.insert_one({
            "name": name,
            "email": email,
            "password": hashed.decode('utf-8'),
            "role": "student",
            "role_id": role_id,
            "verified": True,
            "school": school,
            "department": department
        })


        flash("✅ Registration successful!", "success")
        return redirect('/auth/login')

    # -------- GET REQUEST --------
    schools = list(schools_col.find({}, {"_id": 0}))

    return render_template(
        'register_student.html',
        schools=schools
    )



# -----------------------
# Login Route (Student & Lecturer)
# -----------------------
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        user = users_col.find_one({"email": email, "verified": True})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # Set session
            session['user_id'] = str(user['_id'])
            session['email'] = user['email']
            session['role'] = user['role']
            session['name'] = user['role_id']

            # Redirect based on role
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
