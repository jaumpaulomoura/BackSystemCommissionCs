from cgitb import text
from flask import Blueprint, jsonify, request, abort
from flask_jwt_extended import jwt_required
from models.meta import Meta
from flask_jwt_extended import jwt_required
from models.colaborador import Colaborador
from sqlalchemy.orm import aliased

from database import db

meta_bp = Blueprint('meta_bp', __name__)


@meta_bp.route('/meta', methods=['GET'], strict_slashes=False)
@jwt_required()
def consultar_meta():
    try:
        cupom_vendedora = request.args.get('cupomvendedora')
        time_colaborador = request.args.get('time')
        colaborador_alias = aliased(Colaborador)
        # Inicializa a consulta com join
        query = db.session.query(Meta, colaborador_alias).outerjoin(
            colaborador_alias, Meta.cupom == colaborador_alias.cupom
        )

        if cupom_vendedora:
            query = query.filter(Meta.cupom == cupom_vendedora)
        elif time_colaborador:
            colaboradores = Colaborador.query.filter_by(time=time_colaborador).all()
            cupoms = [colaborador.cupom for colaborador in colaboradores]
            query = query.filter(Meta.cupom.in_(cupoms))

        results = query.all()

        results_col = []
        for meta, colaborador in results:
            results_col.append({
                'id': f"{meta.cupom}_{meta.mes_ano}_{meta.meta}",
                'cupom': meta.cupom,
                'meta': meta.meta,
                'porcentagem': meta.porcentagem,
                'valor': meta.valor,
                'mes_ano': meta.mes_ano,
                'colaborador_nome': colaborador.nome if colaborador else None,
                'colaborador_time': colaborador.time if colaborador else None
            })

        response = jsonify(results_col)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except Exception as e:
        print(f"Erro na consulta SQL: {e}")
        return jsonify({'error': 'Erro na consulta SQL'}), 500

@meta_bp.route('/meta', methods=['POST'])
@jwt_required()
def create_meta():
    data = request.get_json()

    # Verificar se a solicitação contém um array de objetos
    if not isinstance(data, list):
        return jsonify({'error': 'Formato inválido, espere um array de objetos.'}), 400

    errors = []
    success_messages = []

    for item in data:
        cupom = item.get('cupom')
        meta = item.get('meta')
        porcentagem = item.get('porcentagem')
        valor = item.get('valor')
        mes_ano = item.get('mes_ano')

        try:
            # Verificar duplicidade
            existing_meta = Meta.query.filter(
                (Meta.cupom == cupom) &
                (Meta.meta == meta) &
                (Meta.mes_ano == mes_ano)
            ).first()

            if existing_meta:
                errors.append({'cupom': cupom, 'meta': meta, 'mes_ano': mes_ano, 'error': 'A combinação já existe'})
                continue  # Pular para o próximo item

            # Inserir nova meta
            new_meta = Meta(cupom=cupom, meta=meta, porcentagem=porcentagem, valor=valor, mes_ano=mes_ano)
            db.session.add(new_meta)
            success_messages.append({'cupom': cupom, 'meta': meta, 'mes_ano': mes_ano, 'message': 'Meta criada com sucesso'})

        except Exception as e:
            print(f"Erro ao criar meta: {e}")
            errors.append({'cupom': cupom, 'meta': meta, 'mes_ano': mes_ano, 'error': 'Erro ao criar meta'})

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar alterações no banco de dados: {e}")
        return jsonify({'error': 'Erro ao salvar alterações no banco de dados'}), 500

    return jsonify({
        'success': success_messages,
        'errors': errors
    }), 201



@meta_bp.route('/meta', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_meta():
    cupom = request.args.get('cupom')
    meta = request.args.get('meta')
    porcentagem = request.args.get('porcentagem')
    valor = request.args.get('valor')
    mes_ano = request.args.get('mes_ano')

    try:
        query = Meta.query
        if cupom:
            query = query.filter_by(cupom=cupom)
        if meta:
            query = query.filter_by(meta=meta)
        if porcentagem:
            query = query.filter_by(porcentagem=porcentagem)
        if valor:
            query = query.filter_by(valor=valor)
        if mes_ano:
            query = query.filter_by(mes_ano=mes_ano)
        meta = query.first()
        if meta is None:
            return jsonify({'error': 'Meta não encontrado'}), 404

        db.session.delete(meta)
        db.session.commit()
        return jsonify({'message': 'Meta deletado com sucesso'}), 200
    except Exception as e:
        print(f"Erro ao deletar meta: {e}")
        return jsonify({'error': 'Erro ao deletar meta'}), 500

@meta_bp.route('/meta/<string:cupom>', methods=['PUT'])
@jwt_required()
def update_meta(cupom):
    data = request.get_json()
    novo_meta = data.get('meta')
    porcentagem = float(data.get('porcentagem'))
    valor = float(data.get('valor'))
    mes_ano = data.get('mes_ano')

    try:
        

        meta_records = Meta.query.filter(
            Meta.cupom == cupom,
            Meta.mes_ano == mes_ano,
            Meta.meta == novo_meta
        ).all()

        
        if len(meta_records) == 0:
            return jsonify({'error': 'Meta não encontrada'}), 404
        elif len(meta_records) > 1:
            return jsonify({'error': f'Mais de um registro encontrado: {len(meta_records)} registros correspondem.'}), 400

        meta_record = meta_records[0]

       
        meta_record.porcentagem = porcentagem
        meta_record.valor = valor

        db.session.commit()

        return jsonify({'message': 'Meta atualizada com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar meta: {e}")
        return jsonify({'error': 'Erro ao atualizar meta'}), 500

