# login.py
from flask_jwt_extended import create_access_token
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from models.colaborador import Colaborador

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    from main import jwt  # Importa localmente dentro da função
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    colaborador = Colaborador.query.filter_by(email=email).first()
    if colaborador and check_password_hash(colaborador.password, password):
        access_token = create_access_token(identity=colaborador.email)
        return jsonify(access_token=access_token), 200

    return jsonify({'message': 'Invalid credentials'}), 401

