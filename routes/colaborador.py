from flask import Blueprint, jsonify, request, abort
from models.colaborador import Colaborador
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required

from database import db

colaborador_bp = Blueprint('colaborador_bp', __name__)

@colaborador_bp.route('/colaborador', methods=['GET'], strict_slashes=False)
@jwt_required()
def consultar_colaborador():
    try:
        colaboradores = Colaborador.query.all()
        results_col = [colaborador.to_dict() for colaborador in colaboradores]
        response = jsonify(results_col)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    except Exception as e:
        print(f"Erro na consulta SQL: {e}")
        return jsonify({'error': 'Erro na consulta SQL'}), 500

@colaborador_bp.route('/colaborador', methods=['POST'])
@jwt_required()
def create_colaborador():
    data = request.get_json()
    cupom = data.get('cupom')
    nome = data.get('nome')
    sobrenome = data.get('sobrenome')
    funcao = data.get('funcao')
    time = data.get('time')
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    # Verifica se o colaborador já existe
    existing_colaborador = Colaborador.query.filter_by(email=email).first()
    if existing_colaborador:
        return jsonify({'message': 'User already exists'}), 409

    # Cria um novo colaborador
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_colaborador = Colaborador(
        cupom=cupom,
        nome=nome,
        sobrenome=sobrenome,
        funcao=funcao,
        time=time,
        email=email,
        password=hashed_password
    )
    
    try:
        db.session.add(new_colaborador)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred'}), 500

@colaborador_bp.route('/colaborador', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_colaborador():
    cupom = request.args.get('cupom')
    nome = request.args.get('nome')
    funcao = request.args.get('funcao')
    time = request.args.get('time')

    try:
        query = Colaborador.query
        if cupom:
            query = query.filter_by(cupom=cupom)
        if nome:
            query = query.filter_by(nome=nome)
        if funcao:
            query = query.filter_by(funcao=funcao)
        if time:
            query = query.filter_by(time=time)

        colaborador = query.first()
        if colaborador is None:
            return jsonify({'error': 'Colaborador não encontrado'}), 404

        db.session.delete(colaborador)
        db.session.commit()
        return jsonify({'message': 'Colaborador deletado com sucesso'}), 200
    except Exception as e:
        print(f"Erro ao deletar colaborador: {e}")
        return jsonify({'error': 'Erro ao deletar colaborador'}), 500


@colaborador_bp.route('/colaborador/<string:cupom>', methods=['PUT'])
@jwt_required()
def update_colaborador(cupom):
    data = request.get_json()
    nome = data.get('nome')
    sobrenome = data.get('sobrenome')
    funcao = data.get('funcao')
    time = data.get('time')
    email = data.get('email')
    password = data.get('password')
    print(data)
    try:
        colaborador = Colaborador.query.filter_by(cupom=cupom).first()
        if colaborador is None:
            return jsonify({'error': 'Colaborador não encontrado'}), 404

        colaborador.nome = nome
        colaborador.sobrenome = sobrenome
        colaborador.funcao = funcao
        colaborador.time = time
        colaborador.email = email
        colaborador.password = password
        db.session.commit()
        return jsonify({'message': 'Colaborador atualizado com sucesso'}), 200
    except Exception as e:
        print(f"Erro ao atualizar colaborador: {e}")
        return jsonify({'error': 'Erro ao atualizar colaborador'}), 500
