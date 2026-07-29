from flask import Flask, request, render_template, session, redirect
import sqlite3
import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from ktu_llm_evaluator import evaluate_ktu_answer

app = Flask(__name__)
app.secret_key = "super_secure_key_2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# LOAD MODEL ANSWERS
# -------------------------
with open(os.path.join(BASE_DIR, "data", "model_answers.json"), "r", encoding="utf-8") as f:
    MODEL_ANSWERS = json.load(f)

# -------------------------
# MARK SCHEME
# -------------------------
mark_scheme = {
    "Q11": {"(a)": 10, "(b)": 4},
    "Q12": 14,
    "Q13": {"(a)": 10, "(b)": 4},
    "Q14": {"(a)": 10, "(b)": 4},
    "Q15": {"(a)": 7, "(b)": 7},
    "Q16": {"(a)": 7, "(b)": 7},
    "Q17": {"(a)": 10, "(b)": 4},
    "Q18": {"(a)": 10, "(b)": 4},
    "Q19": {"(a)": 10, "(b)": 4},
    "Q20": 14
}

# -------------------------
# DATABASE INIT
# -------------------------
def init_db():

    conn = sqlite3.connect("edutech.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        register_no TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        total INTEGER,
        percentage REAL,
        grade TEXT,
        details TEXT,
        timestamp TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Create Admin
    cursor.execute("SELECT * FROM users WHERE role='admin'")
    if not cursor.fetchone():

        cursor.execute("""
        INSERT INTO users (name, register_no, password, role)
        VALUES (?, ?, ?, ?)
        """, (
            "ADMIN",
            "ADMIN",
            generate_password_hash("ADMIN123"),
            "admin"
        ))

    # Default Students
    students = [

("AAKASH MURALI NAIR","JEC22EC001"),
("ABEL SUNIL","JEC22EC002"),
("ABHIJITH K S","JEC22EC003"),
("ADITHYA KALARIKAL SAJKUMAR","JEC22EC004"),
("AFEEFA SHERIN T A","JEC22EC005"),
("AIVIN SIMON","JEC22EC006"),
("AKSHAYA M R","JEC22EC007"),
("ALBIN BABU","JEC22EC008"),
("ALOKA ANIL","JEC22EC009"),
("ANGEL MARIA DIAS","JEC22EC010"),
("ANITTA PALAMUTTAM THOMAS","JEC22EC011"),
("ANJALI K","JEC22EC012"),
("ANLY ANDERS","JEC22EC013"),
("ANNLIYA ROSE DAVID","JEC22EC014"),
("ANN MARIYA PAUL","JEC22EC015"),
("ANTONY JOHNSON","JEC22EC016"),
("ANUSYOOTH A S","JEC22EC017"),
("ARUN SHANKAR T K","JEC22EC018"),
("ASWIN K","JEC22EC019"),
("BHANUPRIYA","JEC22EC020"),
("C SANJANA MANOJ","JEC22EC021"),
("DARSANA C K","JEC22EC022"),
("DIYOSH BENNY K","JEC22EC023"),
("DURGA C K","JEC22EC024"),
("EDWIN SHAJAN","JEC22EC025"),
("FATHIMA SHILNA M","JEC22EC026"),
("HARI KRISHNAN","JEC22EC027"),
("INDRADATHAN K G","JEC22EC028"),
("JEROSH JAMES","JEC22EC029"),
("JOYAL JAIMY","JEC22EC030"),
("KRISHNENDU R","JEC22EC031"),
("K ROHITH","JEC22EC032"),
("MARIYAM ROSA BABU","JEC22EC033"),
("MERIN MARIA SUNNY","JEC22EC034"),
("M G MITHUN","JEC22EC035"),
("NANDITHA SREEKUMAR B T","JEC22EC036"),
("NIHALA FARVIN P S","JEC22EC037"),
("NIKHIL K","JEC22EC038"),
("NILIYA ROSE THOMAS","JEC22EC039"),
("NIRANJAN R","JEC22EC040"),
("PAVIN JOSHY ANDERSON","JEC22EC041"),
("PIYUSH K C","JEC22EC042"),
("RASHA HANNAN K V","JEC22EC043"),
("SAAHIL K LAZAR","JEC22EC044"),
("SACHIN SHIV K","JEC22EC045"),
("SIVAJYOTHIK M","JEC22EC046"),
("SOUMYA P V","JEC22EC047"),
("SREELAKSHMI K G","JEC22EC048"),
("SUJIL P U","JEC22EC049"),
("VISMAYA K","JEC22EC050"),
("YADHU KRISHNA M R","JEC22EC051"),
("DENIL DAVIS","LJEC22EC052"),
("RONIT PAULSON","LJEC22EC053"),
("SHERIN SAJAN","LJEC22EC054"),
("SHREYA MARIYA T P","LJEC22EC055"),
("SREELAKSHMI P N","LJEC22EC056"),
("VIVEK P","LJEC22EC057")

]

    for s in students:
        nameparts= s[0].split()

        if len(nameparts[0]) == 1:
            first_name = nameparts[1]
        else:
            first_name = nameparts[0]

        password = first_name + "123"

        try:
            cursor.execute("""
            INSERT INTO users (name, register_no, password, role)
            VALUES (?, ?, ?, ?)
            """, (s[0], s[1], generate_password_hash(password), "student"))
        except:
            pass

    conn.commit()
    conn.close()

# -------------------------
# GRADE SYSTEM
# -------------------------
def calculate_grade(p):

    if p >= 90: return "S"
    elif p >= 85: return "A+"
    elif p >= 80: return "A"
    elif p >= 75: return "B+"
    elif p >= 70: return "B"
    elif p >= 65: return "C+"
    elif p >= 60: return "C"
    elif p >= 55: return "D"
    elif p >= 50: return "P"
    else: return "F"

# -------------------------
# REMARK SYSTEM
# -------------------------
def generate_remark(p):

    if p >= 90:
        return "Outstanding performance with excellent conceptual clarity."
    elif p >= 75:
        return "Very good performance. Minor improvements needed."
    elif p >= 60:
        return "Good understanding but lacks depth."
    elif p >= 50:
        return "Average performance."
    else:
        return "Insufficient conceptual understanding."

# -------------------------
# PARSE TXT
# -------------------------
def parse_txt(filepath):

    answers = {}

    with open(filepath,"r",encoding="utf-8") as f:
        content = f.read()

    parts = content.split("Q")

    for part in parts:
        if ":" in part:
            key,value = part.split(":",1)
            answers["Q"+key.strip()] = value.strip()

    return answers

# -------------------------
# HOME
# -------------------------
@app.route("/")
def home():
    return redirect("/login")

# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        reg = request.form["register_no"]
        pwd = request.form["password"]

        conn = sqlite3.connect("edutech.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE register_no=?", (reg,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[3], pwd):

            session["user_id"] = user[0]
            session["role"] = user[4]
            session["name"] = user[1]

            if user[4] == "admin":
                return redirect("/admin/dashboard")

            return redirect("/upload")

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# -------------------------
# UPLOAD PAGE
# -------------------------
@app.route("/upload")
def upload():

    if session.get("role") != "student":
        return redirect("/login")

    return render_template("upload.html", name=session.get("name"))

# -------------------------
# EVALUATE
# -------------------------
@app.route("/evaluate", methods=["POST"])
def evaluate():

    if session.get("role") != "student":
        return redirect("/login")

    # Only one submission
    conn = sqlite3.connect("edutech.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM results WHERE user_id=?", (session["user_id"],))
    existing = cursor.fetchone()

    conn.close()

    if existing:
        return render_template("upload.html",
                               name=session.get("name"),
                               error="You already submitted.")

    file = request.files["file"]

    filename = f"{session['user_id']}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)

    student_answers = parse_txt(filepath)

    detailed_scores = {}
    part_a_total = 0

    # -------- PART A
    for i in range(1,11):

        q = f"Q{i}"

        if q in student_answers:

            result = evaluate_ktu_answer(
                q,
                MODEL_ANSWERS.get(q,""),
                student_answers[q],
                3
            )

            part_a_total += result["score"]

            detailed_scores[q] = {
                "score": result["score"],
                "feedback": result.get("feedback","")
            }

    # -------- PART B
    module_pairs = [
        (("Q11(a)", "Q11(b)"), "Q12"),
        (("Q13(a)", "Q13(b)"), "Q14"),
        (("Q15(a)", "Q15(b)"), "Q16"),
        (("Q17(a)", "Q17(b)"), "Q18"),
        (("Q19(a)", "Q19(b)"), "Q20")
    ]

    part_b_total = 0

    for sub_pair, alt_q in module_pairs:

        sub_total = 0

        for sub in sub_pair:

            if sub in student_answers:

                main_q = sub.split("(")[0]
                sub_key = f"({sub[-2]})"

                max_mark = mark_scheme[main_q][sub_key]

                result = evaluate_ktu_answer(
                    sub,
                    MODEL_ANSWERS.get(sub,""),
                    student_answers[sub],
                    max_mark
                )

                sub_total += result["score"]

                detailed_scores[sub] = {
                    "score": result["score"],
                    "feedback": result.get("feedback","")
                }

        alt_total = 0

        if alt_q in student_answers:

            result = evaluate_ktu_answer(
                alt_q,
                MODEL_ANSWERS.get(alt_q,""),
                student_answers[alt_q],
                14
            )

            alt_total = result["score"]

            detailed_scores[alt_q] = {
                "score": result["score"],
                "feedback": result.get("feedback","")
            }

        module_score = min(max(sub_total, alt_total),14)

        part_b_total += module_score

    total_marks = min(part_a_total + part_b_total,100)

    percentage = total_marks
    grade = calculate_grade(percentage)
    remark = generate_remark(percentage)

    detailed_scores["remark"] = remark

    conn = sqlite3.connect("edutech.db")
    cursor = conn.cursor()


    cursor.execute("""
    INSERT INTO results (user_id,total,percentage,grade,details,timestamp)
    VALUES (?,?,?,?,?,?)
    """,(
        session["user_id"],
        total_marks,
        percentage,
        grade,
        json.dumps(detailed_scores),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return redirect("/myresults")

# -------------------------
# STUDENT RESULTS
# -------------------------
@app.route("/myresults")
def myresults():

    conn = sqlite3.connect("edutech.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT total,percentage,grade,details,timestamp
    FROM results
    WHERE user_id=?
    """,(session["user_id"],))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return render_template("student_results.html", data=None)

    total, percentage, grade, details, timestamp = row

    if timestamp:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        timestamp = dt.strftime("%d/%m/%Y %I:%M %p")
    else:
        timestamp = "-"

    details_dict = json.loads(details)

    feedback_rows = []

    for q, val in details_dict.items():

        if q == "remark":
            continue

        feedback_rows.append({
            "question": q,
            "score": val.get("score","-"),
            "feedback": val.get("feedback","")
        })

    result = {
        "total": total,
        "percentage": percentage,
        "grade": grade,
        "timestamp": timestamp,
        "feedbacks": feedback_rows,
        "remark": details_dict.get("remark","")
    }

    return render_template("student_results.html", data=result)

# -------------------------
# ADMIN DASHBOARD
# -------------------------
@app.route("/admin/dashboard")
def admin_dashboard():

    conn = sqlite3.connect("edutech.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT users.name,
           users.register_no,
           CASE
               WHEN results.user_id IS NULL THEN 'Absent'
               ELSE 'Present'
           END AS status,
           results.total,
           results.grade,
           results.timestamp

    FROM users
    LEFT JOIN results
    ON users.id = results.user_id
    WHERE users.role='student'
    ORDER BY users.register_no
    """)

    data = cursor.fetchall()
    formatted_data = []

    for row in data:
        timestamp = row[5]

        if timestamp:
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            timestamp = dt.strftime("%d/%m/%Y %I:%M %p")
        else:
            timestamp = "-"

        formatted_data.append((
            row[0],  # name
            row[1],  # register_no
            row[2],  # status
            row[3],  # total
            row[4],  # grade
            timestamp
        ))

    conn.close()

    return render_template("admin_dashboard.html", data= formatted_data)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)