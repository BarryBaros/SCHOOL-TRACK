from flask import Flask, request, jsonify
from datetime import datetime
from extensions import db
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
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
        date_of_birth=date_of_birth,
        parent_name=data.get("parent_name"),
        parent_phone=data.get("parent_phone")
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
         "date_of_birth": student.date_of_birth.isoformat() if student.date_of_birth else None,
         "parent_name": student.parent_name,
         "parent_phone": student.parent_phone
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

@app.route("/attendance/arrival", methods=["POST"])
def record_arrival():
   data = request.get_json()

   if not data or "admission_number" not in data:
      return jsonify({
         "message": "Admission number is required"
      }), 400

   admission_number = data["admission_number"].strip()

   student = Student.query.filter_by(
      admission_number=admission_number
   ).first()

   if student is None:
      return jsonify({
         "message": "Student not found"
      }), 404

   today = datetime.today().date()

   existing_attendance = Attendance.query.filter_by(
      student_id=student.id,
      attendance_date=today
   ).first()

   if existing_attendance:
      return jsonify({
         "message": "Student has already arrived today."
      }), 409

   attendance = Attendance(
      student_id=student.id,
      attendance_date=today,
      arrival_time=datetime.now()
   )

   db.session.add(attendance)
   db.session.commit()

   sms_message = (
      f"Hello, {student.parent_name or 'Parent/Guardian'}. "
      f"Your child, {student.first_name} {student.last_name}, "
      f"has arrived at school at "
      f"{attendance.arrival_time.strftime('%I:%M %p')}."
   )

   return jsonify({
      "message": "Arrival recorded successfully",
      "sms_message": sms_message,
      "student": {
         "id": student.id,
         "admission_number": student.admission_number,
         "first_name": student.first_name,
         "last_name": student.last_name,
         "grade": student.grade,
         "arrival_time": attendance.arrival_time.isoformat()
      }
   }), 201


@app.route("/attendance/departure", methods=["POST"])

def record_departure():

   data = request.get_json()
   
   if not data or "admission_number" not in data:

      return jsonify({
         "message": "Admission number is required"
      }), 400

   admission_number = data["admission_number"].strip()

   student = Student.query.filter_by(
      admission_number=admission_number
   ).first()

   if student is None:

      return jsonify({
         "message": "Student not found"
      }), 404
   
   today = datetime.today().date()
   attendance = Attendance.query.filter_by(
      student_id=student.id,
      attendance_date=today
   ).first()

   if attendance is None:

      return jsonify({
         "message": "Student has no arrival record for today."
      }), 404

   if attendance.departure_time is not None:

      return jsonify({
         "message": "Student has already departed today."
      }), 409

   attendance.departure_time = datetime.now()
   
   db.session.commit()

   sms_message = (
      f"Hello, {student.parent_name or 'Parent/Guardian'}. "
      f"Your child, {student.first_name} {student.last_name}, "
      f"has left school at "
      f"{attendance.departure_time.strftime('%I:%M %p')}."
   )

   return jsonify({
         "message": "Departure recorded successfully",
         "sms_message": sms_message,
         "student": {
            "id": student.id,
            "admission_number": student.admission_number,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "grade": student.grade,
            "arrival_time": attendance.arrival_time.isoformat(),
            "departure_time": attendance.departure_time.isoformat()
         }
      }), 200

@app.route("/attendance", methods=["GET"])
def get_attendance():

   # attendance_records = Attendance.query.all()

   requested_date = request.args.get("date")

   if requested_date:
      requested_date = validate_date(requested_date)

      if requested_date is None:
         return jsonify({
            "message": "Invalid date. Use YYYY-MM-DD."
         }), 400

      attendance_records = Attendance.query.filter_by(
         attendance_date=requested_date
      ).all()

   else:
      attendance_records = Attendance.query.all()

   results  = []

   for attendance in attendance_records:

      student = Student.query.get(attendance.student_id)

      results.append({
         "id": attendance.id,
         "student_id": attendance.student_id,
         "admission_number": student.admission_number,
         "first_name": student.first_name,
         "last_name": student.last_name,
         "grade": student.grade,
         "attendance_date": attendance.attendance_date.isoformat(),
         "arrival_time": attendance.arrival_time.isoformat(),
         "departure_time": attendance.departure_time.isoformat() if attendance.departure_time else None
      })
      
   return jsonify(results), 200

@app.route("/attendance/student/<admission_number>", methods=["GET"]) 
def get_student_attendance(admission_number):

   student = Student.query.filter_by(
      admission_number=admission_number
   ).first()

   if student is None:
      return jsonify({
         "message": "Student not found"
      }), 404

   attendance_records = Attendance.query.filter_by(
      student_id=student.id
   ).all()

   results = []

   for attendance in attendance_records:

      results.append({
         "attendance_id": attendance.id,
         "attendance_date": attendance.attendance_date.isoformat(),
         "arrival_time": attendance.arrival_time.isoformat(),
         "departure_time": attendance.departure_time.isoformat() if attendance.departure_time else None
      })

   return jsonify({
      "student": {
         "id": student.id,
         "admission_number": student.admission_number,
         "first_name": student.first_name,
         "last_name": student.last_name,
         "grade": student.grade
      },
      "attendance_records": results
   }), 200


def send_sms(phone_number, message):
   api_key = os.getenv("PAYGRID_API_KEY")
   base_url = os.getenv("PAYGRID_BASE_URL", "").rstrip("/")

   if not api_key or not base_url:
      print("SMS settings are missing from .env")
      return False

   payload = {
      "recipient": [phone_number],
      "message": message,
      "sender_id": "CommsGrid"
   }

   try:
      response = requests.post(
         f"{base_url}/sms/send",
         headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
         },
         json=payload,
         timeout=20
      )

      print("SMS HTTP status:", response.status_code)

      if response.ok:
         print("SMS API response:", response.text)
         return True

      print("SMS request failed:", response.text)
      return False

   except requests.RequestException as error:
      print("SMS connection error:", error)
      return False

with app.app_context():
    db.create_all()

if __name__ == "__main__":
  app.run(port=5555, debug=True)