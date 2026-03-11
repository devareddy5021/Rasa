# 🤖 Student Management Bot — RASA + Python + MongoDB Atlas

A fully-featured chatbot built with **RASA 3.6**, **Python**, and **MongoDB Atlas**.

---

## 📁 Project Structure

```
rasa-student-bot/
│
├── data/
│   ├── nlu.yml          ← NLU training data (intents + examples)
│   ├── stories.yml      ← Multi-turn conversation flows
│   └── rules.yml        ← Deterministic rules (forms, fallback, exit)
│
├── domain/
│   └── domain.yml       ← Intents, entities, slots, responses, forms, actions
│
├── actions/
│   ├── actions.py       ← Custom actions + form validators
│   └── mongo_connection.py  ← MongoDB Atlas connection manager
│
├── config/
│   └── endpoints.yml    ← Action server + tracker store config
│
├── scripts/
│   └── seed_mongodb.py  ← Seed MongoDB with sample data
│
├── config.yml           ← NLU pipeline + dialogue policies
├── requirements.txt
└── .env.example
```

---

## ⚙️ Setup

### 1. Install dependencies
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure MongoDB Atlas
Your MongoDB Atlas is already configured:
```
Cluster:   cluster0.tzc2jbx.mongodb.net
Database:  school_db
User:      devareddy5021_db_user
```
The connection string is pre-set in `actions/mongo_connection.py` and `config/endpoints.yml`.

### 3. Seed the database
```bash
python scripts/seed_mongodb.py
```

### 4. Train the RASA model
```bash
rasa train
```

---

## 🚀 Running the Bot

Open **3 terminal windows**:

**Terminal 1 — Action Server (MongoDB operations)**
```bash
rasa run actions
```

**Terminal 2 — RASA Server**
```bash
rasa run --enable-api --cors "*" --endpoints config/endpoints.yml
```

**Terminal 3 — Chat in terminal (optional)**
```bash
rasa shell
```

---

## 💬 Example Conversations

```
User: hi
Bot:  👋 Hello! I'm the Student Management Bot.
      [👥 Show Students] [📚 Show Courses] [➕ Add Student] ...

User: show students
Bot:  👥 Students List (4 total)
      👤 Alice Johnson — alice@uni.edu | Age 21 | Courses: None

User: add student
Bot:  📝 What is the student's full name?
User: John Doe
Bot:  📧 What is the student's email address?
User: john@uni.edu
Bot:  🎂 What is the student's age?
User: 22
Bot:  ✅ Student Added! MongoDB _id: 65f3a...

User: enroll student
Bot:  👤 Please enter the Student ID:
User: 65f3a...
Bot:  📚 Please enter the Course ID:
User: 65f3b...
Bot:  🎓 Enrollment Successful!

User: bye
Bot:  👋 Goodbye! Session ended.
```

---

## 🗄️ MongoDB Collections

| Collection | Fields |
|---|---|
| `students` | `_id, name, email, age, enrolledCourses[]` |
| `courses`  | `_id, name, code, credits, instructor, capacity, enrolled` |

---

## 🏗️ RASA Architecture

| RASA Component | File |
|---|---|
| NLU Pipeline | `config.yml` |
| Intents + NLU examples | `data/nlu.yml` |
| Conversation flows | `data/stories.yml` |
| Deterministic rules | `data/rules.yml` |
| Domain (slots, responses, forms) | `domain/domain.yml` |
| Custom Actions | `actions/actions.py` |
| MongoDB connection | `actions/mongo_connection.py` |
| Action server endpoint | `config/endpoints.yml` |
