from extensions import db
from datetime import datetime

class StudentQRCode(db.Model):
  __tablename__ = "student_qr_codes"

  id = db.Column(db.Integer, primary_key=True)

  student_id = db.Column(
    db.Integer,
    db.ForeignKey("students.id"),
    nullable=False
  )

  token = db.Column(
    db.String(128),
    unique=True,
    nullable=False,
    index=True
  )

  is_active = db.Column(
    db.Boolean,
    default=True,
    nullable=False
  )

  created_at = db.Column(
    db.DateTime,
    default=datetime.utcnow,
    nullable=False
  )

  deactivated_at = db.Column(db.DateTime, nullable=True)

  replacement_reason = db.Column(db.String(255), nullable=True)

  replaced_by_id = db.Column(
    db.Integer,
    db.ForeignKey("student_qr_codes.id"),
    nullable=True
  )