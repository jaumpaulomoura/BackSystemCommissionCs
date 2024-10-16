from datetime import datetime, timedelta
from flask_mail import Mail, Message
import secrets
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask import Blueprint, app, request, jsonify

from werkzeug.security import generate_password_hash, check_password_hash
from models.colaborador import Colaborador
from database import db
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config



login_bp = Blueprint('login', __name__)
mail = Mail()






@login_bp.route('/forgotPassword', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    
    user = Colaborador.query.filter_by(email=email).first()
    if not user:
        print(f'Email not found: {email}')
        return jsonify({'message': 'Email not found'}), 404

    token = create_access_token(identity=user.email, expires_delta=timedelta(hours=1))

    from_email = Config.SMTP_USERNAME
    to_email = email
    subject = 'Alterar Senha'
    body = f'Clique nesse link para cadastrar uma nova senha http://192.168.12.58:5001/emailPassword/{token}'

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        
        # Send the email
        server.sendmail(from_email, to_email, msg.as_string())
        print('Email enviado com sucesso!')
        
        return jsonify({'message': 'E-mail de redefinição de senha enviado'}), 200

    except smtplib.SMTPAuthenticationError as e:
        print(f'SMTP Authentication Error: {e}')
        return jsonify({'message': 'Email could not be sent due to authentication error'}), 500

    except Exception as e:
        print(f'An error occurred: {e}')
        return jsonify({'message': 'Email could not be sent'}), 500

    finally:
        server.quit()  







































@login_bp.route('/login', methods=['POST'])
def login():
    from main import jwt
      # Importa localmente dentro da função
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    colaborador = Colaborador.query.filter_by(email=email).first()
    if colaborador and check_password_hash(colaborador.password, password):
        access_token = create_access_token(identity=colaborador.email, expires_delta=timedelta(hours=9))
        return jsonify(access_token=access_token), 200

    return jsonify({'message': 'Invalid credentials'}), 401






@login_bp.route('/login', methods=['PUT'])
@jwt_required()
def update_password():
    data = request.get_json()
   
    email = data.get('email')
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not email or not current_password or not new_password:
        return jsonify({'message': 'Missing required fields'}), 400

    user = Colaborador.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, current_password):
        return jsonify({'message': 'Senha Incorreta'}), 401

    user.password = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'message': 'Password updated successfully'}), 200

@login_bp.route('/resetPassword', methods=['PUT'])
@jwt_required()
def reset_password():
    current_user_email = get_jwt_identity()
    data = request.get_json()
    new_password = data.get('new_password')

    # Verifica se a nova senha foi fornecida
    if not new_password:
        return jsonify({'message': 'Nova senha é necessária'}), 400

    # Procura o usuário pelo e-mail
    user = Colaborador.query.filter_by(email=current_user_email).first()
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404

    # Atualiza a senha do usuário
    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({'message': 'Senha atualizada com sucesso'}), 200
