"""
scripts/seed_mongodb.py
Seed MongoDB Atlas with sample students and courses.
Run: python scripts/seed_mongodb.py
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

# Override with real URI directly
os.environ.setdefault(
    "MONGODB_URI",
    "mongodb+srv://devareddy5021_db_user:Y2tipZvQcl3R9cE4@cluster0.tzc2jbx.mongodb.net/school_db?retryWrites=true&w=majority"
)
os.environ.setdefault("MONGODB_DB", "school_db")

from actions.mongo_connection import get_students_collection, get_courses_collection

STUDENTS = [
    {"name": "Alice Johnson",  "email": "alice@uni.edu",  "age": 21, "enrolledCourses": []},
    {"name": "Bob Smith",      "email": "bob@uni.edu",    "age": 23, "enrolledCourses": []},
    {"name": "Carol Martinez", "email": "carol@uni.edu",  "age": 20, "enrolledCourses": []},
    {"name": "David Lee",      "email": "david@uni.edu",  "age": 22, "enrolledCourses": []},
]

COURSES = [
    {"name": "Introduction to Computer Science", "code": "CS101", "credits": 3, "instructor": "Prof. Brown",  "capacity": 30, "enrolled": 0},
    {"name": "Data Structures & Algorithms",     "code": "CS201", "credits": 4, "instructor": "Prof. Green",  "capacity": 25, "enrolled": 0},
    {"name": "Database Management Systems",      "code": "CS301", "credits": 3, "instructor": "Prof. White",  "capacity": 20, "enrolled": 0},
    {"name": "Artificial Intelligence",          "code": "CS401", "credits": 4, "instructor": "Prof. Black",  "capacity": 15, "enrolled": 0},
]

def seed():
    students_col = get_students_collection()
    courses_col  = get_courses_collection()

    # Clear existing
    students_col.delete_many({})
    courses_col.delete_many({})
    print("🗑️  Cleared existing data.")

    # Insert
    s_result = students_col.insert_many(STUDENTS)
    c_result = courses_col.insert_many(COURSES)

    print(f"✅ Inserted {len(s_result.inserted_ids)} students.")
    print(f"✅ Inserted {len(c_result.inserted_ids)} courses.")
    print("🎉 MongoDB seeded successfully!")

if __name__ == "__main__":
    seed()
