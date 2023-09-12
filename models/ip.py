from db import db

class ReverseIP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_ip = db.Column(db.String(18))
    reversed_ip = db.Column(db.String(18))