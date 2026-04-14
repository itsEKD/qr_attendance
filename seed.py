from pymongo import MongoClient
from datetime import datetime
import uuid

MONGO_URI = "mongodb+srv://eliwaindah:test1234@cluster0.g6igyvg.mongodb.net/campus_project"

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["campus_project"]

# Collections
users_col = db.users
sessions_col = db.sessions
attendance_col = db.attendance
schools_col = db.schools

print("🔥 Connected. Seeding database...")

# ⚠️ RUN ONLY ONCE
users_col.delete_many({})
sessions_col.delete_many({})
attendance_col.delete_many({})
schools_col.delete_many({})

# -------------------------
# SCHOOLS (MATCH FORM)
# -------------------------
school1_id = schools_col.insert_one({
    "school": "School of Science & Engineering",
    "departments": ["Computer Science", "IT", "Forensics"]
}).inserted_id

school2_id = schools_col.insert_one({
    "school": "School of Business",
    "departments": ["Accounting", "Finance", "Marketing"]
}).inserted_id

# -------------------------
# LECTURER
# -------------------------
lecturer_id = users_col.insert_one({
    "name": "Dr. Shitoti",
    "email": "ekubira@kabarak.ac.ke",
    "role": "lecturer",
    "role_id": "LEC001",
    "school": "School of Science & Engineering",
    "departments": ["Computer Science", "IT", "Forensics"]
}).inserted_id

# -------------------------
# STUDENTS (MATCH FORM INPUT)
# -------------------------
student1_id = users_col.insert_one({
    "name": "Eliud Shitoti",
    "email": "shitoti@kabarak.ac.ke",
    "role": "student",
    "role_id": "INTE/MG/2020/05/18",
    "school": "School of Science & Engineering",
    "department": "Computer Science",
    "password": "123456"
}).inserted_id

student2_id = users_col.insert_one({
    "name": "Mark Student",
    "email": "mark@kabarak.ac.ke",
    "role": "student",
    "role_id": "INTE/MG/2020/05/19",
    "school": "School of Science & Engineering",
    "department": "IT",
    "password": "123456"
}).inserted_id

# -------------------------
# SESSION
# -------------------------
token = str(uuid.uuid4())

session_id = sessions_col.insert_one({
    "course": "Computer Science",
    "token": token,
    "lecturer_id": str(lecturer_id),
    "start_time": datetime.now(),
    "active": True
}).inserted_id

# -------------------------
# ATTENDANCE
# -------------------------
attendance_col.insert_many([
    {
        "student_id": str(student1_id),
        "admission": "INTE/MG/2020/05/18",
        "name": "Eliud Shitoti",
        "email": "shitoti@kabarak.ac.ke",
        "course": "Computer Science",
        "scan_time": datetime.utcnow(),
        "session_token": token
    },
    {
        "student_id": str(student2_id),
        "admission": "INTE/MG/2020/05/19",
        "name": "Mark Student",
        "email": "mark@kabarak.ac.ke",
        "course": "Computer Science",
        "scan_time": datetime.utcnow(),
        "session_token": token
    }
])

print("✅ Database seeded successfully!")
print(f"📌 Test QR Token: {token}")