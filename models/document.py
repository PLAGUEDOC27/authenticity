from datetime import datetime
from extensions import db

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    original_text = db.Column(db.Text, nullable=True)
    plagiarism_score = db.Column(db.Float, default=0.0)  # 0–1
    ai_generated_prob = db.Column(db.Float, default=0.0)  # 0–1
