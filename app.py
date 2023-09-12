import os
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from db import db
import models
from models import ReverseIP


app = Flask(__name__)
load_dotenv()
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///data.db")
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def get_reverse_ip():
    client_ip = request.remote_addr
    reverse_ip = '.'.join(reversed(client_ip.split('.')))
    reversed_ip_obj = ReverseIP(original_ip=client_ip, reversed_ip=reverse_ip)

    try:
        db.session.add(reversed_ip_obj)
        db.session.commit()
        return f"Reverse IP: {reverse_ip} (Stored in the database)"
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}"

    return f"Reversed IP: {reverse_ip}"