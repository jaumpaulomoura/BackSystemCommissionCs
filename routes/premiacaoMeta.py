from cgitb import text
from flask import Blueprint, jsonify, request, abort
from database import db
from flask_jwt_extended import jwt_required
from models.premiacaoMeta import PremiacaoMeta





premiacaoMeta_bp = Blueprint('premiacaoMeta_bp', __name__)
         
         
       
         
         
         
@premiacaoMeta_bp.route('/premiacaoMeta', methods=['GET'], strict_slashes=False)
@jwt_required()
def consultar_premiacaoMeta():
    try:
        # Obter o valor do parâmetro de consulta 'time', se presente
        time_colaborador = request.args.get('time')
        
        # Iniciar a consulta na tabela PremiacaoMeta
        query = PremiacaoMeta.query
        
        # Se o parâmetro 'time' estiver presente, aplicar filtro
        if time_colaborador:
            query = query.filter_by(time=time_colaborador)
        
        # Executar a consulta
        premiacaoMetaes = query.all()
        
        # Converter os resultados para dicionários
        results_col = [premiacaoMeta.to_dict() for premiacaoMeta in premiacaoMetaes]
        
        # Criar a resposta JSON
        response = jsonify(results_col)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    
    except Exception as e:
        # Exibir erro no console e retornar resposta de erro
        print(f"Erro na consulta SQL: {e}")
        return jsonify({'error': 'Erro na consulta SQL'}), 500



@premiacaoMeta_bp.route('/premiacaoMeta', methods=['POST'])
@jwt_required()
def create_premiacaoMeta():
    data = request.get_json()
    descricao = data.get('descricao')
    time = data.get('time')
    valor = data.get('valor')
    try:
        # Verificar duplicidade
        # Verificar duplicidade
        existing_premiacaoMeta = PremiacaoMeta.query.filter(
            (PremiacaoMeta.descricao == descricao) &
            (PremiacaoMeta.time == time) &
            (PremiacaoMeta.valor == valor)
        ).first()


        if existing_premiacaoMeta:
            return jsonify({'error': 'Cupom ou nome já existe'}), 409

        # Inserir novo premiacaoMeta
        new_premiacaoMeta = PremiacaoMeta(descricao=descricao, time=time, valor=valor)
        db.session.add(new_premiacaoMeta)
        db.session.commit()
        return jsonify({'message': 'PremiacaoMeta criado com sucesso'}), 201
    except Exception as e:
        print(f"Erro ao criar premiacaoMeta: {e}")
        return jsonify({'error': 'Erro ao criar premiacaoMeta'}), 500

@premiacaoMeta_bp.route('/premiacaoMeta', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_premiacaoMeta():
    descricao = request.args.get('descricao')
    time = request.args.get('time')
    valor = request.args.get('valor')

    try:
        query = PremiacaoMeta.query
        if descricao:
            query = query.filter_by(descricao=descricao)
        if time:
            query = query.filter_by(time=time)
        if valor:
            query = query.filter_by(valor=valor)
        premiacaoMeta = query.first()
        if premiacaoMeta is None:
            return jsonify({'error': 'PremiacaoMeta não encontrado'}), 404

        db.session.delete(premiacaoMeta)
        db.session.commit()
        return jsonify({'message': 'PremiacaoMeta deletado com sucesso'}), 200
    except Exception as e:
        print(f"Erro ao deletar premiacaoMeta: {e}")
        return jsonify({'error': 'Erro ao deletar premiacaoMeta'}), 500

@premiacaoMeta_bp.route('/premiacaoMeta/<string:descricao>', methods=['PUT'])
@jwt_required()
def update_premiacaoMeta(descricao):
    data = request.get_json()
    time = data.get('time')
    valor = float(data.get('valor'))

    try:
        

        premiacaoMeta_records = PremiacaoMeta.query.filter(
            PremiacaoMeta.descricao == descricao,
            PremiacaoMeta.time == time
        ).all()

        
        if len(premiacaoMeta_records) == 0:
            return jsonify({'error': 'PremiacaoMeta não encontrada'}), 404
        elif len(premiacaoMeta_records) > 1:
            return jsonify({'error': f'Mais de um registro encontrado: {len(premiacaoMeta_records)} registros correspondem.'}), 400

        premiacaoMeta_record = premiacaoMeta_records[0]

       
        premiacaoMeta_record.valor = valor

        db.session.commit()

        return jsonify({'message': 'PremiacaoMeta atualizada com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar premiacaoMeta: {e}")
        return jsonify({'error': 'Erro ao atualizar premiacaoMeta'}), 500

