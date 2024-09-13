from flask import Blueprint, request, jsonify
from sqlalchemy import func
# from models import db, VwcsEcomPedidosJp, Colaborador
from flask_jwt_extended import jwt_required
from models.colaborador import Colaborador
from models.vwcsEcomPedidosJp import VwcsEcomPedidosJp
from database import db
from datetime import datetime
import pytz

orders_bp = Blueprint('orders_bp', __name__)

@orders_bp.route('/orders', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_orders():
    # Obtém os parâmetros da query
    start_date_str = request.args.get('startDate')
    end_date_str = request.args.get('endDate')
    cupom_vendedora = request.args.get('cupomvendedora')
    time_colaborador = request.args.get('time')

    # Configuração do fuso horário local
    local_tz = pytz.timezone('America/Sao_Paulo')

    # Consulta base
    # query = db.session.query(VwcsEcomPedidosJp).filter(VwcsEcomPedidosJp.status == 'APROVADO')
    query = db.session.query(VwcsEcomPedidosJp).filter(
        VwcsEcomPedidosJp.status == 'APROVADO'
    )

    # Filtro por datas
    if start_date_str:
        try:
            # Verifica e corrige a data de início
            start_date_local = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=local_tz)
            start_date_utc = start_date_local.astimezone(pytz.utc)
            query = query.filter(VwcsEcomPedidosJp.data_submissao >= start_date_utc)
        except ValueError as e:
            return jsonify({'error': f'Formato de startDate inválido. Use YYYY-MM-DD. Detalhes: {e}'}), 400

    if end_date_str:
        try:
            # Verifica e corrige a data de fim
            end_date_local = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=local_tz)
            end_date_utc = end_date_local.astimezone(pytz.utc)
            query = query.filter(VwcsEcomPedidosJp.data_submissao <= end_date_utc)
        except ValueError as e:
            return jsonify({'error': f'Formato de endDate inválido. Use YYYY-MM-DD. Detalhes: {e}'}), 400

    # Filtro por cupom_vendedora ou time_colaborador
    if cupom_vendedora:
        query = query.filter(VwcsEcomPedidosJp.cupom_vendedora.ilike(f'%{cupom_vendedora}%'))
    elif time_colaborador:
        colaboradores = Colaborador.query.filter_by(time=time_colaborador).all()
        cupoms = [colaborador.cupom for colaborador in colaboradores]
        if cupoms:
            query = query.filter(VwcsEcomPedidosJp.cupom_vendedora.in_(cupoms))
        else:
            # Se não houver colaboradores encontrados para o time dado, retorna resultado vazio
            return jsonify([])

    try:
        orders = query.all()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Converte os resultados em dicionários
    results = [order.to_dict() for order in orders]

    return jsonify(results) if results else jsonify([])





@orders_bp.route('/ordersTeste', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_ordersTeste():
    # Obtém os parâmetros da query
    start_date_str = request.args.get('startDate')
    end_date_str = request.args.get('endDate')
    cupom_vendedora = request.args.get('cupomvendedora')
    time_colaborador = request.args.get('time')

    # Configuração do fuso horário local
    local_tz = pytz.timezone('America/Sao_Paulo')

    # Consulta base
    query = db.session.query(VwcsEcomPedidosJp).filter(
        VwcsEcomPedidosJp.status == 'APROVADO',
        VwcsEcomPedidosJp.pedido == 'o52219749'  # Filtro adicional para o pedido específico
    )


    # Filtro por datas
    if start_date_str:
        try:
            # Verifica e corrige a data de início
            start_date_local = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=local_tz)
            start_date_utc = start_date_local.astimezone(pytz.utc)
            query = query.filter(VwcsEcomPedidosJp.data_submissao >= start_date_utc)
        except ValueError as e:
            return jsonify({'error': f'Formato de startDate inválido. Use YYYY-MM-DD. Detalhes: {e}'}), 400

    if end_date_str:
        try:
            # Verifica e corrige a data de fim
            end_date_local = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=local_tz)
            end_date_utc = end_date_local.astimezone(pytz.utc)
            query = query.filter(VwcsEcomPedidosJp.data_submissao <= end_date_utc)
        except ValueError as e:
            return jsonify({'error': f'Formato de endDate inválido. Use YYYY-MM-DD. Detalhes: {e}'}), 400

    # Filtro por cupom_vendedora ou time_colaborador
    if cupom_vendedora:
        query = query.filter(VwcsEcomPedidosJp.cupom_vendedora.ilike(f'%{cupom_vendedora}%'))
    elif time_colaborador:
        colaboradores = Colaborador.query.filter_by(time=time_colaborador).all()
        cupoms = [colaborador.cupom for colaborador in colaboradores]
        if cupoms:
            query = query.filter(VwcsEcomPedidosJp.cupom_vendedora.in_(cupoms))
        else:
            # Se não houver colaboradores encontrados para o time dado, retorna resultado vazio
            return jsonify([])

    try:
        orders = query.all()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Converte os resultados em dicionários
    results = [order.to_dict() for order in orders]

    return jsonify(results) if results else jsonify([])
