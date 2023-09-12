import os
from flask import Flask
from dotenv import load_dotenv
from db import db


app = Flask(__name__)
load_dotenv()

app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL")
db.init_app(app)