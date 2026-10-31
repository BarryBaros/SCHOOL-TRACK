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
from models.sms_notification import SMSNotification
from models.guardian import Guardian

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

   if data.get("date_of_birth"):
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

   required_fields = ["admission_number", "first_name", "last_name", "grade"]

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

   date_of_birth = validate_date(data["date_of_birth"]) if data.get("date_of_birth") else None

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

   required_fields = ["admission_number", "first_name", "last_name", "grade"]

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

   date_of_birth = validate_date(data["date_of_birth"]) if data.get("date_of_birth") else None

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

   sms_sent = False
   sms_message_id = None
   sms_status = None

   if student.parent_phone:
      phone_number = student.parent_phone.strip().replace("+", "")
      sms_sent, sms_message_id, sms_status = send_sms(phone_number, sms_message)

      notification = SMSNotification(
         attendance_id=attendance.id,
         notification_type="ARRIVAL",
         recipient_phone=phone_number,
         message_id=sms_message_id,
         status=sms_status or ("SENT" if sms_sent else "FAILED")
      )

      db.session.add(notification)
      db.session.commit()

   return jsonify({
      "message": "Arrival recorded successfully",
      "sms_message": sms_message,
      "sms_sent": sms_sent,
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

   sms_sent = False
   sms_message_id = None
   sms_status = None
   
   if student.parent_phone:
      phone_number = student.parent_phone.strip().replace("+", "")
      sms_sent, sms_message_id, sms_status = send_sms(phone_number, sms_message)

      notification = SMSNotification(
         attendance_id=attendance.id,
         notification_type="DEPARTURE",
         recipient_phone=phone_number,
         message_id=sms_message_id,
         status=sms_status or ("SENT" if sms_sent else "FAILED")
      )

      db.session.add(notification)
      db.session.commit()

   return jsonify({
         "message": "Departure recorded successfully",
         "sms_message": sms_message,
         "sms_sent": sms_sent,
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
    environment = os.getenv("PAYGRID_ENVIRONMENT", "SANDBOX").upper()
    base_url = os.getenv("PAYGRID_BASE_URL", "").rstrip("/")

    if environment == "PRODUCTION":
        api_key = os.getenv("PAYGRID_PRODUCTION_API_KEY")
        sender_id = os.getenv("PAYGRID_PRODUCTION_SENDER_ID")
    else:
        api_key = os.getenv("PAYGRID_API_KEY")
        sender_id = "CommsGrid"

    if not api_key or not base_url or not sender_id:
        print("SMS settings are missing from .env")
        return False, None, None

    payload = {
        "recipient": [phone_number],
        "message": message,
        "sender_id": sender_id
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

        print("SMS environment:", environment)
        print("SMS HTTP status:", response.status_code)

        if response.ok:
            print("SMS API response:", response.text)

            try:
                result = response.json()
            except ValueError:
                return False, None, None

            data = result.get("data", {})
            details = data.get("details", [])
            sms_details = details[0] if details else {}

            message_id = sms_details.get("message_id")
            sms_status = sms_details.get("status")

            return True, message_id, sms_status

        print("SMS request failed:", response.text)
        return False, None, None

    except requests.RequestException as error:
        print("SMS connection error:", error)
        return False, None, None


with app.app_context():
    db.create_all()

@app.route("/sms-notifications", methods=["GET"])
def get_sms_notifications():
   notifications = SMSNotification.query.order_by(
      SMSNotification.created_at.desc()
   ).all()

   return jsonify({
      "count": len(notifications),
      "notifications": [
         {
            "id": notification.id,
            "attendance_id": notification.attendance_id,
            "notification_type": notification.notification_type,
            "recipient_phone": notification.recipient_phone,
            "message_id": notification.message_id,
            "status": notification.status,
            "created_at": notification.created_at.isoformat()
         }
         for notification in notifications
      ]
   }), 200


@app.route("/sms-status/<string:message_id>", methods=["GET"])
def check_sms_status(message_id):
   environment = os.getenv("PAYGRID_ENVIRONMENT", "SANDBOX").upper()
   base_url = os.getenv("PAYGRID_BASE_URL", "").rstrip("/")

   if environment == "PRODUCTION":
      api_key = os.getenv("PAYGRID_PRODUCTION_API_KEY")
   else:
      api_key = os.getenv("PAYGRID_API_KEY")

   if not api_key or not base_url:
      return jsonify({
         "error": "SMS settings are missing from .env"
      }), 500

   try:
      response = requests.get(
         f"{base_url}/sms/status/{message_id}",
         headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
         },
         timeout=20
      )

      try:
         result = response.json()
      except ValueError:
         return jsonify({
            "error": "Paygrid returned an invalid JSON response"
         }), 502

      if not response.ok:
         return jsonify(result), response.status_code

      #update the database only if Paygrid returns a status in the expected location
      data = result.get("data", {})
      if isinstance(data, dict):
         sms_status = data.get("status")

         if isinstance(sms_status, str) and sms_status.strip():
            notification = SMSNotification.query.filter_by(
               message_id=message_id
            ).first()

            if notification:
               notification.status = sms_status.strip().upper()
               db.session.commit()

      return jsonify(result), response.status_code

   except requests.RequestException as error:
      print("SMS status connection error:", error)
      return jsonify({
         "error": "Could not connect to Paygrid"
      }), 502
   except Exception as error:
      db.session.rollback()
      print("SMS status processing error", error)
      return jsonify({
         "error": "Could not process SMS status"
      }), 500

@app.route("/students/<int:student_id>/guardians", methods=["POST"])
def add_guardian(student_id):
   student = Student.query.get(student_id)

   if student is None:
      return jsonify({
         "message": "Student not found"
      }), 404

   data = request.get_json()

   if not data:
      return jsonify({
         "message": "Request body is required"
      }), 400
   
   required_fields = ["full_name", "phone", "relationship"]

   for field in required_fields:
      if not isinstance(data.get(field), str) or not data[field].strip():
         return jsonify({
            "message": f"{field} is required"
         }), 400

   phone = data["phone"].strip()

   if not phone.isdigit() or len(phone) < 10 or len(phone) > 15:
      return jsonify({
         "message": "Invalid phone number"
      }), 400

   guardian = Guardian(
      student_id=student.id,
      full_name=data["full_name"].strip(),
      phone=phone,
      relationship=data["relationship"].strip(),
      sms_enabled=data.get("sms_enabled", True),
      is_active=True
   )

   db.session.add(guardian)
   db.session.commit()

   return jsonify({
      "message": "Guardian added successfully",
      "guardian": {
         "id": guardian.id,
         "student_id": guardian.student_id,
         "full_name": guardian.full_name,
         "phone": guardian.phone,
         "relationship": guardian.relationship,
         "sms_enabled": guardian.sms_enabled,
         "is_active": guardian.is_active
      }
   }), 201

   

if __name__ == "__main__":
  app.run(port=5555, debug=True)