from pymongo import MongoClient

# MongoDB Atlas URI including the database name
MONGO_URI = "mongodb+srv://eliwaindah:eliwaindaheliwashitojossie@cluster0.jyz0y.mongodb.net/campus_project?retryWrites=true&w=majority"

# Connect to MongoDB
client = MongoClient(MONGO_URI)

# Use the database
db = client.get_database()

# Collections
users_col = db.users          # students & lecturers
sessions_col = db.sessions    # class sessions
attendance_col = db.attendance  # attendance logs
schools_col = db["schools"]
