from pymongo import MongoClient

MONGO_URI = "mongodb+srv://eliwaindah:test1234@cluster0.g6igyvg.mongodb.net/campus_project"

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["campus_project"]

schools_col = db.schools

print("🔥 Seeding schools collection...")

# ⚠️ Clear old data (optional but recommended for dev)
schools_col.delete_many({})

# -------------------------
# SCHOOLS DATA
# -------------------------
schools_data = [
    {
        "school": "School of Science & Engineering",
        "departments": [
            "Computer Science",
            "Information Technology",
            "Forensics",
            "Software Engineering",
            "Cyber Security"
        ]
    },
    {
        "school": "School of Business",
        "departments": [
            "Accounting",
            "Finance",
            "Marketing",
            "Business Administration",
            "Economics"
        ]
    },
    {
        "school": "School of Health Sciences",
        "departments": [
            "Nursing",
            "Public Health",
            "Medical Laboratory",
            "Pharmacy"
        ]
    },
    {
        "school": "School of Education",
        "departments": [
            "Early Childhood Education",
            "Secondary Education",
            "Educational Psychology"
        ]
    }
]

# Insert into DB
schools_col.insert_many(schools_data)

print("✅ Schools seeded successfully!")