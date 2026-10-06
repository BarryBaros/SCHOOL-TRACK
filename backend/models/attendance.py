from extensions import db

class Attendance(db.Model):
  __tablename__ = "attendance"

  id = db.Column(db.Integer, primary_key=True)
  student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
  attendance_date = db.Column(db.Date, nullable=False)

  arrival_time = db.Column(db.DateTime, nullable=False)
  departure_time = db.Column(db.DateTime, nullable=True)