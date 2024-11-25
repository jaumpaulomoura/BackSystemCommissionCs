from flask import Blueprint, request, jsonify
from sqlalchemy import and_, func
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
        return 0.0
    value = value.replace('R$', '').replace('.', '').replace(',', '.').strip()
    return float(value) if value else 0.0

def filter_orders(query, start_date_str, end_date_str, cupom_vendedora, time_colaborador):
    if start_date_str:
        try:
            start_date_local = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.timezone('America/Sao_Paulo'))
            start_date_utc = start_date_local.astimezone(pytz.utc)
            query = query.filter(VwcsEcomPedidosJp.data_submissao >= start_date_utc)
        except ValueError as e:
            return query, jsonify({'error': f'Formato de startDate invÃ¡lido. Use YYYY-MM-DD. Detalhes: {e}'}), 400

    if end_date_str:
        try:
            end_date_local = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=pytz.timezone('America/Sao_Paulo'))
            end_date_utc = end_date_local.astimezone(pytz.utc)
            query = query.filter(VwcsEcomPedidosJp.data_submissao <= end_date_utc)
        except ValueError as e:
            return query, jsonify({'error': f'Formato de endDate invÃ¡lido. Use YYYY-MM-DD. Detalhes: {e}'}), 400

    if cupom_vendedora:
        query = query.filter(VwcsEcomPedidosJp.cupom_vendedora.ilike(f'%{cupom_vendedora}%'))
    elif time_colaborador:
        colaboradores = Colaborador.query.filter_by(time=time_colaborador).all()
        cupoms = [colaborador.cupom for colaborador in colaboradores]
        if cupoms:
            query = query.filter(VwcsEcomPedidosJp.cupom_vendedora.in_(cupoms))
        else:
            return query, jsonify([]), 200 

    return query, None, None 

@orders_bp.route('/orders', methods=['GET'], strict_slashes=False)
# @jwt_required() 
def get_orders():
    start_date_str = request.args.get('startDate')
    end_date_str = request.args.get('endDate')
    cupom_vendedora = request.args.get('cupomvendedora')
    time_colaborador = request.args.get('time')
    local_tz = pytz.timezone('America/Sao_Paulo')
    
    subquery_aproved = db.session.query(VwcsEcomPedidosJp.pedido).join(
        Ticket, VwcsEcomPedidosJp.pedido == Ticket.orderId
    ).filter(
        Ticket.reason == 'Status para Cancelado',
        Ticket.status == 'Autorizado'
    ).subquery()

    approved_orders_query = db.session.query(
        VwcsEcomPedidosJp,
        Colaborador.nome,
        Colaborador.funcao,
        Colaborador.time,
        Colaborador.dtadmissao,
        Colaborador.dtdemissao
    ).outerjoin(
        Colaborador, and_(
            VwcsEcomPedidosJp.cupom_vendedora == Colaborador.cupom,
            Colaborador.dtadmissao <= VwcsEcomPedidosJp.data_submissao,
            Colaborador.dtdemissao >= VwcsEcomPedidosJp.data_submissao
        )
    ).filter(
        VwcsEcomPedidosJp.status == 'APROVADO',
        VwcsEcomPedidosJp.pedido.notin_(subquery_aproved)
    ).distinct()

    approved_orders_query, error_response, status_code = filter_orders(approved_orders_query, start_date_str, end_date_str, cupom_vendedora, time_colaborador)
    if error_response:
        return error_response, status_code

    
    subquery_reaproved = db.session.query(VwcsEcomPedidosJp.pedido).join(
        Ticket, VwcsEcomPedidosJp.pedido == Ticket.orderId
    ).filter(
        Ticket.reason == 'Status para Aprovado',
        Ticket.status == 'Autorizado'
    ).subquery()

    non_approved_orders_query = db.session.query(
        VwcsEcomPedidosJp,
        Colaborador.nome,
        Colaborador.funcao,
        Colaborador.time,
        Colaborador.dtadmissao,
        Colaborador.dtdemissao
    ).outerjoin(
        Ticket, VwcsEcomPedidosJp.pedido == Ticket.orderId
    ).outerjoin(
        Colaborador, and_(
            VwcsEcomPedidosJp.cupom_vendedora == Colaborador.cupom,
            Colaborador.dtadmissao <= VwcsEcomPedidosJp.data_submissao,
            Colaborador.dtdemissao >= VwcsEcomPedidosJp.data_submissao
        )
    ).filter(
        VwcsEcomPedidosJp.status != 'APROVADO',
        VwcsEcomPedidosJp.pedido.in_(subquery_reaproved)
    ).distinct()

    non_approved_orders_query, error_response, status_code = filter_orders(non_approved_orders_query, start_date_str, end_date_str, cupom_vendedora, time_colaborador)
    if error_response:
        return error_response, status_code

 
    union_query = approved_orders_query.union_all(non_approved_orders_query)

    try:
        orders = union_query.all()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    results = []
    for order in orders:
        order_dict = {
            'pedido': order.VwcsEcomPedidosJp.pedido,
            'data_submissao': order.VwcsEcomPedidosJp.data_submissao.isoformat(),
            'hora_submissao': order.VwcsEcomPedidosJp.hora_submissao.isoformat(),
            'cupom':order.VwcsEcomPedidosJp.cupom,
            'cupom_vendedora': order.VwcsEcomPedidosJp.cupom_vendedora,
            'id_cliente':order.VwcsEcomPedidosJp.id_cliente,
            'metodo_pagamento':order.VwcsEcomPedidosJp.metodo_pagamento,
            'parcelas':order.VwcsEcomPedidosJp.parcelas,
            'valor_pago': order.VwcsEcomPedidosJp.valor_pago,
            'valor_frete': order.VwcsEcomPedidosJp.valor_frete,
            'status': order.VwcsEcomPedidosJp.status,
            'total_itens': order.VwcsEcomPedidosJp.total_itens,
            'envio': order.VwcsEcomPedidosJp.envio,
            'idloja': order.VwcsEcomPedidosJp.idloja,
            'site': order.VwcsEcomPedidosJp.site,
            'valor_bruto': order.VwcsEcomPedidosJp.valor_bruto,
            'valor_desconto': order.VwcsEcomPedidosJp.valor_desconto,
            'valor_comissional': parse_currency(order.VwcsEcomPedidosJp.valor_pago) - parse_currency(order.VwcsEcomPedidosJp.valor_frete),
            'nome': order.nome,
            'funcao': order.funcao,
            'time': order.time,
            'dtadmissao': order.dtadmissao,
            'dtdemissao': order.dtdemissao
        }

        valor_pago = parse_currency(order_dict.get('valor_pago', ''))
        valor_frete = parse_currency(order_dict.get('valor_frete', ''))
        order_dict['valor_comissional'] = valor_pago - valor_frete
        
        results.append(order_dict)

    return jsonify(results) if results else jsonify([])
