from flask import Flask, request, jsonify
from extensions import db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://baros:Kitinda%408893@localhost/school_track"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

from models.student import Student

@app.route("/")
def home():
  return "School Track API is running!"

@app.route("/students", methods=["POST"])
def create_student():
   data = request.get_json()
   student = Student(
        admission_number=data["admission_number"],
        first_name=data["first_name"],
        last_name=data["last_name"]
     )
   
   db.session.add(student)
   db.session.commit()

   return jsonify({
      "message": "Student created successfully",
      "student": {
         "id": student.id,
         "admission_number": student.admission_number,
         "first_name": student.first_name,
         "last_name": student.last_name
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
         "last_name": student.last_name
      }
      for student in students
   ])

with app.app_context():
    db.create_all()

if __name__ == "__main__":
  app.run(port=5555, debug=True)