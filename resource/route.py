from sqlalchemy.exc import SQLAlchemyError
from flask import request, jsonify
from db import db
from models import ReverseIP

@app.route('/')
def get_reverse_ip():
    client_ip = request.remote_addr
    reverse_ip = '.'.join(reversed(client_ip.split('.')))
    # reversed_ip_obj = ReversedIP(original_ip=client_ip, reversed_ip=reverse_ip)

    # try:
    #     db.session.add(reversed_ip_obj)
    #     db.session.commit()
    #     return f"Reverse IP: {reverse_ip} (Stored in the database)"
    # except Exception as e:
    #     db.session.rollback()
    #     return f"Error: {str(e)}"

    return f"Your reversed IP: {reverse_ip}"