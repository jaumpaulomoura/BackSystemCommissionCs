from flask import Blueprint, request, jsonify
from sqlalchemy import func
# from models import db, VwcsEcomPedidosJp, Colaborador
from flask_jwt_extended import jwt_required
from models.colaborador import Colaborador
from models.ticket import Ticket
from models.vwcsEcomPedidosJp import VwcsEcomPedidosJp
from database import db
from datetime import datetime
import pytz

orders_bp = Blueprint('orders_bp', __name__)
def parse_currency(value):
    if value is None or value.strip() == '':
        return 0.0  # Retorna 0.0 se o valor for None ou uma string vazia
    # Remove espaços e substitui vírgula por ponto
    value = value.replace('R$', '').replace('.', '').replace(',', '.').strip()
    return float(value) if value else 0.0
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
    subquery_aproved = db.session.query(VwcsEcomPedidosJp.pedido).join(
        Ticket, VwcsEcomPedidosJp.pedido == Ticket.orderId
    ).filter(
        Ticket.reason == 'Status para Cancelado',
        Ticket.status == 'Autorizado'
    ).subquery()

    approved_orders_query = db.session.query(VwcsEcomPedidosJp).filter(
        VwcsEcomPedidosJp.status == 'APROVADO',
        VwcsEcomPedidosJp.pedido.notin_(subquery_aproved)
)


    # Filtro por datas
    if start_date_str:
        try:
            # Verifica e corrige a data de início
            start_date_local = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=local_tz)
            start_date_utc = start_date_local.astimezone(pytz.utc)
            approved_orders_query = approved_orders_query.filter(VwcsEcomPedidosJp.data_submissao >= start_date_utc)
        except ValueError as e:
            return jsonify({'error': f'Formato de startDate inválido. Use YYYY-MM-DD. Detalhes: {e}'}), 400

    if end_date_str:
        try:
            # Verifica e corrige a data de fim
            end_date_local = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=local_tz)
            end_date_utc = end_date_local.astimezone(pytz.utc)
            approved_orders_query = approved_orders_query.filter(VwcsEcomPedidosJp.data_submissao <= end_date_utc)
        except ValueError as e:
            return jsonify({'error': f'Formato de endDate inválido. Use YYYY-MM-DD. Detalhes: {e}'}), 400

    # Filtro por cupom_vendedora ou time_colaborador
    if cupom_vendedora:
        approved_orders_query = approved_orders_query.filter(VwcsEcomPedidosJp.cupom_vendedora.ilike(f'%{cupom_vendedora}%'))
    elif time_colaborador:
        colaboradores = Colaborador.query.filter_by(time=time_colaborador).all()
        cupoms = [colaborador.cupom for colaborador in colaboradores]
        if cupoms:
            approved_orders_query = approved_orders_query.filter(VwcsEcomPedidosJp.cupom_vendedora.in_(cupoms))
        else:
            # Se não houver colaboradores encontrados para o time dado, retorna resultado vazio
            return jsonify([])
   
    subquery_reaproved = db.session.query(VwcsEcomPedidosJp.pedido).join(
        Ticket, VwcsEcomPedidosJp.pedido == Ticket.orderId
    ).filter(
        Ticket.reason == 'Status para Aprovado',
        Ticket.status == 'Autorizado'
    ).subquery()
    
    non_approved_orders_query = db.session.query(VwcsEcomPedidosJp).join(
        Ticket, VwcsEcomPedidosJp.pedido == Ticket.orderId
    ).filter(
        VwcsEcomPedidosJp.status != 'APROVADO',
        VwcsEcomPedidosJp.pedido.in_(subquery_reaproved)
    )
   
   
   
   
    
    if start_date_str:
            try:
                # Verifica e corrige a data de início
                start_date_local = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=local_tz)
                start_date_utc = start_date_local.astimezone(pytz.utc)
                non_approved_orders_query = non_approved_orders_query.filter(VwcsEcomPedidosJp.data_submissao >= start_date_utc)
            except ValueError as e:
                return jsonify({'error': f'Formato de startDate inválido. Use YYYY-MM-DD. Detalhes: {e}'}), 400

    if end_date_str:
            try:
                # Verifica e corrige a data de fim
                end_date_local = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=local_tz)
                end_date_utc = end_date_local.astimezone(pytz.utc)
                non_approved_orders_query = non_approved_orders_query.filter(VwcsEcomPedidosJp.data_submissao <= end_date_utc)
            except ValueError as e:
                return jsonify({'error': f'Formato de endDate inválido. Use YYYY-MM-DD. Detalhes: {e}'}), 400

        # Filtro por cupom_vendedora ou time_colaborador
    if cupom_vendedora:
        non_approved_orders_query = non_approved_orders_query.filter(VwcsEcomPedidosJp.cupom_vendedora.ilike(f'%{cupom_vendedora}%'))
    elif time_colaborador:
            colaboradores = Colaborador.query.filter_by(time=time_colaborador).all()
            cupoms = [colaborador.cupom for colaborador in colaboradores]
            if cupoms:
                non_approved_orders_query = non_approved_orders_query.filter(VwcsEcomPedidosJp.cupom_vendedora.in_(cupoms))
            else:
                return jsonify([])
    
   
    union_query = approved_orders_query.union_all(non_approved_orders_query)
    try:
        orders = union_query.all()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Modificar a construção do resultado para incluir todos os campos e a diferença
# Modificar a construção do resultado para incluir todos os campos e a diferença
    results = []
    for order in orders:
        order_dict = order.to_dict()  # Convertendo o objeto em dicionário

        # Convertendo valor_pago e valor_frete para float e calculando a diferença
        valor_pago = parse_currency(order_dict.get('valor_pago', ''))
        valor_frete = parse_currency(order_dict.get('valor_frete', ''))

        # Calculando valor comissional
        order_dict['valor_comissional'] = valor_pago - valor_frete
        results.append(order_dict)

    return jsonify(results) if results else jsonify([])

