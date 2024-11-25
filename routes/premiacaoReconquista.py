from cgitb import text
from flask import Blueprint, jsonify, request, abort
from database import db
from models.premiacaoReconquista import PremiacaoReconquista
premiacaoReconquista_bp = Blueprint('premiacaoReconquista_bp', __name__)
from flask_jwt_extended import jwt_required         
         
       
         
         
         
@premiacaoReconquista_bp.route('/premiacaoReconquista', methods=['GET'], strict_slashes=False)
@jwt_required()
def consultar_premiacaoReconquista():
    try:
        time_colaborador = request.args.get('time')
        
        query = PremiacaoReconquista.query
        
        if time_colaborador:
            query = query.filter_by(time=time_colaborador)
        
        premiacaoReconquistaes = query.all()
        
        results_col = [premiacaoReconquista.to_dict() for premiacaoReconquista in premiacaoReconquistaes]
        
        response = jsonify(results_col)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    
    except Exception as e:
        print(f"Erro na consulta SQL: {e}")
        return jsonify({'error': 'Erro na consulta SQL'}), 500



@premiacaoReconquista_bp.route('/premiacaoReconquista', methods=['POST'])
@jwt_required()
def create_premiacaoReconquista():
    data = request.get_json()
    descricao = data.get('descricao')
    time = data.get('time')
    valor = data.get('valor')
    minimo = data.get('minimo')
    maximo = data.get('maximo')
    try:
        existing_premiacaoReconquista = PremiacaoReconquista.query.filter(
            (PremiacaoReconquista.descricao == descricao) & (PremiacaoReconquista.time == time)
        ).first()

        if existing_premiacaoReconquista:
            return jsonify({'error': 'Cupom ou nome já existe'}), 409

        new_premiacaoReconquista = PremiacaoReconquista(descricao=descricao, time=time, valor=valor,minimo=minimo,maximo=maximo)
        db.session.add(new_premiacaoReconquista)
        db.session.commit()
        return jsonify({'message': 'PremiacaoReconquista criado com sucesso'}), 201
    except Exception as e:
        print(f"Erro ao criar premiacaoReconquista: {e}")
        return jsonify({'error': 'Erro ao criar premiacaoReconquista'}), 500

@premiacaoReconquista_bp.route('/premiacaoReconquista', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_premiacaoReconquista():
    descricao = request.args.get('descricao')
    time = request.args.get('time')
    valor = request.args.get('valor')

    print(f"Dados recebidos: descricao={descricao}, time={time}, valor={valor}")
    try:
        query = PremiacaoReconquista.query
        if descricao:
            query = query.filter_by(descricao=descricao)
        if time:
            query = query.filter_by(time=time)
        if valor:
            query = query.filter_by(valor=valor)
        premiacaoReconquista = query.first()
        if premiacaoReconquista is None:
            return jsonify({'error': 'PremiacaoReconquista não encontrado'}), 404

        db.session.delete(premiacaoReconquista)
        db.session.commit()
        return jsonify({'message': 'PremiacaoReconquista deletado com sucesso'}), 200
    except Exception as e:
        print(f"Erro ao deletar premiacaoReconquista: {e}")
        return jsonify({'error': 'Erro ao deletar premiacaoReconquista'}), 500

@premiacaoReconquista_bp.route('/premiacaoReconquista/<string:descricao>', methods=['PUT'])
@jwt_required()
def update_premiacaoReconquista(descricao):
    data = request.get_json()
    time = data.get('time')
    valor = float(data.get('valor'))
    minimo = (data.get('minimo'))
    maximo = (data.get('maximo'))

    try:
        

        premiacaoReconquista_records = PremiacaoReconquista.query.filter(
            PremiacaoReconquista.descricao == descricao,
            PremiacaoReconquista.time == time
        ).all()

        
        if len(premiacaoReconquista_records) == 0:
            return jsonify({'error': 'PremiacaoReconquista não encontrada'}), 404
        elif len(premiacaoReconquista_records) > 1:
            return jsonify({'error': f'Mais de um registro encontrado: {len(premiacaoReconquista_records)} registros correspondem.'}), 400

        premiacaoReconquista_record = premiacaoReconquista_records[0]

       
        premiacaoReconquista_record.valor = valor
        premiacaoReconquista_record.minimo = minimo
        premiacaoReconquista_record.maximo = maximo

        db.session.commit()

        return jsonify({'message': 'PremiacaoReconquista atualizada com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar premiacaoReconquista: {e}")
        return jsonify({'error': 'Erro ao atualizar premiacaoReconquista'}), 500

