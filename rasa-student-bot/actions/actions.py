# # ============================================================
# # actions/actions.py
# # RASA Custom Actions + Form Validators
# # MongoDB Atlas (PyMongo)
# # ============================================================
# from typing import Any, Text, Dict, List, Optional
# from rasa_sdk import Action, Tracker, FormValidationAction
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.events import SlotSet, AllSlotsReset, SessionStarted, ActionExecuted
# from rasa_sdk.types import DomainDict
# from bson import ObjectId
# import re
# import logging

# from mongo_connection import get_students_collection, get_courses_collection
# logger = logging.getLogger(__name__)

# # ── Helpers ────────────────────────────────────────────────
# MAIN_MENU_BUTTONS = [
#     {"title": "👥 Show Students",  "payload": "/show_students"},
#     {"title": "📚 Show Courses",   "payload": "/show_courses"},
#     {"title": "➕ Add Student",    "payload": "/add_student"},
#     {"title": "📖 Add Course",     "payload": "/add_course"},
#     {"title": "🔗 Enroll Student", "payload": "/enroll_student"},
#     {"title": "❌ Exit",           "payload": "/goodbye"},
# ]

# def is_valid_email(email: str) -> bool:
#     return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

# def format_student(student: dict, courses_col) -> str:
#     enrolled = student.get("enrolledCourses", [])
#     if enrolled:
#         course_names = []
#         for cid in enrolled:
#             c = courses_col.find_one({"_id": cid})
#             if c:
#                 course_names.append(c.get("code", cid))
#         courses_str = ", ".join(course_names) if course_names else "None"
#     else:
#         courses_str = "None"
#     return (
#         f"👤 **{student['name']}**\n"
#         f"   📧 {student['email']}  |  🎂 Age: {student.get('age', '?')}\n"
#         f"   📚 Courses: {courses_str}\n"
#         f"   🔑 ID: `{student['_id']}`"
#     )

# def format_course(course: dict, students_col) -> str:
#     enrolled_students = list(students_col.find({"enrolledCourses": course["_id"]}))
#     names = [s["name"].split()[0] for s in enrolled_students] if enrolled_students else []
#     enrolled_str = ", ".join(names) if names else "No students yet"
#     return (
#         f"📖 **{course['name']}** `{course.get('code','?')}`\n"
#         f"   👨‍🏫 {course.get('instructor','?')}  |  ⭐ {course.get('credits','?')} credits\n"
#         f"   👥 Enrolled: {course.get('enrolled', 0)}/{course.get('capacity','?')} → {enrolled_str}\n"
#         f"   🔑 ID: `{course['_id']}`"
#     )


# # ══════════════════════════════════════════════════════════════
# # ACTION: Show All Students
# # ══════════════════════════════════════════════════════════════
# class ActionShowStudents(Action):

#     def name(self) -> Text:
#         return "action_show_students"

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> List[Dict[Text, Any]]:

#         try:
#             students_col = get_students_collection()
#             courses_col  = get_courses_collection()
#             students = list(students_col.find({}))

#             if not students:
#                 dispatcher.utter_message(text="📭 No students found in the database.")
#                 return []

#             lines = [f"👥 **Students List** ({len(students)} total)\n{'─'*40}"]
#             for s in students:
#                 lines.append(format_student(s, courses_col))

#             dispatcher.utter_message(text="\n\n".join(lines))
#             logger.info(f"Fetched {len(students)} students from MongoDB")

#         except Exception as e:
#             logger.error(f"action_show_students error: {e}")
#             dispatcher.utter_message(text=f"❌ Database error: {str(e)}")

#         return []


# # ══════════════════════════════════════════════════════════════
# # ACTION: Show All Courses
# # ══════════════════════════════════════════════════════════════
# class ActionShowCourses(Action):

#     def name(self) -> Text:
#         return "action_show_courses"

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> List[Dict[Text, Any]]:

#         try:
#             courses_col  = get_courses_collection()
#             students_col = get_students_collection()
#             courses = list(courses_col.find({}))

#             if not courses:
#                 dispatcher.utter_message(text="📭 No courses found in the database.")
#                 return []

#             lines = [f"📚 **Courses List** ({len(courses)} total)\n{'─'*40}"]
#             for c in courses:
#                 lines.append(format_course(c, students_col))

#             dispatcher.utter_message(text="\n\n".join(lines))
#             logger.info(f"Fetched {len(courses)} courses from MongoDB")

#         except Exception as e:
#             logger.error(f"action_show_courses error: {e}")
#             dispatcher.utter_message(text=f"❌ Database error: {str(e)}")

#         return []


# # ══════════════════════════════════════════════════════════════
# # ACTION: Add Student (called after form submission)
# # ══════════════════════════════════════════════════════════════
# class ActionAddStudent(Action):

#     def name(self) -> Text:
#         return "action_add_student"

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> List[Dict[Text, Any]]:

#         name  = tracker.get_slot("student_name")
#         email = tracker.get_slot("student_email")
#         age   = tracker.get_slot("student_age")

#         if not all([name, email, age]):
#             dispatcher.utter_message(text="⚠️ Missing required fields. Please try again.")
#             return [AllSlotsReset()]

#         try:
#             students_col = get_students_collection()

#             # Check duplicate email
#             existing = students_col.find_one({"email": email})
#             if existing:
#                 dispatcher.utter_message(
#                     text=f"⚠️ A student with email **{email}** already exists.",
#                     buttons=MAIN_MENU_BUTTONS
#                 )
#                 return [AllSlotsReset()]

#             doc = {
#                 "name":            name,
#                 "email":           email,
#                 "age":             int(age),
#                 "enrolledCourses": [],
#             }
#             result = students_col.insert_one(doc)
#             inserted_id = str(result.inserted_id)

#             dispatcher.utter_message(
#                 text=(
#                     f"✅ **Student Added Successfully!**\n\n"
#                     f"👤 Name:  {name}\n"
#                     f"📧 Email: {email}\n"
#                     f"🎂 Age:   {int(age)}\n"
#                     f"🔑 MongoDB _id: `{inserted_id}`"
#                 )
#             )
#             logger.info(f"Inserted student: {name} → _id={inserted_id}")

#         except Exception as e:
#             logger.error(f"action_add_student error: {e}")
#             dispatcher.utter_message(text=f"❌ Failed to add student: {str(e)}")

#         return [
#             SlotSet("student_name",  None),
#             SlotSet("student_email", None),
#             SlotSet("student_age",   None),
#         ]


# # ══════════════════════════════════════════════════════════════
# # ACTION: Add Course (called after form submission)
# # ══════════════════════════════════════════════════════════════
# class ActionAddCourse(Action):

#     def name(self) -> Text:
#         return "action_add_course"

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> List[Dict[Text, Any]]:

#         name       = tracker.get_slot("course_name")
#         code       = tracker.get_slot("course_code")
#         credits    = tracker.get_slot("credits")
#         instructor = tracker.get_slot("instructor")
#         capacity   = tracker.get_slot("capacity")

#         if not all([name, code, credits, instructor, capacity]):
#             dispatcher.utter_message(text="⚠️ Missing required fields. Please try again.")
#             return [AllSlotsReset()]

#         try:
#             courses_col = get_courses_collection()

#             # Check duplicate code
#             existing = courses_col.find_one({"code": code.upper()})
#             if existing:
#                 dispatcher.utter_message(
#                     text=f"⚠️ Course code **{code.upper()}** already exists.",
#                     buttons=MAIN_MENU_BUTTONS
#                 )
#                 return [AllSlotsReset()]

#             doc = {
#                 "name":       name,
#                 "code":       code.upper(),
#                 "credits":    int(credits),
#                 "instructor": instructor,
#                 "capacity":   int(capacity),
#                 "enrolled":   0,
#             }
#             result = courses_col.insert_one(doc)
#             inserted_id = str(result.inserted_id)

#             dispatcher.utter_message(
#                 text=(
#                     f"✅ **Course Added Successfully!**\n\n"
#                     f"📖 Name:       {name}\n"
#                     f"🔑 Code:       {code.upper()}\n"
#                     f"⭐ Credits:    {int(credits)}\n"
#                     f"👨‍🏫 Instructor: {instructor}\n"
#                     f"👥 Capacity:   {int(capacity)}\n"
#                     f"🆔 MongoDB _id: `{inserted_id}`"
#                 )
#             )
#             logger.info(f"Inserted course: {name} ({code}) → _id={inserted_id}")

#         except Exception as e:
#             logger.error(f"action_add_course error: {e}")
#             dispatcher.utter_message(text=f"❌ Failed to add course: {str(e)}")

#         return [
#             SlotSet("course_name",  None),
#             SlotSet("course_code",  None),
#             SlotSet("credits",      None),
#             SlotSet("instructor",   None),
#             SlotSet("capacity",     None),
#         ]


# # ══════════════════════════════════════════════════════════════
# # ACTION: Enroll Student in Course
# # ══════════════════════════════════════════════════════════════
# class ActionEnrollStudent(Action):

#     def name(self) -> Text:
#         return "action_enroll_student"

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> List[Dict[Text, Any]]:

#         student_id = tracker.get_slot("enroll_student_id")
#         course_id  = tracker.get_slot("enroll_course_id")

#         if not student_id or not course_id:
#             dispatcher.utter_message(text="⚠️ Student ID or Course ID missing.")
#             return []

#         try:
#             students_col = get_students_collection()
#             courses_col  = get_courses_collection()

#             # Try ObjectId first, fall back to string match
#             def find_by_id(col, id_str):
#                 try:
#                     doc = col.find_one({"_id": ObjectId(id_str)})
#                     if doc: return doc
#                 except Exception:
#                     pass
#                 return col.find_one({"_id": id_str})

#             student = find_by_id(students_col, student_id)
#             course  = find_by_id(courses_col,  course_id)

#             if not student:
#                 dispatcher.utter_message(text=f"❌ No student found with ID: `{student_id}`")
#                 return [SlotSet("enroll_student_id", None), SlotSet("enroll_course_id", None)]

#             if not course:
#                 dispatcher.utter_message(text=f"❌ No course found with ID: `{course_id}`")
#                 return [SlotSet("enroll_student_id", None), SlotSet("enroll_course_id", None)]

#             enrolled_list = student.get("enrolledCourses", [])
#             if course["_id"] in enrolled_list:
#                 dispatcher.utter_message(
#                     text=f"⚠️ **{student['name']}** is already enrolled in **{course['name']}**."
#                 )
#                 return [SlotSet("enroll_student_id", None), SlotSet("enroll_course_id", None)]

#             # Check capacity
#             if course.get("enrolled", 0) >= course.get("capacity", 9999):
#                 dispatcher.utter_message(
#                     text=f"⚠️ Course **{course['name']}** is at full capacity!"
#                 )
#                 return [SlotSet("enroll_student_id", None), SlotSet("enroll_course_id", None)]

#             # Update student's enrolled courses
#             students_col.update_one(
#                 {"_id": student["_id"]},
#                 {"$push": {"enrolledCourses": course["_id"]}}
#             )
#             # Update course enrolled count
#             courses_col.update_one(
#                 {"_id": course["_id"]},
#                 {"$inc": {"enrolled": 1}}
#             )

#             dispatcher.utter_message(
#                 text=(
#                     f"🎓 **Enrollment Successful!**\n\n"
#                     f"👤 Student: **{student['name']}** (`{student['_id']}`)\n"
#                     f"📖 Course:  **{course['name']}** `{course.get('code','')}`\n\n"
#                     f"✅ MongoDB documents updated."
#                 )
#             )
#             logger.info(f"Enrolled {student['name']} → {course['name']}")

#         except Exception as e:
#             logger.error(f"action_enroll_student error: {e}")
#             dispatcher.utter_message(text=f"❌ Enrollment failed: {str(e)}")

#         return [
#             SlotSet("enroll_student_id", None),
#             SlotSet("enroll_course_id",  None),
#         ]


# # ══════════════════════════════════════════════════════════════
# # ACTION: Reset Slots
# # ══════════════════════════════════════════════════════════════
# class ActionResetSlots(Action):

#     def name(self) -> Text:
#         return "action_reset_slots"

#     def run(self, dispatcher, tracker, domain):
#         return [AllSlotsReset()]


# # ══════════════════════════════════════════════════════════════
# # FORM VALIDATOR: Add Student Form
# # ══════════════════════════════════════════════════════════════
# class ValidateAddStudentForm(FormValidationAction):

#     def name(self) -> Text:
#         return "validate_add_student_form"

#     def validate_student_name(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         if not slot_value or len(str(slot_value).strip()) < 2:
#             dispatcher.utter_message(text="⚠️ Please enter a valid name (at least 2 characters).")
#             return {"student_name": None}
#         return {"student_name": str(slot_value).strip().title()}

#     def validate_student_email(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         if not slot_value or not is_valid_email(str(slot_value).strip()):
#             dispatcher.utter_message(text="⚠️ Please enter a valid email (e.g. name@example.com).")
#             return {"student_email": None}
#         return {"student_email": str(slot_value).strip().lower()}

#     def validate_student_age(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         try:
#             age = int(float(slot_value))
#             if age < 10 or age > 100:
#                 raise ValueError
#             return {"student_age": age}
#         except (ValueError, TypeError):
#             dispatcher.utter_message(text="⚠️ Please enter a valid age (10–100).")
#             return {"student_age": None}


# # ══════════════════════════════════════════════════════════════
# # FORM VALIDATOR: Add Course Form
# # ══════════════════════════════════════════════════════════════
# class ValidateAddCourseForm(FormValidationAction):

#     def name(self) -> Text:
#         return "validate_add_course_form"

#     def validate_course_name(self, slot_value, dispatcher, tracker, domain):
#         if not slot_value or len(str(slot_value).strip()) < 3:
#             dispatcher.utter_message(text="⚠️ Course name must be at least 3 characters.")
#             return {"course_name": None}
#         return {"course_name": str(slot_value).strip()}

#     def validate_course_code(self, slot_value, dispatcher, tracker, domain):
#         code = str(slot_value).strip().upper()
#         if not re.match(r"^[A-Z]{2,6}\d{2,4}$", code):
#             dispatcher.utter_message(text="⚠️ Use format like CS101 or MATH201.")
#             return {"course_code": None}
#         return {"course_code": code}

#     def validate_credits(self, slot_value, dispatcher, tracker, domain):
#         try:
#             c = int(float(slot_value))
#             if c < 1 or c > 10:
#                 raise ValueError
#             return {"credits": c}
#         except (ValueError, TypeError):
#             dispatcher.utter_message(text="⚠️ Credits must be a number between 1 and 10.")
#             return {"credits": None}

#     def validate_instructor(self, slot_value, dispatcher, tracker, domain):
#         if not slot_value or len(str(slot_value).strip()) < 3:
#             dispatcher.utter_message(text="⚠️ Please enter a valid instructor name.")
#             return {"instructor": None}
#         return {"instructor": str(slot_value).strip()}

#     def validate_capacity(self, slot_value, dispatcher, tracker, domain):
#         try:
#             cap = int(float(slot_value))
#             if cap < 1 or cap > 1000:
#                 raise ValueError
#             return {"capacity": cap}
#         except (ValueError, TypeError):
#             dispatcher.utter_message(text="⚠️ Capacity must be between 1 and 1000.")
#             return {"capacity": None}


# # ══════════════════════════════════════════════════════════════
# # FORM VALIDATOR: Enroll Form
# # ══════════════════════════════════════════════════════════════
# class ValidateEnrollForm(FormValidationAction):

#     def name(self) -> Text:
#         return "validate_enroll_form"

#     def validate_enroll_student_id(self, slot_value, dispatcher, tracker, domain):
#         if not slot_value or len(str(slot_value).strip()) < 1:
#             dispatcher.utter_message(text="⚠️ Please provide a valid Student ID.")
#             return {"enroll_student_id": None}
#         return {"enroll_student_id": str(slot_value).strip()}

#     def validate_enroll_course_id(self, slot_value, dispatcher, tracker, domain):
#         if not slot_value or len(str(slot_value).strip()) < 1:
#             dispatcher.utter_message(text="⚠️ Please provide a valid Course ID.")
#             return {"enroll_course_id": None}
#         return {"enroll_course_id": str(slot_value).strip()}




# ============================================================
# actions/actions.py
# RASA Custom Actions + Form Validators
# MongoDB Atlas (PyMongo)
# ============================================================
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset
from rasa_sdk.types import DomainDict
from bson import ObjectId
from bson.errors import InvalidId
import re
import logging

# ✅ FIX: Absolute import — works correctly with rasa run actions
from .mongo_connection import get_students_collection, get_courses_collection

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────
MAIN_MENU_BUTTONS = [
    {"title": "👥 Show Students",  "payload": "/show_students"},
    {"title": "📚 Show Courses",   "payload": "/show_courses"},
    {"title": "➕ Add Student",    "payload": "/add_student"},
    {"title": "📖 Add Course",     "payload": "/add_course"},
    {"title": "🔗 Enroll Student", "payload": "/enroll_student"},
    {"title": "❌ Exit",           "payload": "/goodbye"},
]

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def to_object_id(id_str: str):
    """
    Safely convert string to ObjectId.
    Returns ObjectId if valid, else returns the original string.
    This handles both ObjectId _ids and plain string _ids.
    """
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        return id_str

def find_doc_by_id(collection, id_str: str):
    """
    Try ObjectId first, then fallback to raw string.
    Solves the type-mismatch bug where enrolledCourses stores
    ObjectId but we query with a plain string.
    """
    try:
        oid = ObjectId(id_str)
        doc = collection.find_one({"_id": oid})
        if doc:
            return doc
    except (InvalidId, TypeError):
        pass
    return collection.find_one({"_id": id_str})

def format_student(student: dict, courses_col) -> str:
    enrolled_ids = student.get("enrolledCourses", [])
    course_codes = []
    for cid in enrolled_ids:
        # Search by ObjectId AND string to handle both cases
        course = courses_col.find_one({"_id": cid})
        if not course:
            try:
                course = courses_col.find_one({"_id": ObjectId(str(cid))})
            except Exception:
                pass
        if course:
            course_codes.append(course.get("code", str(cid)))

    courses_str = ", ".join(course_codes) if course_codes else "No courses enrolled"
    return (
        f"👤 {student['name']}\n"
        f"   📧 {student.get('email','N/A')}  |  🎂 Age: {student.get('age','?')}\n"
        f"   📚 Courses: {courses_str}\n"
        f"   🔑 ID: {student['_id']}"
    )

def format_course(course: dict, students_col) -> str:
    course_id = course["_id"]
    enrolled_students = list(students_col.find({"enrolledCourses": course_id}))
    names = [s["name"].split()[0] for s in enrolled_students] if enrolled_students else []
    enrolled_str = ", ".join(names) if names else "No students yet"
    return (
        f"📖 {course['name']}  [{course.get('code','?')}]\n"
        f"   👨‍🏫 {course.get('instructor','?')}  |  ⭐ {course.get('credits','?')} credits\n"
        f"   👥 Enrolled: {course.get('enrolled', 0)}/{course.get('capacity','?')}  →  {enrolled_str}\n"
        f"   🔑 ID: {course['_id']}"
    )


# ══════════════════════════════════════════════════════════════
# ACTION: Show All Students
# ══════════════════════════════════════════════════════════════
class ActionShowStudents(Action):

    def name(self) -> Text:
        return "action_show_students"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:

        try:
            students_col = get_students_collection()
            courses_col  = get_courses_collection()

            students = list(students_col.find({}))
            logger.info(f"action_show_students: fetched {len(students)} students")

            if not students:
                dispatcher.utter_message(
                    text="📭 No students found in school_db.",
                    buttons=MAIN_MENU_BUTTONS
                )
                return []

            header = f"👥 Students List — {len(students)} total\n" + "─" * 35
            lines  = [header]
            for s in students:
                lines.append(format_student(s, courses_col))

            dispatcher.utter_message(text="\n\n".join(lines), buttons=MAIN_MENU_BUTTONS)

        except Exception as e:
            logger.error(f"action_show_students ERROR: {e}", exc_info=True)
            dispatcher.utter_message(
                text=f"❌ Error fetching students: {str(e)}",
                buttons=MAIN_MENU_BUTTONS
            )

        return []


# ══════════════════════════════════════════════════════════════
# ACTION: Show All Courses
# ══════════════════════════════════════════════════════════════
class ActionShowCourses(Action):

    def name(self) -> Text:
        return "action_show_courses"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:

        try:
            courses_col  = get_courses_collection()
            students_col = get_students_collection()

            courses = list(courses_col.find({}))
            logger.info(f"action_show_courses: fetched {len(courses)} courses")

            if not courses:
                dispatcher.utter_message(
                    text="📭 No courses found in school_db.",
                    buttons=MAIN_MENU_BUTTONS
                )
                return []

            header = f"📚 Courses List — {len(courses)} total\n" + "─" * 35
            lines  = [header]
            for c in courses:
                lines.append(format_course(c, students_col))

            dispatcher.utter_message(text="\n\n".join(lines), buttons=MAIN_MENU_BUTTONS)

        except Exception as e:
            logger.error(f"action_show_courses ERROR: {e}", exc_info=True)
            dispatcher.utter_message(
                text=f"❌ Error fetching courses: {str(e)}",
                buttons=MAIN_MENU_BUTTONS
            )

        return []


# ══════════════════════════════════════════════════════════════
# ACTION: Add Student (after form completes)
# ══════════════════════════════════════════════════════════════
class ActionAddStudent(Action):

    def name(self) -> Text:
        return "action_add_student"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:

        name  = tracker.get_slot("student_name")
        email = tracker.get_slot("student_email")
        age   = tracker.get_slot("student_age")

        if not all([name, email, age]):
            dispatcher.utter_message(
                text="⚠️ Missing required fields. Please try again.",
                buttons=MAIN_MENU_BUTTONS
            )
            return [AllSlotsReset()]

        try:
            students_col = get_students_collection()

            # Duplicate email check
            if students_col.find_one({"email": email.lower()}):
                dispatcher.utter_message(
                    text=f"⚠️ Student with email {email} already exists.",
                    buttons=MAIN_MENU_BUTTONS
                )
                return [
                    SlotSet("student_name",  None),
                    SlotSet("student_email", None),
                    SlotSet("student_age",   None),
                ]

            doc = {
                "name":            name.strip().title(),
                "email":           email.strip().lower(),
                "age":             int(float(age)),
                "enrolledCourses": [],
            }
            result = students_col.insert_one(doc)

            dispatcher.utter_message(
                text=(
                    f"✅ Student Added to school_db!\n\n"
                    f"👤 Name:  {doc['name']}\n"
                    f"📧 Email: {doc['email']}\n"
                    f"🎂 Age:   {doc['age']}\n"
                    f"🔑 _id:   {result.inserted_id}"
                ),
                buttons=MAIN_MENU_BUTTONS
            )
            logger.info(f"Inserted student: {doc['name']} → {result.inserted_id}")

        except Exception as e:
            logger.error(f"action_add_student ERROR: {e}", exc_info=True)
            dispatcher.utter_message(
                text=f"❌ Failed to add student: {str(e)}",
                buttons=MAIN_MENU_BUTTONS
            )

        return [
            SlotSet("student_name",  None),
            SlotSet("student_email", None),
            SlotSet("student_age",   None),
        ]


# ══════════════════════════════════════════════════════════════
# ACTION: Add Course (after form completes)
# ══════════════════════════════════════════════════════════════
class ActionAddCourse(Action):

    def name(self) -> Text:
        return "action_add_course"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:

        name       = tracker.get_slot("course_name")
        code       = tracker.get_slot("course_code")
        credits    = tracker.get_slot("credits")
        instructor = tracker.get_slot("instructor")
        capacity   = tracker.get_slot("capacity")

        if not all([name, code, credits, instructor, capacity]):
            dispatcher.utter_message(
                text="⚠️ Missing required fields. Please try again.",
                buttons=MAIN_MENU_BUTTONS
            )
            return [AllSlotsReset()]

        try:
            courses_col = get_courses_collection()

            # Duplicate code check
            if courses_col.find_one({"code": code.upper()}):
                dispatcher.utter_message(
                    text=f"⚠️ Course code {code.upper()} already exists.",
                    buttons=MAIN_MENU_BUTTONS
                )
                return [
                    SlotSet("course_name",  None),
                    SlotSet("course_code",  None),
                    SlotSet("credits",      None),
                    SlotSet("instructor",   None),
                    SlotSet("capacity",     None),
                ]

            doc = {
                "name":       name.strip(),
                "code":       code.strip().upper(),
                "credits":    int(float(credits)),
                "instructor": instructor.strip(),
                "capacity":   int(float(capacity)),
                "enrolled":   0,
            }
            result = courses_col.insert_one(doc)

            dispatcher.utter_message(
                text=(
                    f"✅ Course Added to school_db!\n\n"
                    f"📖 Name:       {doc['name']}\n"
                    f"🔑 Code:       {doc['code']}\n"
                    f"⭐ Credits:    {doc['credits']}\n"
                    f"👨‍🏫 Instructor: {doc['instructor']}\n"
                    f"👥 Capacity:   {doc['capacity']}\n"
                    f"🆔 _id:        {result.inserted_id}"
                ),
                buttons=MAIN_MENU_BUTTONS
            )
            logger.info(f"Inserted course: {doc['name']} ({doc['code']}) → {result.inserted_id}")

        except Exception as e:
            logger.error(f"action_add_course ERROR: {e}", exc_info=True)
            dispatcher.utter_message(
                text=f"❌ Failed to add course: {str(e)}",
                buttons=MAIN_MENU_BUTTONS
            )

        return [
            SlotSet("course_name",  None),
            SlotSet("course_code",  None),
            SlotSet("credits",      None),
            SlotSet("instructor",   None),
            SlotSet("capacity",     None),
        ]


# ══════════════════════════════════════════════════════════════
# ACTION: Enroll Student in Course
# ══════════════════════════════════════════════════════════════
class ActionEnrollStudent(Action):

    def name(self) -> Text:
        return "action_enroll_student"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:

        student_id_str = tracker.get_slot("enroll_student_id")
        course_id_str  = tracker.get_slot("enroll_course_id")

        if not student_id_str or not course_id_str:
            dispatcher.utter_message(
                text="⚠️ Student ID or Course ID missing.",
                buttons=MAIN_MENU_BUTTONS
            )
            return []

        try:
            students_col = get_students_collection()
            courses_col  = get_courses_collection()

            student = find_doc_by_id(students_col, student_id_str)
            course  = find_doc_by_id(courses_col,  course_id_str)

            if not student:
                dispatcher.utter_message(
                    text=f"❌ No student found with ID: {student_id_str}",
                    buttons=MAIN_MENU_BUTTONS
                )
                return [SlotSet("enroll_student_id", None), SlotSet("enroll_course_id", None)]

            if not course:
                dispatcher.utter_message(
                    text=f"❌ No course found with ID: {course_id_str}",
                    buttons=MAIN_MENU_BUTTONS
                )
                return [SlotSet("enroll_student_id", None), SlotSet("enroll_course_id", None)]

            enrolled_list = student.get("enrolledCourses", [])
            course_oid    = course["_id"]

            # Already enrolled check
            if course_oid in enrolled_list or str(course_oid) in [str(x) for x in enrolled_list]:
                dispatcher.utter_message(
                    text=f"⚠️ {student['name']} is already enrolled in {course['name']}.",
                    buttons=MAIN_MENU_BUTTONS
                )
                return [SlotSet("enroll_student_id", None), SlotSet("enroll_course_id", None)]

            # Capacity check
            if course.get("enrolled", 0) >= course.get("capacity", 9999):
                dispatcher.utter_message(
                    text=f"⚠️ {course['name']} is at full capacity!",
                    buttons=MAIN_MENU_BUTTONS
                )
                return [SlotSet("enroll_student_id", None), SlotSet("enroll_course_id", None)]

            # Update student's enrolledCourses array
            students_col.update_one(
                {"_id": student["_id"]},
                {"$push": {"enrolledCourses": course_oid}}
            )
            # Increment course enrolled count
            courses_col.update_one(
                {"_id": course_oid},
                {"$inc": {"enrolled": 1}}
            )

            dispatcher.utter_message(
                text=(
                    f"🎓 Enrollment Successful!\n\n"
                    f"👤 Student: {student['name']}\n"
                    f"📖 Course:  {course['name']} [{course.get('code','')}]\n"
                    f"✅ MongoDB Atlas updated."
                ),
                buttons=MAIN_MENU_BUTTONS
            )
            logger.info(f"Enrolled {student['name']} → {course['name']}")

        except Exception as e:
            logger.error(f"action_enroll_student ERROR: {e}", exc_info=True)
            dispatcher.utter_message(
                text=f"❌ Enrollment failed: {str(e)}",
                buttons=MAIN_MENU_BUTTONS
            )

        return [
            SlotSet("enroll_student_id", None),
            SlotSet("enroll_course_id",  None),
        ]


# ══════════════════════════════════════════════════════════════
# ACTION: Reset Slots
# ══════════════════════════════════════════════════════════════
class ActionResetSlots(Action):

    def name(self) -> Text:
        return "action_reset_slots"

    def run(self, dispatcher, tracker, domain):
        return [AllSlotsReset()]


# ══════════════════════════════════════════════════════════════
# FORM VALIDATOR: Add Student
# ══════════════════════════════════════════════════════════════
class ValidateAddStudentForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_add_student_form"

    def validate_student_name(self, slot_value, dispatcher, tracker, domain):
        if not slot_value or len(str(slot_value).strip()) < 2:
            dispatcher.utter_message(text="⚠️ Name must be at least 2 characters.")
            return {"student_name": None}
        return {"student_name": str(slot_value).strip().title()}

    def validate_student_email(self, slot_value, dispatcher, tracker, domain):
        if not slot_value or not is_valid_email(str(slot_value).strip()):
            dispatcher.utter_message(text="⚠️ Enter a valid email (e.g. name@example.com).")
            return {"student_email": None}
        return {"student_email": str(slot_value).strip().lower()}

    def validate_student_age(self, slot_value, dispatcher, tracker, domain):
        try:
            age = int(float(slot_value))
            if age < 10 or age > 100:
                raise ValueError
            return {"student_age": age}
        except (ValueError, TypeError):
            dispatcher.utter_message(text="⚠️ Enter a valid age between 10 and 100.")
            return {"student_age": None}


# ══════════════════════════════════════════════════════════════
# FORM VALIDATOR: Add Course
# ══════════════════════════════════════════════════════════════
class ValidateAddCourseForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_add_course_form"

    def validate_course_name(self, slot_value, dispatcher, tracker, domain):
        if not slot_value or len(str(slot_value).strip()) < 3:
            dispatcher.utter_message(text="⚠️ Course name must be at least 3 characters.")
            return {"course_name": None}
        return {"course_name": str(slot_value).strip()}

    def validate_course_code(self, slot_value, dispatcher, tracker, domain):
        code = str(slot_value).strip().upper()
        if not re.match(r"^[A-Z]{2,6}\d{2,4}$", code):
            dispatcher.utter_message(text="⚠️ Use format like CS101 or MATH201.")
            return {"course_code": None}
        return {"course_code": code}

    def validate_credits(self, slot_value, dispatcher, tracker, domain):
        try:
            c = int(float(slot_value))
            if c < 1 or c > 10:
                raise ValueError
            return {"credits": c}
        except (ValueError, TypeError):
            dispatcher.utter_message(text="⚠️ Credits must be a number between 1 and 10.")
            return {"credits": None}

    def validate_instructor(self, slot_value, dispatcher, tracker, domain):
        if not slot_value or len(str(slot_value).strip()) < 3:
            dispatcher.utter_message(text="⚠️ Enter a valid instructor name.")
            return {"instructor": None}
        return {"instructor": str(slot_value).strip()}

    def validate_capacity(self, slot_value, dispatcher, tracker, domain):
        try:
            cap = int(float(slot_value))
            if cap < 1 or cap > 1000:
                raise ValueError
            return {"capacity": cap}
        except (ValueError, TypeError):
            dispatcher.utter_message(text="⚠️ Capacity must be between 1 and 1000.")
            return {"capacity": None}


# ══════════════════════════════════════════════════════════════
# FORM VALIDATOR: Enroll
# ══════════════════════════════════════════════════════════════
class ValidateEnrollForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_enroll_form"

    def validate_enroll_student_id(self, slot_value, dispatcher, tracker, domain):
        if not slot_value or len(str(slot_value).strip()) < 1:
            dispatcher.utter_message(text="⚠️ Please provide a valid Student ID.")
            return {"enroll_student_id": None}
        return {"enroll_student_id": str(slot_value).strip()}

    def validate_enroll_course_id(self, slot_value, dispatcher, tracker, domain):
        if not slot_value or len(str(slot_value).strip()) < 1:
            dispatcher.utter_message(text="⚠️ Please provide a valid Course ID.")
            return {"enroll_course_id": None}
        return {"enroll_course_id": str(slot_value).strip()}