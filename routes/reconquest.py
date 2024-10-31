from flask import Blueprint, jsonify, request
from sqlalchemy.dialects import postgresql
import pytz
from sqlalchemy import func, and_
# from models import Colaborador, SubmittedOrder, Ticket, db, VwcsEcomPedidosJp
from flask_jwt_extended import jwt_required
from models.colaborador import Colaborador

from models.submittedOrder import SubmittedOrder
from models.ticket import Ticket

from models.vwcsEcomPedidosJp import VwcsEcomPedidosJp
from database import db


from datetime import datetime, timedelta
from sqlalchemy.orm import aliased

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
    first_day_current_month = date.replace(day=1).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=local_tz)
    last_day_current_month = (first_day_current_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    last_day_current_month = last_day_current_month.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=local_tz)
    return first_day_current_month.astimezone(pytz.utc), last_day_current_month.astimezone(pytz.utc)

def get_previous_month_range(date):
    """Get the first and last day of the previous month for the given date."""
    first_day_current_month, _ = get_current_month_range(date)
    first_day_prev_month = first_day_current_month - timedelta(days=1)
    first_day_prev_month = first_day_prev_month.replace(day=1).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=local_tz)
    last_day_prev_month = (first_day_prev_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    last_day_prev_month = last_day_prev_month.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=local_tz)
    return first_day_prev_month.astimezone(pytz.utc), last_day_prev_month.astimezone(pytz.utc)

def adjust_for_timezone(date_input):
    sao_paulo_tz = pytz.timezone('America/Sao_Paulo')

    # Verifica se a entrada é uma string e a converte para datetime
    if isinstance(date_input, str):
        date_time_utc = datetime.strptime(date_input, '%Y-%m-%d %H:%M:%S')
        date_time_utc = date_time_utc.replace(tzinfo=pytz.utc)  # Define como UTC
    elif isinstance(date_input, datetime):
        date_time_utc = date_input
    else:
        return None

    # Ajusta para o fuso horário de São Paulo
    date_time_sao_paulo = date_time_utc.astimezone(sao_paulo_tz)
    return date_time_sao_paulo

def get_all_orders(start_date=None, end_date=None, cupom_vendedora=None, time_colaborador=None):
    """Retrieve orders based on filters and calculate metrics."""
    local_tz = pytz.timezone('America/Sao_Paulo')
    formatted_start_date = format_date_for_query(parse_date(start_date)) if start_date else None
    formatted_end_date = format_date_for_query(parse_date(end_date)) if end_date else None
    colaborador_alias = aliased(Colaborador)
    # Convert start and end dates to UTC
    if formatted_start_date:
        start_date_local = datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=local_tz)
        formatted_start_date = start_date_local.astimezone(pytz.utc).strftime('%Y-%m-%d')
    if formatted_end_date:
        end_date_local = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=local_tz)
        formatted_end_date = end_date_local.astimezone(pytz.utc).strftime('%Y-%m-%d')

    filters_aproved = [VwcsEcomPedidosJp.status == 'APROVADO'    ]
    if formatted_start_date:
        filters_aproved.append(VwcsEcomPedidosJp.data_submissao >= formatted_start_date)
    if formatted_end_date:
        filters_aproved.append(VwcsEcomPedidosJp.data_submissao <= formatted_end_date)
    if time_colaborador:
        filters_aproved.append(colaborador_alias.time == time_colaborador)
    elif cupom_vendedora:
        filters_aproved.append(colaborador_alias.cupom == cupom_vendedora)
    
    subquery_exclude_tickets_cancelled = (
    db.session.query(Ticket.orderId)
    .filter(
        (Ticket.reason == 'Status para Cancelado') ,(Ticket.status == 'Autorizado')
    )
    .subquery()
    )
    filters_aproved.append(~VwcsEcomPedidosJp.pedido.in_(subquery_exclude_tickets_cancelled))

   
    filters_reaproved= [VwcsEcomPedidosJp.status != 'APROVADO'   ]
    if formatted_start_date:
        filters_reaproved.append(VwcsEcomPedidosJp.data_submissao >= formatted_start_date)
    if formatted_end_date:
        filters_reaproved.append(VwcsEcomPedidosJp.data_submissao <= formatted_end_date)
    if time_colaborador:
        filters_reaproved.append(colaborador_alias.time == time_colaborador)
    elif cupom_vendedora:
        filters_reaproved.append(colaborador_alias.cupom == cupom_vendedora)
    subquery_include_tickets_approved = (
        db.session.query(Ticket.orderId)
        .filter(
            (Ticket.reason == 'Status para Aprovado') , (Ticket.status == 'Autorizado')
        )
        .subquery()
    )
    filters_reaproved.append(VwcsEcomPedidosJp.pedido.in_(subquery_include_tickets_approved))

    min_data_query_aproved = (
        db.session.query(
            VwcsEcomPedidosJp.cupom_vendedora.label('cupom_vendedora'),
            VwcsEcomPedidosJp.id_cliente.label('id_cliente'),
            func.min(VwcsEcomPedidosJp.data_submissao).label('min_data'),
            colaborador_alias.nome.label('nome')
        )
         .join(
        colaborador_alias, 
        and_(
            colaborador_alias.cupom == VwcsEcomPedidosJp.cupom_vendedora,
            VwcsEcomPedidosJp.data_submissao >= colaborador_alias.dtadmissao,
            VwcsEcomPedidosJp.data_submissao <= colaborador_alias.dtdemissao
        )
    )
        .filter(and_(*filters_aproved))  
        .distinct(VwcsEcomPedidosJp.id_cliente)
        .group_by(VwcsEcomPedidosJp.cupom_vendedora, colaborador_alias.nome, VwcsEcomPedidosJp.id_cliente)
    )

    min_data_query_reaproved = (
        db.session.query(
            VwcsEcomPedidosJp.cupom_vendedora.label('cupom_vendedora'),
            VwcsEcomPedidosJp.id_cliente.label('id_cliente'),
            func.min(VwcsEcomPedidosJp.data_submissao).label('min_data'),
            colaborador_alias.nome.label('nome')
        )
          .join(
        colaborador_alias, 
        and_(
            colaborador_alias.cupom == VwcsEcomPedidosJp.cupom_vendedora,
            VwcsEcomPedidosJp.data_submissao >= colaborador_alias.dtadmissao,
            VwcsEcomPedidosJp.data_submissao <= colaborador_alias.dtdemissao
        )
    )
        .filter(and_(*filters_aproved))  
        .distinct(VwcsEcomPedidosJp.id_cliente)
        .group_by(VwcsEcomPedidosJp.cupom_vendedora, colaborador_alias.nome, VwcsEcomPedidosJp.id_cliente)
    )

    min_data_query = min_data_query_aproved.union_all(min_data_query_reaproved).subquery()

    subquery_aproved = (
        db.session.query(
            VwcsEcomPedidosJp.id_cliente.label('id_cliente'),
            func.max(VwcsEcomPedidosJp.data_submissao).label('last_order')
        )
        .join(min_data_query, VwcsEcomPedidosJp.id_cliente == min_data_query.c.id_cliente)
        .filter(
            and_(
                VwcsEcomPedidosJp.data_submissao < min_data_query.c.min_data,
                VwcsEcomPedidosJp.data_submissao.isnot(None),
                VwcsEcomPedidosJp.status == 'APROVADO',
                ~VwcsEcomPedidosJp.pedido.in_(subquery_exclude_tickets_cancelled)
            )
        )
        .group_by(VwcsEcomPedidosJp.id_cliente)
    )

    # Executar a subconsulta e imprimir os resultados
    # approved_results = subquery_aproved.all()
    # print("Resultados da subconsulta aprovada:")
    # for result in approved_results:
    #     print(f"ID Cliente: {result.id_cliente}, Último Pedido: {result.last_order}")

    # Subconsulta para pedidos não aprovados
    subquery_reaproved = (
        db.session.query(
            VwcsEcomPedidosJp.id_cliente.label('id_cliente'),
            func.max(VwcsEcomPedidosJp.data_submissao).label('last_order')
        )
        .join(min_data_query, VwcsEcomPedidosJp.id_cliente == min_data_query.c.id_cliente)
        .filter(
            and_(
                VwcsEcomPedidosJp.data_submissao < min_data_query.c.min_data,
                VwcsEcomPedidosJp.data_submissao.isnot(None),
                VwcsEcomPedidosJp.status != 'APROVADO',
                ~VwcsEcomPedidosJp.pedido.in_(subquery_include_tickets_approved)
            )
        )
        .group_by(VwcsEcomPedidosJp.id_cliente)
    )

# Executar a subconsulta e imprimir os resultados
    # reapproved_results = subquery_reaproved.all()
    # print("Resultados da subconsulta não aprovada:")
    # for result in reapproved_results:
    #     print(f"ID Cliente: {result.id_cliente}, Último Pedido: {result.last_order}")

    #     # União das duas subconsultas
    subquery = subquery_aproved.union_all(subquery_reaproved).subquery()

    # A consulta final pode incluir o join com outras tabelas ou agregações
    results = db.session.query(subquery).all()

   
    # print("Consulta SQL Gerada para subquery:")
    # print(str(subquery.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})))
    # print("Resultado da subquery:")
    # for row in db.session.query(subquery).all():
    #     print(row)
    
    today = datetime.now()
    first_day_current_month, last_day_current_month = get_current_month_range(today)
    orders_query = (
        db.session.query(
            min_data_query.c.cupom_vendedora.label('cupom_vendedora'),
            min_data_query.c.id_cliente,
            min_data_query.c.min_data,
            func.max(subquery.c.last_order).label('last_order'),
            min_data_query.c.nome
        )
        .outerjoin(subquery, min_data_query.c.id_cliente == subquery.c.id_cliente)
        .group_by(
            min_data_query.c.cupom_vendedora,
            min_data_query.c.id_cliente,
            min_data_query.c.min_data,  # Certifique-se de incluir todos os campos que não são agregados
            min_data_query.c.nome  # Adicionando 'nome' ao GROUP BY
        )
    )

    # Executar a consulta e imprimir os resultados
    # results = orders_query.all()
    # for result in results:
    #     print(result)


    orders_results = orders_query.all()
    # print("Resultado da orders_query:")
    # for result in orders_results:
    #     print(result)       
    combined_results = []
    for client_data in orders_results:
        min_data = client_data.min_data
        last_orders = client_data.last_order
        # print("Resultado da orders_query:")
        # for result in orders_results:
        #     print(result)       
        days_difference = None
        days_mes_anterior = None
    
        # print("minima data:",min_data_query)
        if min_data and last_orders:
            min_date = parse_date(format_date_for_query(adjust_for_timezone(min_data)))
            last_order_date = parse_date(format_date_for_query((adjust_for_timezone((last_orders)))))
            # print('min_date')
            # print(min_date)
            # print('last_order_date')
            # print(last_order_date)
            if min_date and last_order_date:
                days_difference = (min_date -last_order_date).days
               

        current_date = parse_date(format_date_for_query(adjust_for_timezone(min_data))) or datetime.now()
        first_day_prev_month, last_day_prev_month = get_previous_month_range(current_date)
        min_data_prev_month = None
        # print(first_day_current_month,last_day_prev_month)
        min_data_prev_month_aproved = (
            db.session.query(func.min(VwcsEcomPedidosJp.data_submissao))
            # .join(colaborador_alias, colaborador_alias.cupom == VwcsEcomPedidosJp.cupom_vendedora)
            .filter(
                VwcsEcomPedidosJp.id_cliente == client_data.id_cliente,
                VwcsEcomPedidosJp.data_submissao >= first_day_prev_month,
                VwcsEcomPedidosJp.data_submissao <= last_day_prev_month,
                VwcsEcomPedidosJp.cupom_vendedora == client_data.cupom_vendedora,
                VwcsEcomPedidosJp.status == 'APROVADO',
                ~VwcsEcomPedidosJp.pedido.in_(subquery_exclude_tickets_cancelled)  # Correção: operador ~ para negação
            )
            .group_by(VwcsEcomPedidosJp.id_cliente)
            .scalar()
        )

        min_data_prev_month_reaproved = (
            db.session.query(func.min(VwcsEcomPedidosJp.data_submissao))
            # .join(colaborador_alias, colaborador_alias.cupom == VwcsEcomPedidosJp.cupom_vendedora)
            .filter(
                VwcsEcomPedidosJp.id_cliente == client_data.id_cliente,
                VwcsEcomPedidosJp.data_submissao >= first_day_prev_month,
                VwcsEcomPedidosJp.data_submissao <= last_day_prev_month,
                VwcsEcomPedidosJp.cupom_vendedora == client_data.cupom_vendedora,
                VwcsEcomPedidosJp.status != 'APROVADO',
                VwcsEcomPedidosJp.pedido.in_(subquery_include_tickets_approved)  # Correção: condição de inclusão
            )
            .group_by(VwcsEcomPedidosJp.id_cliente)
            .scalar()
        )

        # União das duas consultas
        
        min_data_prev_month = min(
    filter(None, [min_data_prev_month_aproved, min_data_prev_month_reaproved]), 
    default=None
)
      

            
       
        
        last_order_prev_month = None
        if min_data_prev_month:
            last_order_prev_month_aproved = (
                db.session.query(func.max(VwcsEcomPedidosJp.data_submissao))
                .filter(
                    VwcsEcomPedidosJp.id_cliente == client_data.id_cliente,
                    VwcsEcomPedidosJp.data_submissao < min_data_prev_month,
                    VwcsEcomPedidosJp.status == 'APROVADO',
                    ~VwcsEcomPedidosJp.pedido.in_(subquery_exclude_tickets_cancelled)
                )
                .group_by(VwcsEcomPedidosJp.id_cliente)
                .scalar()
            )
            last_order_prev_month_reaproved = (
                db.session.query(func.max(VwcsEcomPedidosJp.data_submissao))
                .filter(
                    VwcsEcomPedidosJp.id_cliente == client_data.id_cliente,
                    VwcsEcomPedidosJp.data_submissao < min_data_prev_month,
                    VwcsEcomPedidosJp.status != 'APROVADO',
                    VwcsEcomPedidosJp.pedido.in_(subquery_include_tickets_approved)
                )
                .group_by(VwcsEcomPedidosJp.id_cliente)
                .scalar()
            )
            
            last_order_prev_month = max(
    filter(None, [last_order_prev_month_aproved, last_order_prev_month_reaproved]), 
    default=None
)
            
            
            # if last_order_prev_month_aproved is not None and last_order_prev_month_reaproved is not None:
            #     last_order_prev_month = max(last_order_prev_month_aproved, last_order_prev_month_reaproved)
            # elif last_order_prev_month_aproved is not None:
            #     last_order_prev_month = last_order_prev_month_aproved
            # elif last_order_prev_month_reaproved is not None:
            #     last_order_prev_month = last_order_prev_month_reaproved
            # else:
            #     last_order_prev_month = None
        # print("Resultado da last_order_prev_month:")
        # print("Resultado da last_order_prev_month:", last_order_prev_month)
        if min_data_prev_month and last_order_prev_month:
            min_data_prev_month_date = parse_date(format_date_for_query(min_data_prev_month))
            last_order_prev_month_date = parse_date(format_date_for_query(last_order_prev_month))
            if min_data_prev_month_date and last_order_prev_month_date:
                days_mes_anterior = (min_data_prev_month_date - last_order_prev_month_date).days

        status = ""
        if days_difference is not None and days_difference > 90:
            status = "Reconquista"
        elif not status and format_date_for_query(last_orders) is None :
            status = "Reconquista"  
        elif days_mes_anterior is not None and days_mes_anterior > 90:
            status = "Repagar"
          
        elif min_data_prev_month is not None and last_order_prev_month is  None and  format_date_for_query(last_orders) is not None:
            status = "Repagar"    
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
            'last_order': format_date_for_query(adjust_for_timezone((last_orders))),
            'min_data': (format_date_for_query(adjust_for_timezone(min_data))),
            'dias': days_difference,
            'last_order_mes_anterior': format_date_for_query(adjust_for_timezone((last_order_prev_month))),
            'min_data_mes_anterior': format_date_for_query(adjust_for_timezone(min_data_prev_month)),
            'dias_mes_anterior': days_mes_anterior,
            'reqconquista_mes_anterior': status,        
            'Status': status,
            'nome': client_data.nome
        })
        # print("Resultado da combined_results:")
        # print(combined_results)

    return combined_results

@reconquest_bp.route('/reconquest', methods=['GET'], strict_slashes=False)
# @jwt_required()
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
# @jwt_required()
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
        cupom_vendedora = order['cupom_vendedora']
        if cupom_vendedora not in orders_by_cupom:
            orders_by_cupom[cupom_vendedora] = []
        orders_by_cupom[cupom_vendedora].append(order)
    
    # Calcular as contagens para cada cupom
    response = calculate_counts_by_cupom(orders_by_cupom)

    return jsonify(response)