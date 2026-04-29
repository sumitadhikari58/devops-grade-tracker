import os
import uuid

from flask import Flask, jsonify, redirect, render_template, request, url_for
from prometheus_flask_exporter import PrometheusMetrics


app = Flask(__name__)
PrometheusMetrics(app)

students = []
APP_ENV = os.environ.get("APP_ENV", "Development")


def calculate_grade(score):
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 65:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def compute_stats():
    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for student in students:
        grade_counts[student["grade"]] += 1

    if not students:
        return {
            "total": 0,
            "average": 0,
            "highest": 0,
            "highest_name": "—",
            "pass_rate": 0,
            "grade_counts": grade_counts,
        }

    total_score = sum(student["score"] for student in students)
    top_student = max(students, key=lambda item: item["score"])
    passing_students = sum(1 for student in students if student["score"] >= 50)

    return {
        "total": len(students),
        "average": round(total_score / len(students), 1),
        "highest": top_student["score"],
        "highest_name": top_student["name"],
        "pass_rate": round((passing_students / len(students)) * 100, 1),
        "grade_counts": grade_counts,
    }


@app.route("/")
def index():
    sorted_students = sorted(students, key=lambda student: student["score"], reverse=True)
    return render_template("index.html", students=sorted_students, stats=compute_stats(), env=APP_ENV)


@app.route("/add", methods=["POST"])
def add_student():
    name = request.form.get("name", "").strip()
    roll = request.form.get("roll", "").strip()
    subject = request.form.get("subject", "").strip()
    score_value = request.form.get("score", "").strip()

    if not all([name, roll, subject, score_value]):
        return redirect(url_for("index", error="All fields are required."))

    try:
        score = int(score_value)
    except ValueError:
        return redirect(url_for("index", error="Score must be an integer between 0 and 100."))

    if score < 0 or score > 100:
        return redirect(url_for("index", error="Score must be between 0 and 100."))

    students.append(
        {
            "id": str(uuid.uuid4()),
            "name": name,
            "roll": roll,
            "subject": subject,
            "score": score,
            "grade": calculate_grade(score),
        }
    )
    return redirect(url_for("index", success="Student added successfully!"))


@app.route("/delete/<student_id>", methods=["POST"])
def delete_student(student_id):
    students[:] = [student for student in students if student["id"] != student_id]
    return redirect(url_for("index"))


@app.route("/health")
def health():
    return jsonify({"status": "ok", "env": APP_ENV, "students": len(students)})


@app.route("/api/students")
def api_students():
    return jsonify(students)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
