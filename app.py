import os
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from db import db
import models
from models import ReverseIP


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
load_dotenv()
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///data.db")
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def get_reverse_ip():
    client_ip = request.headers.get('X-Forwarded-For')
    if client_ip:
        reverse_ip = '.'.join(reversed(client_ip.split('.')))
        reversed_ip_obj = ReverseIP(original_ip=client_ip, reversed_ip=reverse_ip)

        try:
            db.session.add(reversed_ip_obj)
            db.session.commit()
            return f"Reversed IP: {reverse_ip} is Stored"
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"
    else:
        return "X-Forwarded-For header not found in the request."