from extensions import db

class Guardian(db.Model):
  __tablename__ = "guardians"

  id = db.Column(db.Integer, primary_key=True)

  student_id = db.Column(
    db.Integer,
    db.ForeignKey("students.id"),
    nullable=False
  )

  full_name = db.Column(db.String(150), nullable=False)
  phone = db.Column(db.String(20), nullable=False)
  relationship = db.Column(db.String(50), nullable=False)

  sms_enabled = db.Column(db.Boolean, default=True, nullable=False)
  is_active = db.Column(db.Boolean, default=True, nullable=False)