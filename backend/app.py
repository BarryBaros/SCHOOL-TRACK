from flask import Flask, request, jsonify
from datetime import datetime
from extensions import db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://baros:Kitinda%408893@localhost/school_track"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

from models.student import Student
from models.attendance import Attendance

def validate_date(date_string):
   try:
      date = datetime.strptime(date_string, "%Y-%m-%d").date()

      if date > datetime.today().date():
         return None

      return date

   except ValueError:
      return None

def validate_name(name):
   if not name or not name.strip():
      return False

   return True

def validate_admission_number(admission_number):
   if not admission_number or not admission_number.strip():
      return False

   return True

def validate_grade(grade):
   valid_grades = [
      "PP 1",
      "PP 2",
      "PP 3",
      "Grade 1",
      "Grade 2",
      "Grade 3",
      "Grade 4",
      "Grade 5",
      "Grade 6",
      "Grade 7"
   ]

   if grade.strip() not in valid_grades:
      return False

   return True

def validate_student_data(data):
   if not validate_name(data["first_name"]):
      return "First name cannot be empty"

   if not validate_name(data["last_name"]):
      return "Last name cannot be empty"

   if not validate_admission_number(data["admission_number"]):
      return "Admission number cannot be empty"

   if not validate_grade(data["grade"]):
      return "Invalid grade"

   date_of_birth = validate_date(data["date_of_birth"])

   if date_of_birth is None:
      return "Invalid date of birth. Use YYYY-MM-DD format."
   return None

@app.route("/")
def home():
  return "School Track API is running!"

@app.route("/students", methods=["POST"])
def create_student():
   data = request.get_json()

   if not data:
      return jsonify({
         "message": "Request body is required"
      }), 400

   required_fields = ["admission_number", "first_name", "last_name", "grade", "date_of_birth"]

   for field in required_fields:
      if field not in data or not data[field]:
         return jsonify({
            "message": f"{field} is required"
         }), 400

   error = validate_student_data(data)

   if error:
      return jsonify({
         "message": error
      }), 400

   date_of_birth = validate_date(data["date_of_birth"])

   admission_number = data["admission_number"].strip()

   existing_student = Student.query.filter_by(
      admission_number=admission_number
   ).first()

   if existing_student:
      return jsonify({
         "message": "Admission number already exists"
      }), 409

   student = Student(
        admission_number=admission_number,
        first_name=data["first_name"].strip(),
        last_name=data["last_name"].strip(),
        grade=data["grade"].strip(),
        date_of_birth=date_of_birth
     )
   
   db.session.add(student)
   db.session.commit()

   return jsonify({
      "message": "Student created successfully",
      "student": {
         "id": student.id,
         "admission_number": student.admission_number,
         "first_name": student.first_name,
         "last_name": student.last_name,
         "grade": student.grade,
         "date_of_birth": student.date_of_birth.isoformat() if student.date_of_birth else None
      }
   }), 201

@app.route("/students", methods=["GET"])
def get_students():
   students = Student.query.all()

   return jsonify([
      {
         "id": student.id,
         "admission_number": student.admission_number,
         "first_name": student.first_name,
         "last_name": student.last_name,
         "grade": student.grade,
         "date_of_birth": student.date_of_birth.isoformat() if student.date_of_birth else None
      }
      for student in students
   ])

@app.route("/students/search", methods=["GET"])
def search_student():
   admission_number = request.args.get("admission_number")

   if not admission_number:
      return jsonify({
         "message": "Admission number required!"
      }), 400

   student = Student.query.filter_by(
      admission_number=admission_number
   ).first()

   if student is None:
      return jsonify({
         "message": "Student not found!"
      }), 404

   return jsonify({
      "id": student.id,
      "admission_number": student.admission_number,
      "first_name": student.first_name,
      "last_name": student.last_name,
      "grade": student.grade,
      "date_of_birth": student.date_of_birth.isoformat() if student.date_of_birth else None
   })

@app.route("/students/<int:id>", methods=["GET"])
def get_student(id):
   student = Student.query.get(id)

   if student is None:
      return jsonify({
         "message": "Student not found!"
      }), 404

   return jsonify({
      "id": student.id,
      "admission_number": student.admission_number,
      "first_name": student.first_name,
      "last_name": student.last_name,
      "grade": student.grade,
      "date_of_birth": student.date_of_birth.isoformat() if student.date_of_birth else None
   })

@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):
   student = Student.query.get(id)

   if student is None:
      return jsonify({
         "message": "Student not found!"
      }), 404

   data = request.get_json()

   if not data:
      return jsonify({
         "message": "Request body is required"
      }), 400
   
   required_fields = ["admission_number", "first_name", "last_name", "grade", "date_of_birth"]

   for field in required_fields:
      if field not in data or not data[field]:
         return jsonify({
            "message": f"{field} is required"
         }), 400

   error = validate_student_data(data)

   if error:
      return jsonify({
         "message": error
      }), 400

   date_of_birth = validate_date(data["date_of_birth"])

   admission_number = data["admission_number"].strip()

   existing_student = Student.query.filter_by(
      admission_number=admission_number
   ).first()
      
   if existing_student and existing_student.id != student.id:
      return jsonify({
         "message": "Admission number already exists"
      }), 409
      
   student.admission_number = admission_number
   student.first_name = data["first_name"].strip()
   student.last_name = data["last_name"].strip()
   student.grade = data["grade"].strip()
   student.date_of_birth = date_of_birth

   db.session.commit()

   return jsonify({
      "message": "Student updated successfully!",
      "student": {
         "id": student.id,
         "admission_number": student.admission_number,
         "first_name": student.first_name,
         "last_name": student.last_name,
         "grade": student.grade,
         "date_of_birth": student.date_of_birth.isoformat() if student.date_of_birth else None
      }
   })


@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
   student = Student.query.get(id)

   if student is None:
      return jsonify({
         "message": "Student not found!"
      }), 404

   db.session.delete(student)
   db.session.commit()

   return jsonify({
      "message": "Student deleted successfully!"
   })

with app.app_context():
    db.create_all()

if __name__ == "__main__":
  app.run(port=5555, debug=True)