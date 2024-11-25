from datetime import datetime
from flask import Blueprint, request, jsonify, session
import pytz
from sqlalchemy import Numeric, and_, cast, func
from flask_jwt_extended import jwt_required

from models.colaborador import Colaborador
from models.meta import Meta
from models.premiacaoMeta import PremiacaoMeta
from models.ticket import Ticket
from models.vwcsEcomPedidosJp import VwcsEcomPedidosJp
from models.closing import Closing
from database import db

import time

closing_bp = Blueprint('closing_bp', __name__)



@closing_bp.route('/closing', methods=['GET'], strict_slashes=False)
# @jwt_required()
def get_closing():
    start_time = time.time()


    mes_ano = request.args.get('mes_ano')
    cupom_vendedora = request.args.get('cupomvendedora')
    time_colaborador = request.args.get('time')

    try:
        query = (
            db.session.query(
                Closing,
                Colaborador.time.label('colaborador_time'),  
                Colaborador.nome
            )
            .join(Colaborador, Colaborador.cupom == Closing.cupom_vendedora)
        )
        
        
        if cupom_vendedora:
            query = query.filter(Closing.cupom_vendedora == cupom_vendedora)
        
        if time_colaborador:
            query = query.filter(Colaborador.time == time_colaborador)
        
        if mes_ano:
            query = query.filter(Closing.mes_ano == mes_ano)
        
        results = query.all()

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    formatted_results = []
    for closing, colaborador_time, nome in results:
        closing_dict = closing.to_dict()
        closing_dict['time'] = colaborador_time 
        closing_dict['nome'] = nome
        formatted_results.append(closing_dict)

    elapsed_time = time.time() - start_time
    print(f"Tempo de execução: {elapsed_time:.4f} segundos")

    return jsonify(formatted_results) if formatted_results else jsonify([])




@closing_bp.route('/closingGroup', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_closing_grouped():
    start_time = time.time()
    time_param = request.args.get('time')
    try:
        query = db.session.query(
            Closing.mes,
            Closing.ano,
            Closing.mes_ano,
            Colaborador.time,
            Closing.dt_insert,
            func.sum(Closing.total_pago).label('total_pago'),
            func.sum(Closing.total_frete).label('total_frete'),
            func.sum(Closing.total_comissional).label('total_comissional'),
            func.sum(Closing.valor_comissao).label('valor_comissao'),
            func.sum(Closing.total_receber).label('total_receber'),
        ).join(Colaborador, Colaborador.cupom == Closing.cupom_vendedora)

       
        if time_param:
            query = query.filter(Colaborador.time == time_param)

        closings_grouped = query.group_by(
            Closing.mes,
            Closing.ano,
            Closing.mes_ano,
            Colaborador.time,
            Closing.dt_insert
        ).all()
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

   
    results = [
        {
            'mes': closing.mes,
            'ano': closing.ano,
            'mes_ano': closing.mes_ano,
            'time': closing.time,
            'dt_insert': closing.dt_insert,
            'total_pago': closing.total_pago,
            'total_frete': closing.total_frete,
            'total_comissional': closing.total_comissional,
            'valor_comissao': closing.valor_comissao,
            'total_receber': closing.total_receber
        }
        for closing in closings_grouped
    ]

    elapsed_time = time.time() - start_time
    print(f"Tempo de execução: {elapsed_time:.4f} segundos")

    
    return jsonify(results) if results else jsonify([])

local_tz = pytz.timezone('America/Sao_Paulo')

def ajustar_para_fuso_horario_local(data_utc):
    """
    Converte a data do UTC para o fuso horário de São Paulo.
    """
    if data_utc is None:
        return None

    return data_utc.astimezone(local_tz)



@closing_bp.route('/closingOrder', methods=['GET'], strict_slashes=False)
# @jwt_required()
def get_orders():
    start_time = time.time()
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


    if start_date_str:
        try:
            
            start_date_local = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=local_tz)
            start_date_utc = start_date_local.astimezone(pytz.utc)
            approved_orders_query = approved_orders_query.filter(VwcsEcomPedidosJp.data_submissao >= start_date_utc)
        except ValueError as e:
            return jsonify({'error': f'Formato de startDate inválido. Use YYYY-MM-DD. Detalhes: {e}'}), 400

    if end_date_str:
        try:
           
            end_date_local = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=local_tz)
            end_date_utc = end_date_local.astimezone(pytz.utc)
            approved_orders_query = approved_orders_query.filter(VwcsEcomPedidosJp.data_submissao <= end_date_utc)
        except ValueError as e:
            return jsonify({'error': f'Formato de endDate inválido. Use YYYY-MM-DD. Detalhes: {e}'}), 400

    if cupom_vendedora:
        approved_orders_query = approved_orders_query.filter(VwcsEcomPedidosJp.cupom_vendedora.ilike(f'%{cupom_vendedora}%'))
    elif time_colaborador:
        colaboradores = Colaborador.query.filter_by(time=time_colaborador).all()
        cupoms = [colaborador.cupom for colaborador in colaboradores]
        if cupoms:
            approved_orders_query = approved_orders_query.filter(VwcsEcomPedidosJp.cupom_vendedora.in_(cupoms))
        else:
            return jsonify([])
   
   
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
   
    
    if start_date_str:
            try:
                start_date_local = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=local_tz)
                start_date_utc = start_date_local.astimezone(pytz.utc)
                non_approved_orders_query = non_approved_orders_query.filter(VwcsEcomPedidosJp.data_submissao >= start_date_utc)
            except ValueError as e:
                return jsonify({'error': f'Formato de startDate inválido. Use YYYY-MM-DD. Detalhes: {e}'}), 400

    if end_date_str:
            try:
                end_date_local = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=local_tz)
                end_date_utc = end_date_local.astimezone(pytz.utc)
                non_approved_orders_query = non_approved_orders_query.filter(VwcsEcomPedidosJp.data_submissao <= end_date_utc)
            except ValueError as e:
                return jsonify({'error': f'Formato de endDate inválido. Use YYYY-MM-DD. Detalhes: {e}'}), 400

    if cupom_vendedora:
        non_approved_orders_query = non_approved_orders_query.filter(VwcsEcomPedidosJp.cupom_vendedora.ilike(f'%{cupom_vendedora}%'))
    elif time_colaborador:
            colaboradores = Colaborador.query.filter_by(time=time_colaborador).all()
            cupoms = [colaborador.cupom for colaborador in colaboradores]
            if cupoms:
                non_approved_orders_query = non_approved_orders_query.filter(VwcsEcomPedidosJp.cupom_vendedora.in_(cupoms))
            else:
                return jsonify([])
    
    ped = db.session.query(
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
        VwcsEcomPedidosJp.pedido == 'o54607571'
    ).distinct()
   

    query = approved_orders_query.union_all(non_approved_orders_query).union_all(ped)






    try:
        grouped_data = (
            query.with_entities(
                VwcsEcomPedidosJp.cupom_vendedora,
                Colaborador.nome,
                Colaborador.funcao,
                func.concat(VwcsEcomPedidosJp.cupom_vendedora, '-', Colaborador.nome).label('id'),
                func.min(VwcsEcomPedidosJp.data_submissao).label('min_date'),
                func.sum(cast(func.replace(VwcsEcomPedidosJp.valor_pago, ',', '.'), Numeric)).label('total_valor_pago'),
                func.sum(cast(func.replace(VwcsEcomPedidosJp.valor_frete, ',', '.'), Numeric)).label('total_valor_frete')
            )
            .group_by(
                VwcsEcomPedidosJp.cupom_vendedora,
                Colaborador.nome,Colaborador.funcao,
            )
        ).all()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    results = []
    gerentes_processados = set() 
    
    for data in grouped_data:
        total_comissao = (
            (float(data.total_valor_pago) if data.total_valor_pago is not None else 0.0) -
            (float(data.total_valor_frete) if data.total_valor_frete is not None else 0.0)
        )

        mes = data.min_date.month if data.min_date else 0
        ano = data.min_date.year if data.min_date else 0
        mes_formatado = f"{mes:02d}"
        mes_ano = f"{mes_formatado}-{ano}"

        selected_meta = 'Não tem meta cadastrada'
        porcentagem = 0
        valor_meta = 0
        premiacao_meta = 0 

        metas = (
            db.session.query(Meta)
            .filter(
                func.concat(Meta.cupom, '-', Meta.nome) == data.id,
                Meta.mes_ano == mes_ano
            )
            .order_by(Meta.valor.desc())
            .all()
        )

        for meta in metas:
            if total_comissao >= meta.valor:
                selected_meta = meta.meta
                porcentagem = meta.porcentagem
                valor_meta = meta.valor
                break

        colaborador = db.session.query(Colaborador).filter(
            func.concat(Colaborador.cupom, '-', Colaborador.nome) == data.id,
        ).first()

        if colaborador:
            premiacao = db.session.query(PremiacaoMeta).filter(
                PremiacaoMeta.descricao == selected_meta,
                PremiacaoMeta.time == colaborador.time
            ).first()
            
            if premiacao:
                premiacao_meta = premiacao.valor
            else:
                premiacao_meta = 0
        
        results.append({
            'cupom_vendedora': data.cupom_vendedora,
            'nome': data.nome,
            'funcao':data.funcao,
            'mes': mes,
            'ano': ano,
            'total_valor_pago': float(data.total_valor_pago) if data.total_valor_pago is not None else 0.0,
            'total_valor_frete': float(data.total_valor_frete) if data.total_valor_frete is not None else 0.0,
            'total_comissional': total_comissao,
            'meta': selected_meta,
            'porcentagem': porcentagem,
            'premiacao_meta': premiacao_meta,
            'Valor_comisao': total_comissao * porcentagem
        })

        
       

    elapsed_time = time.time() - start_time
    print(f"Tempo de execução: {elapsed_time:.4f} segundos")

    return jsonify(results)

















@closing_bp.route('/closing', methods=['POST'])
@jwt_required()
def create_colaborador():
    data_list = request.get_json()
    
    if not isinstance(data_list, list):
        return jsonify({'error': 'O formato dos dados está incorreto. Espera-se uma lista de objetos.'}), 400

    try:
        for data in data_list:
            if not isinstance(data, dict):
                return jsonify({'error': 'Os itens da lista devem ser dicionários.'}), 400
            
            print(f"Dados recebidos: {data}")

            mes = data.get('mes')
            ano = data.get('ano')
            mes_ano = data.get('mes_ano')
            cupom_vendedora = data.get('cupom_vendedora')
            funcao = data.get('funcao')
            total_pago = data.get('total_pago')
            total_frete = data.get('total_frete')
            total_comissional = data.get('total_comissional')
            meta_atingida = data.get('meta_atingida')
            porcentagem_meta = data.get('porcentagem_meta')
            valor_comissao = data.get('valor_comissao')
            premiacao_meta = data.get('premiacao_meta')
            qtd_reconquista = data.get('qtd_reconquista')
            vlr_reconquista = data.get('vlr_reconquista')
            vlr_total_reco = data.get('vlr_total_reco')
            qtd_repagar = data.get('qtd_repagar')
            vlr_recon_mes_ant = data.get('vlr_recon_mes_ant')
            vlr_total_recon_mes_ant = data.get('vlr_total_recon_mes_ant')
            premiacao_reconquista = data.get('premiacao_reconquista')
            total_receber = data.get('total_receber')
            vlr_taxa_conversao= data.get('vlr_taxa_conversao')
            
            print(f"Mes: {mes}, Ano: {ano}")

            if isinstance(mes, int):
                mes = str(mes)
            if isinstance(ano, int):
                ano = str(ano)
            print(f"Mes convertido: {mes}, Ano convertido: {ano}")

           
            existing_closing = Closing.query.filter(
                (Closing.cupom_vendedora == cupom_vendedora) &
                (Closing.mes == mes) &
                (Closing.ano == ano)
            ).all()


            print(f"Registros existentes: {existing_closing}")

            if existing_closing:
                existing_info = [
                    {
                        'cupom_vendedora': record.cupom_vendedora,
                        'mes': record.mes,
                        'ano': record.ano
                    } for record in existing_closing
                ]
                return jsonify({
                    'error': 'Cupom ou nome já existe',
                    'existing_records': existing_info
                }), 409

            new_closing = Closing(
                mes=mes, ano=ano, mes_ano=mes_ano, cupom_vendedora=cupom_vendedora,funcao=funcao, total_pago=total_pago,
                total_frete=total_frete, total_comissional=total_comissional, meta_atingida=meta_atingida,
                porcentagem_meta=porcentagem_meta, valor_comissao=valor_comissao, premiacao_meta=premiacao_meta,
                qtd_reconquista=qtd_reconquista, vlr_reconquista=vlr_reconquista, vlr_total_reco=vlr_total_reco,
                qtd_repagar=qtd_repagar, vlr_recon_mes_ant=vlr_recon_mes_ant, vlr_total_recon_mes_ant=vlr_total_recon_mes_ant,
                premiacao_reconquista=premiacao_reconquista, total_receber=total_receber,vlr_taxa_conversao=vlr_taxa_conversao
            )
            
            print(f"Novo registro: {new_closing}")

            db.session.add(new_closing)

        db.session.commit()
        return jsonify({'message': 'Closings criados com sucesso'}), 201
    except Exception as e:
        print(f"Erro ao criar closing: {e}")
        return jsonify({'error': 'Erro ao criar closing'}), 500