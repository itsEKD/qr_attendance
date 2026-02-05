from flask import Flask, render_template, send_file, request, session, redirect
from bson.objectid import ObjectId
from datetime import datetime
import qrcode
import uuid
import os
from openpyxl import Workbook
import tempfile


from config import users_col, sessions_col, attendance_col
from auth.routes import auth   # ✅ Blueprint import

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ✅ Register Blueprint
app.register_blueprint(auth, url_prefix='/auth')

# Ensure QR folder exists
os.makedirs("static/qr_codes", exist_ok=True)


# -----------------------
# Home
# -----------------------
@app.route('/')
def home():
    return render_template('home.html')


# -----------------------
# Lecturer Dashboard
# -----------------------

@app.route('/lecturer_dashboard')
def lecturer_dashboard():
    if session.get('role') != 'lecturer':
        return redirect('/auth/login')

    lecturer = users_col.find_one({
        "_id": ObjectId(session.get('user_id'))
    })

    departments = lecturer.get('departments', [])

    return render_template(
        'lecturer_dashboard.html',
        departments=departments,
        lecturer=lecturer
    )



# -----------------------
# Start Session (Generate QR)
# -----------------------
@app.route('/start_session', methods=['POST'])
def start_session():
    if session.get('role') != 'lecturer':
        return "❌ Unauthorized Access"

    course = request.form['course']
    token = str(uuid.uuid4())

    new_session = {
        "course": course,
        "token": token,
        "lecturer_id": session.get('user_id'),
        "start_time": datetime.now(),
        "active": True
    }

    result = sessions_col.insert_one(new_session)
    session_id = str(result.inserted_id)

    # Generate QR
    img = qrcode.make(token)
    img.save(f"static/qr_codes/{token}.png")

    # Go directly to marksheet
    return redirect(f"/marksheet/{session_id}")


# -----------------------
# Student Dashboard
# -----------------------
@app.route('/student_dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect('/auth/login')
    return render_template('student_dashboard.html')


# -----------------------
# Scan Page
# -----------------------
@app.route('/scan')
def scan():
    if session.get('role') != 'student':
        return redirect('/auth/login')
    return render_template('scan.html')


# -----------------------
# Mark Attendance (Student scans QR)
# -----------------------
@app.route('/mark_attendance/<token>')
def mark_attendance(token):
    if session.get('role') != 'student':
        return redirect('/auth/login')

    # Find active session
    session_data = sessions_col.find_one({
        "token": token,
        "active": True
    })

    if not session_data:
        return "❌ Session Expired or Invalid"

    session_id = str(session_data['_id'])

    # Prevent duplicate attendance
    already_marked = attendance_col.find_one({
        "session_id": session_id,
        "student_id": session.get('user_id')
    })

    if already_marked:
        return "⚠️ Attendance Already Marked"

    # Get student full data
    student = users_col.find_one({
        "_id": ObjectId(session.get('user_id'))
    })

    # Record attendance
    attendance_col.insert_one({
        "session_id": session_id,
        "student_id": session.get('user_id'),
        "admission": student.get('role_id'),
        "name": student.get('name'),
        "course": session_data.get('course'),
        "scan_time": datetime.now()
    })

    return "✅ Attendance Recorded Successfully"


# -----------------------
# Lecturer Marksheet (Live Attendance)
# -----------------------
@app.route('/marksheet/<session_id>')
def marksheet(session_id):
    if session.get('role') != 'lecturer':
        return redirect('/auth/login')

    records = attendance_col.find({"session_id": session_id})
    qr_token = sessions_col.find_one({"_id": ObjectId(session_id)})["token"]

    return render_template(
        'marksheet.html',
        records=records,
        qr_token=qr_token,
        session_id=session_id
    )

@app.route('/end_session/<session_id>')
def end_session(session_id):
    if session.get('role') != 'lecturer':
        return redirect('/auth/login')

    sessions_col.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"active": False, "end_time": datetime.now()}}
    )

    return redirect('/lecturer_dashboard')

@app.route('/export_excel/<session_id>')
def export_excel(session_id):
    if session.get('role') != 'lecturer':
        return redirect('/auth/login')

    records = attendance_col.find({"session_id": session_id})

    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance"

    # Headers
    ws.append(["Admission", "Name", "Course", "Scan Time"])

    for r in records:
        ws.append([
            r.get('admission'),
            r.get('name'),
            r.get('course'),
            str(r.get('scan_time'))
        ])

    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(tmp.name)

    return send_file(tmp.name, as_attachment=True, download_name="attendance.xlsx")

# -----------------------
# Run App
# -----------------------
if __name__ == '__main__':
    app.run(debug=True)
