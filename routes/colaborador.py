from flask import Blueprint, jsonify, request, abort
from models import Colaborador
from database import db

colaborador_bp = Blueprint('colaborador_bp', __name__)

@colaborador_bp.route('/colaborador', methods=['GET'], strict_slashes=False)
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
def create_colaborador():
    data = request.get_json()
    cupom = data.get('cupom')
    nome = data.get('nome')
    funcao = data.get('funcao')
    time = data.get('time')

    try:
        # Verificar duplicidade
        existing_colaborador = Colaborador.query.filter(
            (Colaborador.cupom == cupom) | (Colaborador.nome == nome)
        ).first()

        if existing_colaborador:
            return jsonify({'error': 'Cupom ou nome já existe'}), 409

        # Inserir novo colaborador
        new_colaborador = Colaborador(cupom=cupom, nome=nome, funcao=funcao, time=time)
        db.session.add(new_colaborador)
        db.session.commit()
        return jsonify({'message': 'Colaborador criado com sucesso'}), 201
    except Exception as e:
        print(f"Erro ao criar colaborador: {e}")
        return jsonify({'error': 'Erro ao criar colaborador'}), 500

@colaborador_bp.route('/colaborador', methods=['DELETE'], strict_slashes=False)
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
def update_colaborador(cupom):
    data = request.get_json()
    nome = data.get('nome')
    funcao = data.get('funcao')
    time = data.get('time')

    try:
        colaborador = Colaborador.query.filter_by(cupom=cupom).first()
        if colaborador is None:
            return jsonify({'error': 'Colaborador não encontrado'}), 404

        colaborador.nome = nome
        colaborador.funcao = funcao
        colaborador.time = time
        db.session.commit()
        return jsonify({'message': 'Colaborador atualizado com sucesso'}), 200
    except Exception as e:
        print(f"Erro ao atualizar colaborador: {e}")
        return jsonify({'error': 'Erro ao atualizar colaborador'}), 500
