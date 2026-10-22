
from flask import Flask, jsonify, request, render_template
import student_management as sm

app = Flask(__name__)


def get_all_students():
    return [
        student
        for bucket in sm.hash_table
        for student in bucket
    ]


def refresh_database():
    sm.hash_table = [[] for _ in range(sm.TABLE_SIZE)]
    sm.load_database()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/students", methods=["GET"])
def get_students():
    return jsonify(get_all_students())


@app.route("/api/students", methods=["POST"])
def add_student_api():
    data = request.get_json(silent=True) or {}

    roll_no = str(data.get("roll_no", "")).strip()
    name = str(data.get("name", "")).strip()
    department = str(data.get("department", "")).strip()

    try:
        year = int(data.get("year", 0))
        marks = float(data.get("marks", -1))
        attendance = float(data.get("attendance", -1))
    except (ValueError, TypeError):
        return jsonify({"error": "Year and marks must be numeric."}), 400

    if not roll_no or not name or not department:
        return jsonify({"error": "All fields are required."}), 400

    if (
    year not in (1, 2, 3, 4)
    or not 0 <= marks <= 100
    or not 0 <= attendance <= 100
     ):
     return jsonify({"error": "Invalid year, marks, or attendance."}), 400
    if sm.search_record(roll_no):
        return jsonify({"error": "Roll number already exists."}), 409

    student = {
        "roll_no": roll_no,
        "name": name,
        "department": department,
        "year": year,
        "marks": marks,
        "attendance": attendance
    }

    index = sm.hash_function(roll_no)
    sm.hash_table[index].append(student)
    sm.save_database()

    return jsonify({
        "message": "Student added successfully.",
        "student": student,
        "hash_value": index
    }), 201


@app.route("/api/students/<roll_no>", methods=["PUT"])
def update_student_api(roll_no):
    student = sm.search_record(roll_no)

    if not student:
        return jsonify({"error": "Student not found."}), 404

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", student["name"])).strip()
    department = str(data.get("department", student["department"])).strip()

    try:
        year = int(data.get("year", student["year"]))
        marks = float(data.get("marks", student["marks"]))
        attendance = float(data.get("attendance", student.get("attendance", 0)))
    except (ValueError, TypeError):
        return jsonify({"error": "Year and marks must be numeric."}), 400

    if not name or not department:
        return jsonify({"error": "Name and department are required."}), 400

    if (
    year not in (1, 2, 3, 4)
    or not 0 <= marks <= 100
    or not 0 <= attendance <= 100
):
     return jsonify({"error": "Invalid year, marks, or attendance."}), 400
    student.update({
        "name": name,
        "department": department,
        "year": year,
        "marks": marks,
        "attendance": attendance
    })

    sm.save_database()

    return jsonify({"message": "Student updated successfully.", "student": student})


@app.route("/api/students/<roll_no>", methods=["DELETE"])
def delete_student_api(roll_no):
    index = sm.hash_function(roll_no)

    for student in sm.hash_table[index]:
        if student["roll_no"] == roll_no:
            sm.hash_table[index].remove(student)
            sm.save_database()
            return jsonify({"message": "Student deleted successfully."})

    return jsonify({"error": "Student not found."}), 404


@app.route("/api/analytics", methods=["GET"])
def analytics():
    students = get_all_students()

    if not students:
        return jsonify({
            "total": 0,
            "average": 0,
            "topper": None
        })

    topper = max(students, key=lambda student: float(student["marks"]))
    average = sum(float(student["marks"]) for student in students) / len(students)

    return jsonify({
        "total": len(students),
        "average": round(average, 2),
        "topper": topper
    })


if __name__ == "__main__":
    refresh_database()
    app.run(debug=True)
