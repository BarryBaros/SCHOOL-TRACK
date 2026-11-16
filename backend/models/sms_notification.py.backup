from datetime import datetime
from extensions import db


class SMSNotification(db.Model):
  __tablename__ = "sms_notifications"

  id = db.Column(db.Integer, primary_key=True)

  attendance_id = db.Column(
    db.Integer,
    db.ForeignKey("attendance.id"),
    nullable=False
  )

  notification_type = db.Column(db.String(20), nullable=False)
  recipient_phone = db.Column(db.String(20), nullable=False)
  message_id = db.Column(db.String(100), nullable=True)
  status = db.Column(db.String(30), nullable=False, default="PENDING")

  created_at = db.Column(
    db.DateTime,
    nullable=False,
    default=datetime.utcnow
  )