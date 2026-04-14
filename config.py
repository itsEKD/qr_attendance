from pymongo import MongoClient

MONGO_URI = "mongodb+srv://eliwaindah:test1234@cluster0.g6igyvg.mongodb.net/campus_project"

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

# Explicit DB (safer)
db = client["campus_project"]

# Collections
users_col = db.users
sessions_col = db.sessions
attendance_col = db.attendance
schools_col = db["schools"]