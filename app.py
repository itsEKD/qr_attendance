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

@app.context_processor
def inject_now():
    return {'datetime': datetime}
# -----------------------
# Home
# -----------------------

@app.route('/')
def home():
    return render_template('home.html', datetime=datetime)



# -----------------------
# Lecturer Dashboard
# -----------------------
@app.route('/lecturer_dashboard')
def lecturer_dashboard():
    if session.get('role') != 'lecturer':
        return redirect('/auth/login')

    lecturer = users_col.find_one({"_id": ObjectId(session.get('user_id'))})

    if lecturer is None:
        session.clear()
        return redirect('/auth/login')

    lecturer['_id'] = str(lecturer['_id'])
    departments = lecturer.get('departments', [])

    # Fetch all sessions for this lecturer
    raw_sessions = list(sessions_col.find({"lecturer_id": session.get('user_id')}))
    active_sessions = []
    for s in raw_sessions:
        s['_id'] = str(s['_id'])  # serialize ObjectId
        active_sessions.append(s)

    return render_template(
        'lecturer_dashboard.html',
        departments=departments,
        lecturer=lecturer,
        active_sessions=active_sessions
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
from datetime import datetime

@app.route('/mark_attendance/<token>')
def mark_attendance(token):
    if session.get('role') != 'student':
        return redirect('/auth/login')

    student_id = session.get('user_id')
    student = users_col.find_one({"_id": ObjectId(student_id)})

    already_marked = attendance_col.find_one({
        "student_id": student_id,
        "session_token": token
    })
    if already_marked:
        return "⚠️ Attendance Already Marked"

    session_data = sessions_col.find_one({"token": token})
    if session_data:
        attendance_col.insert_one({
            "student_id": student_id,
            "admission": student['role_id'],
            "name": student.get('name', ''),      # ← Full Name
            "email": student.get('email', ''),    # ← Email
            "course": session_data['course'],
            "scan_time": datetime.utcnow(),
            "session_token": token
        })
        return "✅ Attendance Recorded Successfully"
    else:
        return "❌ Invalid Session"




# -----------------------
# Lecturer Marksheet (Live Attendance)
# -----------------------
@app.route('/marksheet/<session_id>')
def marksheet(session_id):
    if session.get('role') != 'lecturer':
        return redirect('/auth/login')

    session_data = sessions_col.find_one({"_id": ObjectId(session_id)})
    if not session_data:
        return "❌ Session not found"

    qr_token = session_data["token"]

    # Fetch attendance by session_token
    records = list(attendance_col.find({"session_token": qr_token}))

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
    ws.append(["Admission", "Name", "Email", "Course", "Scan Time"])

    for r in records:
        ws.append([
            r.get('admission'),
            r.get('name'),
            r.get('email'),
            r.get('course'),
            str(r.get('scan_time'))
        ])


    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(tmp.name)

    return send_file(tmp.name, as_attachment=True, download_name="attendance.xlsx")

@app.route('/session_attendance/<token>')
def session_attendance(token):
    if session.get('role') != 'lecturer':
        return redirect('/auth/login')

    session_data = sessions_col.find_one({"token": token})
    if not session_data:
        return "❌ Invalid Session"

    attendance_records = list(attendance_col.find({"session_token": token}))
    return render_template('session_attendance.html',
                           attendance_records=attendance_records,
                           session_course=session_data['course'])


# -----------------------
# Run App
# -----------------------
if __name__ == '__main__':
    app.run(debug=True)
