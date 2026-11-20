from extensions import db
from datetime import datetime

class User(db.Model):
  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True)
  full_name = db.Column(db.String(150), nullable=False)
  email = db.Column(db.String(150), unique=True, nullable=False)
  password_hash = db.Column(db.String(255), nullable=False)
  role = db.Column(db.String(30), nullable=False, default="TEACHER")
  is_active = db.Column(db.Boolean, default=True, nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)