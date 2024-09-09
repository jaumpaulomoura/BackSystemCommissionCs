from flask import Blueprint, jsonify, request
import pytz
from sqlalchemy import func, and_
from models import Colaborador, SubmittedOrder, Ticket, db, VwcsEcomPedidosJp
from datetime import datetime, timedelta

reconquest_bp = Blueprint('reconquest_bp', __name__)
local_tz = pytz.timezone('America/Sao_Paulo')
def parse_date(date_str):
    """Parse a date string into a datetime object."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None

def format_date_for_query(date_obj):
    """Format a datetime object for use in a query."""
    return date_obj.strftime('%Y-%m-%d') if date_obj else None

def get_month_range(date):
    """Get the first and last day of the month for the given date."""
    first_day = date.replace(day=1)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    return first_day, last_day

def get_current_month_range(date):
    """Get the first and last day of the current month for the given date."""
    local_tz = pytz.timezone('America/Sao_Paulo')
    first_day_current_month = date.replace(day=1).replace(tzinfo=local_tz)
    last_day_current_month = (first_day_current_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    last_day_current_month = last_day_current_month.replace(tzinfo=local_tz)
    return first_day_current_month.astimezone(pytz.utc), last_day_current_month.astimezone(pytz.utc)

def get_previous_month_range(date):
    """Get the first and last day of the previous month for the given date."""
    first_day_current_month, _ = get_current_month_range(date)
    first_day_prev_month = first_day_current_month - timedelta(days=1)
    first_day_prev_month = first_day_prev_month.replace(day=1).replace(tzinfo=local_tz)
    last_day_prev_month = (first_day_prev_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    last_day_prev_month = last_day_prev_month.replace(tzinfo=local_tz)
    return first_day_prev_month.astimezone(pytz.utc), last_day_prev_month.astimezone(pytz.utc)


def get_all_orders(start_date=None, end_date=None, cupom_vendedora=None, time_colaborador=None):
    """Retrieve orders based on filters and calculate metrics."""
    local_tz = pytz.timezone('America/Sao_Paulo')
    formatted_start_date = format_date_for_query(parse_date(start_date)) if start_date else None
    formatted_end_date = format_date_for_query(parse_date(end_date)) if end_date else None

    # Convert start and end dates to UTC
    if formatted_start_date:
        start_date_local = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=local_tz)
        formatted_start_date = start_date_local.astimezone(pytz.utc).strftime('%Y-%m-%d')
    if formatted_end_date:
        end_date_local = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=local_tz)
        formatted_end_date = end_date_local.astimezone(pytz.utc).strftime('%Y-%m-%d')

    filters = [VwcsEcomPedidosJp.status == 'APROVADO']
    if formatted_start_date:
        filters.append(VwcsEcomPedidosJp.data_submissao >= formatted_start_date)
    if formatted_end_date:
        filters.append(VwcsEcomPedidosJp.data_submissao <= formatted_end_date)

    if time_colaborador:
        colaboradores = Colaborador.query.filter_by(time=time_colaborador).all()
        cupoms = [colaborador.cupom for colaborador in colaboradores]
        if cupoms:
            filters.append(VwcsEcomPedidosJp.cupom_vendedora.in_(cupoms))
            print("Cupons filtrados:", cupoms)  # Debug: cupons filtrados
    elif cupom_vendedora:
        filters.append(VwcsEcomPedidosJp.cupom_vendedora == cupom_vendedora)
        print("Cupom vendedor específico:", cupom_vendedora)  # Debug: cupom específico
    
    min_data_query = (
        db.session.query(
            VwcsEcomPedidosJp.cupom_vendedora,
            VwcsEcomPedidosJp.id_cliente,
            func.min(VwcsEcomPedidosJp.data_submissao).label('min_data')
        )
        .filter(and_(*filters))
        .group_by(VwcsEcomPedidosJp.cupom_vendedora, VwcsEcomPedidosJp.id_cliente)
        .subquery()
    )


    subquery = (
        db.session.query(
            VwcsEcomPedidosJp.id_cliente,
            func.max(VwcsEcomPedidosJp.data_submissao).label('last_order')
        )
        .join(min_data_query, VwcsEcomPedidosJp.id_cliente == min_data_query.c.id_cliente)
        .filter(
            and_(
                VwcsEcomPedidosJp.data_submissao < min_data_query.c.min_data,
                VwcsEcomPedidosJp.data_submissao.isnot(None),
                VwcsEcomPedidosJp.status == 'APROVADO' 
            )
        )
        .group_by(VwcsEcomPedidosJp.id_cliente)
        .subquery()
    )
    today = datetime.now()
    first_day_current_month, last_day_current_month = get_current_month_range(today)

    orders_query = (
        db.session.query(
            min_data_query.c.cupom_vendedora,
            min_data_query.c.id_cliente,
            min_data_query.c.min_data,
            subquery.c.last_order
        )
        .outerjoin(subquery, min_data_query.c.id_cliente == subquery.c.id_cliente)
    )

    orders_results = orders_query.all()

    combined_results = []
    for client_data in orders_results:
        min_data = client_data.min_data
        last_order = client_data.last_order

        days_difference = None
        days_mes_anterior = None

        if min_data and last_order:
            min_date = parse_date(format_date_for_query(min_data))
            last_order_date = parse_date(format_date_for_query(last_order))
            if min_date and last_order_date:
                days_difference = (min_date - last_order_date).days

        current_date = parse_date(format_date_for_query(min_data)) or datetime.now()
        first_day_prev_month, last_day_prev_month = get_previous_month_range(current_date)

        min_data_prev_month = (
            db.session.query(func.min(VwcsEcomPedidosJp.data_submissao))
            .filter(
                VwcsEcomPedidosJp.id_cliente == client_data.id_cliente,
                VwcsEcomPedidosJp.data_submissao >= first_day_prev_month,
                VwcsEcomPedidosJp.data_submissao <= last_day_prev_month,
                VwcsEcomPedidosJp.cupom_vendedora == cupom_vendedora,
                VwcsEcomPedidosJp.status == 'APROVADO'
            )
            .scalar()
        )

        last_order_prev_month = None
        if min_data_prev_month:
            last_order_prev_month = (
                db.session.query(func.max(VwcsEcomPedidosJp.data_submissao))
                .filter(
                    VwcsEcomPedidosJp.id_cliente == client_data.id_cliente,
                    VwcsEcomPedidosJp.data_submissao < min_data_prev_month,
                    VwcsEcomPedidosJp.status == 'APROVADO'
                )
                .scalar()
            )

        if min_data_prev_month and last_order_prev_month:
            min_data_prev_month_date = parse_date(format_date_for_query(min_data_prev_month))
            last_order_prev_month_date = parse_date(format_date_for_query(last_order_prev_month))
            if min_data_prev_month_date and last_order_prev_month_date:
                days_mes_anterior = (min_data_prev_month_date - last_order_prev_month_date).days

        status = ""
        if days_mes_anterior is not None and days_mes_anterior > 90:
            status = "Repagar"
        elif days_difference is not None and days_difference > 90:
            status = "Reconquista"
        if not status:
            ticket_query = (
                db.session.query(Ticket)
                .join(SubmittedOrder, Ticket.orderId == SubmittedOrder.order_id)
                .filter(
                    SubmittedOrder.profile_id == client_data.id_cliente,
                    Ticket.dateCreated >= first_day_current_month,
                    Ticket.dateCreated <= last_day_current_month,
                    Ticket.reason == 'Reconquista'
                )
                .first()
            )
            if ticket_query:
                status = 'Reconquista'

        combined_results.append({
            'cupom_vendedora': client_data.cupom_vendedora, 
            'id_cliente': client_data.id_cliente,
            'last_order': format_date_for_query(last_order),
            'min_data': format_date_for_query(min_data),
            'dias': days_difference,
            'last_order_mes_anterior': format_date_for_query(last_order_prev_month),
            'min_data_mes_anterior': format_date_for_query(min_data_prev_month),
            'dias_mes_anterior': days_mes_anterior,
            'reqconquista_mes_anterior': status,        
            'Status': status
        })

    return combined_results

@reconquest_bp.route('/reconquest', methods=['GET'], strict_slashes=False)
def reconquest():
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    cupom_vendedora = request.args.get('cupomvendedora')
    time_colaborador = request.args.get('time')

    orders = get_all_orders(start_date, end_date, cupom_vendedora, time_colaborador)
    return jsonify(orders)

    




def calculate_counts_by_cupom(orders):
    results = []
    
    for cupom_vendedora, order_list in orders.items():
        count_reconquista = sum(1 for order in order_list if order['Status'] == "Reconquista")
        count_repagar = sum(1 for order in order_list if order.get('reqconquista_mes_anterior') == "Repagar")
        
        results.append({
            'cupom_vendedora': cupom_vendedora,
            'Reconquista': count_reconquista,
            'Repagar': count_repagar
        })
    
    return results

@reconquest_bp.route('/reconquestGroup', methods=['GET'], strict_slashes=False)
def get_summary_summarys():
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    cupom_vendedora = request.args.get('cupomvendedora')
    time_colaborador = request.args.get('time')

    # Implementação da função para obter todos os pedidos com base nos parâmetros
    all_orders = get_all_orders(start_date, end_date, cupom_vendedora, time_colaborador)
    
    # Organizar os pedidos por `cupom_vendedora`
    orders_by_cupom = {}
    for order in all_orders:
        cupom = order['cupom_vendedora']
        if cupom not in orders_by_cupom:
            orders_by_cupom[cupom] = []
        orders_by_cupom[cupom].append(order)
    
    # Calcular as contagens para cada cupom
    response = calculate_counts_by_cupom(orders_by_cupom)

    return jsonify(response)