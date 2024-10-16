from flask import Blueprint, app, jsonify, request, abort
from models.ColaboradorChb import Departamento, Funcionario, Rescisao
from models.colaborador import Colaborador
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required
import cx_Oracle
from database import connect_to_oracle, db

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
    # sobrenome = data.get('sobrenome')
    funcao = data.get('funcao')
    time = data.get('time')
    email = data.get('email')
    password = data.get('password')
    dtadmissao=data.get('dtadmissao')
    dtdemissao=data.get('dtdemissao')
    
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
        # sobrenome=sobrenome,
        funcao=funcao,
        time=time,
        email=email,
        password=hashed_password,
        dtadmissao=dtadmissao,
        dtdemissao=dtdemissao
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
    # sobrenome = data.get('sobrenome')
    funcao = data.get('funcao')
    time = data.get('time')
    email = data.get('email')
    password = data.get('password')
    dtadmissao=data.get('dtadmissao')
    dtdemissao=data.get('dtdemissao')
    print(data)
    try:
        colaborador = Colaborador.query.filter_by(cupom=cupom).first()
        if colaborador is None:
            return jsonify({'error': 'Colaborador não encontrado'}), 404

        colaborador.nome = nome
        # colaborador.sobrenome = sobrenome
        colaborador.funcao = funcao
        colaborador.time = time
        colaborador.email = email
        colaborador.password = password
        colaborador.dtadmissao=dtadmissao
        colaborador.dtdemissao=dtdemissao
        db.session.commit()
        return jsonify({'message': 'Colaborador atualizado com sucesso'}), 200
    except Exception as e:
        print(f"Erro ao atualizar colaborador: {e}")
        return jsonify({'error': 'Erro ao atualizar colaborador'}), 500

@colaborador_bp.route('/colaboradorChb', methods=['GET'], strict_slashes=False)
def consultar_colaboradorChb():
    try:
        # Query para buscar colaboradores da empresa com pe01codemp = 36
        colaboradores = db.session.query(Funcionario, Departamento, Rescisao).\
            outerjoin(Departamento, (Funcionario.pe01codemp == Departamento.pe01codemp) & (Funcionario.fp03depto == Departamento.fp03depto)).\
            outerjoin(Rescisao, (Funcionario.pe01codemp == Rescisao.pe01codemp) & (Funcionario.fp02cod == Rescisao.fp02cod)).\
            filter(Funcionario.pe01codemp == 36).\
            all()

        # Preparar os resultados para retornar em formato JSON
        resultado = []
        for func, dept, resc in colaboradores:
            colaborador_info = func.to_dict()  # Certifique-se de que o método to_dict() está implementado corretamente
            
            # Converte a data de demissão para o formato aaaa-mm-dd ou define como 2099-12-31
            if resc and resc.fp74dtresc:
                colaborador_info['dt_demissao'] = resc.fp74dtresc.strftime('%Y-%m-%d')
            else:
                colaborador_info['dt_demissao'] = '2099-12-31'
                
            # Converte a data de admissão para o formato aaaa-mm-dd
            if func.fp02dtadmi:  # Verifica se a data de admissão não é None
                colaborador_info['fp02dtadmi'] = func.fp02dtadmi.strftime('%Y-%m-%d')
            else:
                colaborador_info['fp02dtadmi'] = None  # Ou algum valor padrão, se necessário

            # Remove espaços vazios das strings
            colaborador_info['fp02nom'] = colaborador_info['fp02nom'].strip()
            colaborador_info['fp03depto'] = colaborador_info['fp03depto'].strip()
            
            # Adiciona informações do departamento, garantindo que dept não é None
            colaborador_info['nome_depto'] = dept.fp03descri.strip() if dept and dept.fp03descri else None
            
            # Adiciona as informações processadas ao resultado
            resultado.append(colaborador_info)

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    