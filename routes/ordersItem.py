from collections import defaultdict
from flask import Blueprint, request, jsonify
from sqlalchemy import Numeric, String, func
from flask_jwt_extended import jwt_required
from models import modelo
from models.colaborador import Colaborador
from models.modelo import CategoriaGestor, ClasItem, ClassGestor, ClassModelo, Colecao, Cor, CorGestor, GrupoGestor, Lancamento, Linha, Modelo, Montagem, SubClassifGestor
from models.ticket import Ticket
from models.vwcsEcomItensPedidosJp import VwcsEcomItensPedidosJp
from models.vwcsEcomPedidosJp import VwcsEcomPedidosJp
from database import db
from datetime import datetime,date, time
import pytz

ordersItem_bp = Blueprint('ordersItem_bp', __name__)

def parse_currency(value):
    if value is None or value.strip() == '':
        return 0.0
    value = value.replace('R$', '').replace('.', '').replace(',', '.').strip()
    return float(value) if value else 0.0

def apply_date_filters(query, start_date_str, end_date_str, local_tz):
    if start_date_str:
        try:
            start_date_local = datetime.strptime(start_date_str, '%Y-%m-%d').replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=local_tz)
            start_date_utc = start_date_local.astimezone(pytz.utc)
            query = query.filter(VwcsEcomPedidosJp.data_submissao >= start_date_utc)
        except ValueError as e:
            raise ValueError(f'Formato de startDate inválido. Use YYYY-MM-DD. Detalhes: {e}')

    if end_date_str:
        try:
            end_date_local = datetime.strptime(end_date_str, '%Y-%m-%d').replace(
                hour=23, minute=59, second=59, microsecond=999999, tzinfo=local_tz)
            end_date_utc = end_date_local.astimezone(pytz.utc)
            query = query.filter(VwcsEcomPedidosJp.data_submissao <= end_date_utc)
        except ValueError as e:
            raise ValueError(f'Formato de endDate inválido. Use YYYY-MM-DD. Detalhes: {e}')

    return query


def get_ordersItem(start_date_str, end_date_str, cupom_vendedora, time_colaborador):
    
    print("Valores de entrada:", start_date_str, end_date_str, cupom_vendedora, time_colaborador)






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

    approved_orders_query = db.session.query(
    VwcsEcomPedidosJp.pedido,
    VwcsEcomPedidosJp.cupom_vendedora,
    VwcsEcomPedidosJp.data_submissao,
    VwcsEcomPedidosJp.envio,
    VwcsEcomPedidosJp.hora_submissao,
    VwcsEcomPedidosJp.id_cliente,
    VwcsEcomPedidosJp.idloja,
    VwcsEcomPedidosJp.metodo_pagamento,
    VwcsEcomPedidosJp.parcelas,
    VwcsEcomPedidosJp.site,
    VwcsEcomPedidosJp.status,
    VwcsEcomPedidosJp.total_itens,
    VwcsEcomPedidosJp.valor_bruto,
    VwcsEcomPedidosJp.valor_desconto,
    VwcsEcomPedidosJp.valor_frete,
    VwcsEcomPedidosJp.valor_pago,
    VwcsEcomItensPedidosJp.referencia.label("modelo"),
    VwcsEcomItensPedidosJp.tamanho,
    VwcsEcomItensPedidosJp.quantidade,
    VwcsEcomItensPedidosJp.valor_venda_unitario.label("valorVendaUnit"), 
    VwcsEcomItensPedidosJp.valor_desconto.label("valorDesc"),            
    VwcsEcomItensPedidosJp.valor_pago.label("valorPago"),                
    VwcsEcomItensPedidosJp.link,
    VwcsEcomItensPedidosJp.nome_site.label("nomeSite") 
).join(
    VwcsEcomItensPedidosJp, VwcsEcomPedidosJp.pedido == VwcsEcomItensPedidosJp.id_pedido
).filter(
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

    if cupom_vendedora:
        # Use `in_` with a list to ensure proper filtering
        approved_orders_query = approved_orders_query.filter(VwcsEcomPedidosJp.cupom_vendedora.ilike(f'%{cupom_vendedora}%'))
    elif time_colaborador:
        # Get all collaborators for the specified time
        colaboradores = Colaborador.query.filter_by(time=time_colaborador).all()
        # Collect their coupons into a list
        cupoms = [colaborador.cupom for colaborador in colaboradores]
        if cupoms:
            # Filter by the list of coupons
            approved_orders_query = approved_orders_query.filter(VwcsEcomPedidosJp.cupom_vendedora.in_(cupoms))
        else:
            # Return an empty response if no collaborators found
            return jsonify([])


   
    subquery_reaproved = db.session.query(VwcsEcomPedidosJp.pedido).join(
        Ticket, VwcsEcomPedidosJp.pedido == Ticket.orderId
    ).filter(
        Ticket.reason == 'Status para Aprovado',
        Ticket.status == 'Autorizado'
    ).subquery()
    
    non_approved_orders_query = db.session.query(
        VwcsEcomPedidosJp.pedido,
        VwcsEcomPedidosJp.cupom_vendedora,
        VwcsEcomPedidosJp.data_submissao,
        VwcsEcomPedidosJp.envio,
        VwcsEcomPedidosJp.hora_submissao,
        VwcsEcomPedidosJp.id_cliente,
        VwcsEcomPedidosJp.idloja,
        VwcsEcomPedidosJp.metodo_pagamento,
        VwcsEcomPedidosJp.parcelas,
        VwcsEcomPedidosJp.site,
        VwcsEcomPedidosJp.status,
        VwcsEcomPedidosJp.total_itens,
        VwcsEcomPedidosJp.valor_bruto,
        VwcsEcomPedidosJp.valor_desconto,
        VwcsEcomPedidosJp.valor_frete,
        VwcsEcomPedidosJp.valor_pago,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None 
    ).join(
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
        order_dict = {
            'pedido': order[0],
            'cupom_vendedora': order[1],
            'data_submissao': order[2].isoformat() if isinstance(order[2], (date, datetime)) else order[2],
            'envio': order[3],
            'hora_submissao': order[4].isoformat() if isinstance(order[4], time) else order[4],
            'id_cliente': order[5],
            'idloja': order[6],
            'metodo_pagamento': order[7],
            'parcelas': order[8],
            'site': order[9],
            'status': order[10],
            'total_itens': order[11],
            'valor_bruto': order[12],
            'valor_desconto': order[13],
            'valor_frete': order[14],
            'valor_pago': order[15],
            'modelo': order[16],
            'tamanho': order[17],
            'quantidade': order[18],
            'valorVendaUnit': order[19],
            'valorDesc': order[20],
            'valorPago': order[21],
            'link': order[22],
            'nomeSite': order[23]
        }

        # Converte valor_pago e valor_frete para float e calcula a diferença
        valor_pago = parse_currency(order_dict.get('valor_pago', ''))
        valor_frete = parse_currency(order_dict.get('valor_frete', ''))

        results.append(order_dict)

    return (results)
    
    
    
    
    
    
    
def get_ordersItemGroup(start_date_str, end_date_str, cupom_vendedora, time_colaborador):
    local_tz = pytz.timezone('America/Sao_Paulo')

    subquery_aproved = db.session.query(VwcsEcomPedidosJp.pedido).join(
        Ticket, VwcsEcomPedidosJp.pedido == Ticket.orderId
    ).filter(
        Ticket.reason == 'Status para Cancelado',
        Ticket.status == 'Autorizado'
    ).subquery()

    from sqlalchemy import func

    approved_orders_query = db.session.query(
        # VwcsEcomPedidosJp.pedido,
        VwcsEcomPedidosJp.cupom_vendedora,
        VwcsEcomItensPedidosJp.referencia.label("modelo"),
        VwcsEcomItensPedidosJp.tamanho,
        func.sum(VwcsEcomItensPedidosJp.quantidade).label("quantidade_total"),
       func.sum(func.cast(func.replace(VwcsEcomItensPedidosJp.valor_pago, ',', '.'), Numeric)).label("valor_pago")
    ).join(
        VwcsEcomItensPedidosJp, VwcsEcomPedidosJp.pedido == VwcsEcomItensPedidosJp.id_pedido
    ).filter(
        VwcsEcomPedidosJp.status == 'APROVADO',
        VwcsEcomPedidosJp.pedido.notin_(subquery_aproved)
    ).group_by(
        # VwcsEcomPedidosJp.pedido,
        VwcsEcomPedidosJp.cupom_vendedora,
        VwcsEcomItensPedidosJp.referencia,
        VwcsEcomItensPedidosJp.tamanho,
        # VwcsEcomItensPedidosJp.valor_venda_unitario
    )

    # Filtro por datas
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

    # Filtro por cupom_vendedora ou time_colaborador
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
        # VwcsEcomPedidosJp.pedido,
        VwcsEcomPedidosJp.cupom_vendedora,
        None,
        None,
        None,
        None,
    ).join(
        Ticket, VwcsEcomPedidosJp.pedido == Ticket.orderId
    ).filter(
        VwcsEcomPedidosJp.status != 'APROVADO',
        VwcsEcomPedidosJp.pedido.in_(subquery_reaproved)
    )

    # Filtro para pedidos não aprovados por datas
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

    # Filtro por cupom_vendedora ou time_colaborador para pedidos não aprovados
    if cupom_vendedora:
        non_approved_orders_query = non_approved_orders_query.filter(VwcsEcomPedidosJp.cupom_vendedora.ilike(f'%{cupom_vendedora}%'))
    elif time_colaborador:
        colaboradores = Colaborador.query.filter_by(time=time_colaborador).all()
        cupoms = [colaborador.cupom for colaborador in colaboradores]
        if cupoms:
            non_approved_orders_query = non_approved_orders_query.filter(VwcsEcomPedidosJp.cupom_vendedora.in_(cupoms))
        else:
            return jsonify([])

    # União das consultas
    union_query = approved_orders_query.union_all(non_approved_orders_query)

    try:
        orders = union_query.all()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    results = []
    for order in orders:
        order_dict = {
            # 'pedido': order[0],
            'cupom_vendedora': order[0],
            'modelo': order[1],
            'tamanho': order[2],
            'quantidade': order[3],
            'valorPago': order[4],
        }
        results.append(order_dict)

    return results

    
    
    
    
    
def get_modelos(modelos):
    if modelos:
        try:
            if isinstance(modelos, dict):
                modelo_param = list(modelos.values())  # Extrai os valores do dicionário
            elif isinstance(modelos, list):
                modelo_param = [str(m).strip() for m in modelos]
            else:
                modelo_param = [str(modelos).strip()]
            
            # Executa a consulta e armazena o resultado na variável `modelo`
            modelos_resultados  = db.session.query(
               
                func.trim(Modelo.PC13CODIGO).label('modelo'),
                func.trim(Modelo.PC13EMP08).label('empresa'),
                func.trim(Modelo.PC13COR).label('cor'),
                func.trim(Modelo.PC13CODCOL).label('cod_col'),
                func.trim(Modelo.PC13CODLAN).label('cod_lan'),                
                func.trim(Modelo.PC13CLAITE).label('codClassItem'),
                func.trim(Modelo.PC13CLAIPA).label('codClasItemPA'),
                func.trim(Modelo.PC13CODCTG).label('codCategoriaGestor'),
                func.trim(Modelo.PC13CODGMD).label('codGrupoGestor'),
                func.trim(Modelo.PC13CODCGE).label('codClasGestor'),
                func.trim(Modelo.PC13CODSCL).label('codSubClassifGestor'),
                func.trim(Modelo.PC13GESCOR).label('codCorGestor'),
                func.trim(Modelo.PC13CLASS).label('codClassDeModelo'),                
                func.trim(Modelo.PC13DESPLA).label('desc_plan'),
                func.trim(Modelo.PC13DESFAT).label('desc_fat'),                
                func.trim(Modelo.PC13GRADE).label('codGrade'),
                func.trim(Modelo.PC13FORMA).label('forma'),
                func.trim(Modelo.PC13NBM).label('NCM'),
                func.trim(Modelo.PC13LINHA).label('linha'),
                func.trim(Modelo.PC13PESBRU).label('pesoBruto'),
                func.trim(Modelo.PC13PESLIQ).label('pesoLiquido'),
                func.trim(Modelo.PC13ALTSAL).label('alturaSalto'),
                func.trim(Modelo.PC13COMMOD).label('comprimento'),
                func.trim(Modelo.PC13ALTMOD).label('altura'),
                func.trim(Modelo.PC13LARMOD).label('largura'),
                func.trim(Modelo.PC13VRUNIT).label('vrCusto'),
                func.trim(Modelo.PC13ALTSLN).label('alturaNovo'),
                func.trim(Modelo.PC13TIPMON).label('tipMontagem'),                
                func.trim(Cor.PC10DESCR).label('cor_descr'),
                func.trim(ClassModelo.PC04DESCR).label('class_descr'),
                func.trim(GrupoGestor.PCALDESCR).label('grupoGestor_desc'),
                func.trim(Colecao.PCAIDESC).label('colecao_desc'),
                func.trim(Lancamento.PCBMDESCR).label('lancamento_desc'),
                func.trim(CategoriaGestor.PCBJDESCR).label('catGestor_desc'),
                func.trim(CorGestor.PCDRDESCR).label('corGestor_desc'),
                func.trim(ClassGestor.PCBKDESCR).label('classGestor_desc'),
                func.trim(SubClassifGestor.PCBKDESSUB).label('subClassGestor_desc'),
                func.trim(Linha.PC03DESCR).label('linha_desc'),
                func.trim(ClasItem.PC16DESCR).label('ClasItemdesc'),
               
                func.trim(Montagem.PCDODESCRI).label('montagem_desc')
            ).outerjoin(
                Cor, Modelo.PC13COR == Cor.PC10CODIGO
            ).outerjoin(
                ClassModelo, Modelo.PC13CLASS == ClassModelo.PC04CODIGO
            ).outerjoin(
                GrupoGestor, 
                (Modelo.PC13EMP08 == GrupoGestor.PCALCODEMP) & 
                (Modelo.PC13CODGMD == GrupoGestor.PCALCODIGO)
            ).outerjoin(
                Colecao, 
                (Modelo.PC13EMP08 == Colecao.PCAICODEMP) & 
                (Modelo.PC13CODCOL == Colecao.PCAICODIGO)
            ).outerjoin(
                Lancamento, 
                (Modelo.PC13EMP08 == Lancamento.PCBMCODEMP) & 
                (Modelo.PC13CODLAN == Lancamento.PCBMCODIGO)
            ).outerjoin(
                CategoriaGestor, 
                (Modelo.PC13EMP08 == CategoriaGestor.PCBJCODEMP) & 
                (Modelo.PC13CODCTG == CategoriaGestor.PCBJCODIGO)
            ).outerjoin(
                CorGestor, 
                (Modelo.PC13GESCOR == CorGestor.PCDRCODIGO)
            ).outerjoin(
                ClassGestor, 
                (Modelo.PC13EMP08 == ClassGestor.PCBKCODEMP) & 
                (Modelo.PC13CODCGE == ClassGestor.PCBKCODIGO)
            ).outerjoin(
                SubClassifGestor, 
                (Modelo.PC13EMP08 == SubClassifGestor.PCBKCODEMP) & 
                (Modelo.PC13CODSCL == SubClassifGestor.PCBKSUBCLA)&
                (ClassGestor.PCBKCODIGO == SubClassifGestor.PCBKCODIGO)
            ).outerjoin(
                Linha, 
                (Modelo.PC13EMP08 == Linha.PC03CODEMP) & 
                (Modelo.PC13LINHA == Linha.PC03CODIGO)
            ).outerjoin(
                ClasItem, 
                (Modelo.PC13CLAITE == ClasItem.PC16CODIGO)
            ).outerjoin(
                Montagem, 
                (Modelo.PC13EMP08 == Montagem.PCDOCODEMP)&
                (Modelo.PC13TIPMON == Montagem.PCDOCODIGO)
            ).filter(
                Modelo.PC13EMP08 == 61,
                Modelo.PC13ANOPED==0,
                func.trim(Modelo.PC13CODIGO).in_(modelo_param)  # Modificado para buscar em lista
            ).all()
            # print("Tipo de modelos_resultados:", type(modelos_resultados))
            # print("Conteúdo de modelos_resultados:", modelos_resultados)
            # Verifica se `modelo` tem um resultado
            if modelos_resultados:
                categoria_mapping = {
                        2: ('CS', 'CALCADOS'),
                        3: ('RS', 'CALCADOS'),
                        4: ('CARMEN STEFFENS', 'MARKETING'),
                        5: ('RS', 'CARTEIRAS'),
                        6: ('CS', 'ACESSORIOS'),
                        8: ('BIJOUX', 'BIJOUX'),
                        9: ('RS', 'ACESSORIOS'),
                        10: ('CS', 'BOLSAS'),
                        11: ('CS', 'BOLSAS TEEN'),
                        12: ('CS', 'CALCADOS TEEN'),
                        13: ('CS', 'CARTEIRAS'),
                        14: ('CS', 'VESTUARIOS'),
                        15: ('RS', 'CALCADOS TEEN'),
                        16: ('RS', 'BOLSAS'),
                        17: ('CS', 'FITNESS'),
                        18: ('CS', 'MODA PRAIA'),
                        19: ('CS YOUNG', 'VESTUARIOS'),
                        20: ('CS CLUB', 'CALCADOS'),
                        21: ('CS CLUB', 'BOLSAS'),
                        22: ('CS CLUB', 'ACESSORIOS'),
                        23: ('CS CLUB', 'CARTEIRAS'),
                        24: ('CS YOUNG', 'CALCADOS'),
                        25: ('CS YOUNG', 'BOLSAS'),
                        26: ('CS YOUNG', 'ACESSORIOS'),
                        27: ('CS', 'LINGERIE'),
                        28: ('CS YOUNG', 'CARTEIRAS'),
                        29: ('RS', 'VESTUARIOS'),
                        30: ('CS CLUB', 'MARKETING'),
                        31: ('CS YOUNG', 'MARKETING'),
                        32: ('RAPHAEL STEFFENS', 'MARKETING'),
                        33: ('CS', 'RESORTS'),
                        34: ('CS CLUB', 'RESORTS'),
                        35: ('CS YOUNG', 'RESORTS'),
                        36: ('RS', 'RESORTS'),
                        37: ('CS', 'MEIA CALCA'),
                        111: ('TOP', 'TOP'),
                        250: ('NAO VENDAVEL', 'MARKETING'),
                        251: ('VENDAVEL', 'MARKETING'),
                        300: ('PROJETOS', 'PROJETOS')
                    }
                modelos_dict = {} 
                base_url = 'https://img.carmensteffens.com.br/_imgprodutos/800x800/'
                for modelo in modelos_resultados:
                    
                    modelo_dict = {
                    'modelo': modelo.modelo,
                    'empresa': modelo.empresa,
                    'cor': modelo.cor,
                    'cod_col': modelo.cod_col,
                    'cod_lan': modelo.cod_lan,
                    'codClassItem': modelo.codClassItem,
                    'codClasItemPA': modelo.codClasItemPA,
                    'codCategoriaGestor': modelo.codCategoriaGestor,
                    'codGrupoGestor': modelo.codGrupoGestor,
                    'codClasGestor': modelo.codClasGestor,
                    'codSubClassifGestor': modelo.codSubClassifGestor,
                    'codCorGestor': modelo.codCorGestor,
                    'codClassDeModelo': modelo.codClassDeModelo,
                    'desc_plan': modelo.desc_plan,
                    'desc_fat': modelo.desc_fat,
                    'codGrade': modelo.codGrade,
                    'forma': modelo.forma,
                    'NCM': modelo.NCM,
                    'linha': modelo.linha,
                    'pesoBruto': modelo.pesoBruto,
                    'pesoLiquido': modelo.pesoLiquido,
                    'alturaSalto': modelo.alturaSalto,
                    'comprimento': modelo.comprimento,
                    'altura': modelo.altura,
                    'largura': modelo.largura,
                    'vrCusto': modelo.vrCusto,
                    'alturaNovo': modelo.alturaNovo,
                    'tipMontagem': modelo.tipMontagem,
                    'cor_descr': modelo.cor_descr,  
                    'class_descr': modelo.class_descr,
                    'grupoGestor_desc':modelo.grupoGestor_desc ,
                    'colecao_desc':modelo.colecao_desc,
                    'lancamento_desc':modelo.lancamento_desc,
                    'catGestor_desc':modelo.catGestor_desc,
                    'corGestor_desc':modelo.corGestor_desc,
                    'classGestor_desc':modelo.classGestor_desc,
                    'subClassGestor_desc':modelo.subClassGestor_desc,
                    'linha_desc': modelo.linha_desc,
                    'ClasItemdesc': modelo.ClasItemdesc,
                    'montagem_desc': modelo.montagem_desc,
                    'path_foto': f"{base_url}{modelo.modelo}_1.jpg"
                        }
     # Exemplo de mapeamento
     
                    categoria_info = categoria_mapping.get(int(modelo.codCategoriaGestor))
                    # print(f"Tipo de codCategoriaGestor: {type(modelo.codCategoriaGestor)}")

                    if categoria_info:
                        modelo_dict['catGestor_desc'] = categoria_info[1]  # Nome da categoria
                        modelo_dict['marca'] = categoria_info[0]  # Subcategoria
                    else:
                        modelo_dict['catGestor_desc'] = 'Outros'  # Pode ser alterado conforme a necessidade
                        modelo_dict['marca'] = 'Outros'  # Pode ser alterado conforme a necessidade


                    modelos_dict[modelo.modelo] = modelo_dict
                        
                # Verifica se modelos_dict tem resultados
                if modelos_dict:
                    # print('modelos_dict:', modelos_dict)  
                    return modelos_dict  # Retorna o dicionário dos modelos encontrados
                else:
                    return {'message': 'Modelo não encontrado'}
        except Exception as e:
            return {'message': f'Erro ao buscar o modelo: {str(e)}'}
        else:
            return {'message': 'Parâmetro modelo não fornecido'}
        

from flask import jsonify, request
from itertools import islice

@ordersItem_bp.route('/ordersItem', methods=['GET'])
def get_orders():
    # Collect query parameters
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    cupom_vendedora = request.args.get('cupom_vendedora')
    time_colaborador = request.args.get('time')

    # Display received parameters
    print(f'Parâmetros recebidos: start_date={start_date}, end_date={end_date}, cupom_vendedora={cupom_vendedora}, time_colaborador={time_colaborador}')

    # Obtain orders based on the provided parameters
    results = get_ordersItem(start_date, end_date, cupom_vendedora, time_colaborador)

    if results and isinstance(results, list):
        # Extract all unique model codes
        modelos_codigos = list(set(order.get('modelo') for order in results if order.get('modelo')))
        print('modelos:', modelos_codigos)

        # Function to split the list into chunks of up to 1000
        def chunked_list(iterable, size):
            iterator = iter(iterable)
            for first in iterator:
                yield [first] + list(islice(iterator, size - 1))

        detalhes_modelos = {}
        for chunk in chunked_list(modelos_codigos, 1000):
            # For each chunk, call get_modelos and update the dictionary with details
            detalhes_modelos.update(get_modelos(chunk))

        print('Detalhes dos modelos obtidos:', detalhes_modelos)

        # Associate model details with each order
        for order in results:
            modelo_codigo = order.get('modelo')
            if modelo_codigo:
                modelo_detalhes = detalhes_modelos.get(modelo_codigo)
                if modelo_detalhes:
                    order.update(modelo_detalhes)
                else:
                    order['message'] = 'Modelo não encontrado'

    # Return the list of orders with their respective model details
    return jsonify(results), 200


















@ordersItem_bp.route('/modelo', methods=['GET'], strict_slashes=False)
def get_modelo():
    modelo_param = request.args.get('modelo')
   

    try:
        if modelo_param:
            # Executa a consulta e armazena o resultado na variável `modelo`
            modelo = db.session.query(
                func.trim(Modelo.PC13CODIGO).label('modelo'),
                func.trim(Modelo.PC13EMP08).label('empresa'),
                func.trim(Modelo.PC13COR).label('cor'),
                func.trim(Modelo.PC13CODCOL).label('cod_col'),
                func.trim(Modelo.PC13CODLAN).label('cod_lan'),                
                func.trim(Modelo.PC13CLAITE).label('codClassItem'),
                func.trim(Modelo.PC13CLAIPA).label('codClasItemPA'),
                func.trim(Modelo.PC13CODCTG).label('codCategoriaGestor'),
                func.trim(Modelo.PC13CODGMD).label('codGrupoGestor'),
                func.trim(Modelo.PC13CODCGE).label('codClasGestor'),
                func.trim(Modelo.PC13CODSCL).label('codSubClassifGestor'),
                func.trim(Modelo.PC13GESCOR).label('codCorGestor'),
                func.trim(Modelo.PC13CLASS).label('codClassDeModelo'),                
                func.trim(Modelo.PC13DESPLA).label('desc_plan'),
                func.trim(Modelo.PC13DESFAT).label('desc_fat'),                
                func.trim(Modelo.PC13GRADE).label('codGrade'),
                func.trim(Modelo.PC13FORMA).label('forma'),
                func.trim(Modelo.PC13NBM).label('NCM'),
                func.trim(Modelo.PC13LINHA).label('linha'),
                func.trim(Modelo.PC13PESBRU).label('pesoBruto'),
                func.trim(Modelo.PC13PESLIQ).label('pesoLiquido'),
                func.trim(Modelo.PC13ALTSAL).label('alturaSalto'),
                func.trim(Modelo.PC13COMMOD).label('comprimento'),
                func.trim(Modelo.PC13ALTMOD).label('altura'),
                func.trim(Modelo.PC13LARMOD).label('largura'),
                func.trim(Modelo.PC13VRUNIT).label('vrCusto'),
                func.trim(Modelo.PC13ALTSLN).label('alturaNovo'),
                func.trim(Modelo.PC13TIPMON).label('tipMontagem'),                
                func.trim(Cor.PC10DESCR).label('cor_descr'),
                func.trim(ClassModelo.PC04DESCR).label('class_descr'),
                func.trim(GrupoGestor.PCALDESCR).label('grupoGestor_desc'),
                func.trim(Colecao.PCAIDESC).label('colecao_desc'),
                func.trim(Lancamento.PCBMDESCR).label('lancamento_desc'),
                func.trim(CategoriaGestor.PCBJDESCR).label('catGestor_desc'),
                func.trim(CorGestor.PCDRDESCR).label('corGestor_desc'),
                func.trim(ClassGestor.PCBKDESCR).label('classGestor_desc'),
                func.trim(SubClassifGestor.PCBKDESSUB).label('subClassGestor_desc'),
                func.trim(Linha.PC03DESCR).label('linha_desc'),
                func.trim(ClasItem.PC16DESCR).label('ClasItemdesc'),
                func.trim(Montagem.PCDODESCRI).label('montagem_desc'),
            ).outerjoin(
                Cor, Modelo.PC13COR == Cor.PC10CODIGO
            ).outerjoin(
                ClassModelo, Modelo.PC13CLASS == ClassModelo.PC04CODIGO
            ).outerjoin(
                GrupoGestor, 
                (Modelo.PC13EMP08 == GrupoGestor.PCALCODEMP) & 
                (Modelo.PC13CODGMD == GrupoGestor.PCALCODIGO)
            ).outerjoin(
                Colecao, 
                (Modelo.PC13EMP08 == Colecao.PCAICODEMP) & 
                (Modelo.PC13CODCOL == Colecao.PCAICODIGO)
            ).outerjoin(
                Lancamento, 
                (Modelo.PC13EMP08 == Lancamento.PCBMCODEMP) & 
                (Modelo.PC13CODLAN == Lancamento.PCBMCODIGO)
            ).outerjoin(
                CategoriaGestor, 
                (Modelo.PC13EMP08 == CategoriaGestor.PCBJCODEMP) & 
                (Modelo.PC13CODCTG == CategoriaGestor.PCBJCODIGO)
            ).outerjoin(
                CorGestor, 
                (Modelo.PC13GESCOR == CorGestor.PCDRCODIGO)
            ).outerjoin(
                ClassGestor, 
                (Modelo.PC13EMP08 == ClassGestor.PCBKCODEMP) & 
                (Modelo.PC13CODCGE == ClassGestor.PCBKCODIGO)
            ).outerjoin(
                SubClassifGestor, 
                (Modelo.PC13EMP08 == SubClassifGestor.PCBKCODEMP) & 
                (Modelo.PC13CODSCL == SubClassifGestor.PCBKSUBCLA)&
                (ClassGestor.PCBKCODIGO == SubClassifGestor.PCBKCODIGO)
            ).outerjoin(
                Linha, 
                (Modelo.PC13EMP08 == Linha.PC03CODEMP) & 
                (Modelo.PC13LINHA == Linha.PC03CODIGO)
            ).outerjoin(
                ClasItem, 
                (Modelo.PC13CLAITE == ClasItem.PC16CODIGO)
            ).outerjoin(
                Montagem, 
                (Modelo.PC13EMP08 == Montagem.PCDOCODEMP)&
                (Modelo.PC13TIPMON == Montagem.PCDOCODIGO)
            ).filter(
                Modelo.PC13EMP08 == 61,
                func.trim(Modelo.PC13CODIGO) == modelo_param.strip()
            ).first()

            # Verifica se `modelo` tem um resultado
            if modelo:
                # Converte a tupla em um dicionário manualmente
                modelo_dict = {
                    'modelo': modelo.modelo,
                    'empresa': modelo.empresa,
                    'cor': modelo.cor,
                    'cod_col': modelo.cod_col,
                    'cod_lan': modelo.cod_lan,
                    'codClassItem': modelo.codClassItem,
                    'codClasItemPA': modelo.codClasItemPA,
                    'codCategoriaGestor': modelo.codCategoriaGestor,
                    'codGrupoGestor': modelo.codGrupoGestor,
                    'codClasGestor': modelo.codClasGestor,
                    'codSubClassifGestor': modelo.codSubClassifGestor,
                    'codCorGestor': modelo.codCorGestor,
                    'codClassDeModelo': modelo.codClassDeModelo,
                    'desc_plan': modelo.desc_plan,
                    'desc_fat': modelo.desc_fat,
                    'codGrade': modelo.codGrade,
                    'forma': modelo.forma,
                    'NCM': modelo.NCM,
                    'linha': modelo.linha,
                    'pesoBruto': modelo.pesoBruto,
                    'pesoLiquido': modelo.pesoLiquido,
                    'alturaSalto': modelo.alturaSalto,
                    'comprimento': modelo.comprimento,
                    'altura': modelo.altura,
                    'largura': modelo.largura,
                    'vrCusto': modelo.vrCusto,
                    'alturaNovo': modelo.alturaNovo,
                    'tipMontagem': modelo.tipMontagem,
                    'cor_descr': modelo.cor_descr,  
                    'class_descr': modelo.class_descr,
                    'grupoGestor_desc':modelo.grupoGestor_desc ,
                    'colecao_desc':modelo.colecao_desc,
                    'lancamento_desc':modelo.lancamento_desc,
                    'catGestor_desc':modelo.catGestor_desc,
                    'corGestor_desc':modelo.corGestor_desc,
                    'classGestor_desc':modelo.classGestor_desc,
                    'subClassGestor_desc':modelo.subClassGestor_desc,
                    'linha_desc': modelo.linha_desc,
                    'ClasItemdesc': modelo.ClasItemdesc,
                    'montagem_desc': modelo.montagem_desc,
                        }
                return jsonify(modelo_dict), 200
            else:
                return jsonify({'message': 'Modelo não encontrado'}), 404
        else:
            # Busca todos os modelos se `modelo_param` não foi fornecido
            modelos = db.session.query(Modelo).all()
            modelos_list = [modelo.to_dict() for modelo in modelos]
            return jsonify(modelos_list), 200
    except Exception as e:
        # Log para o erro e retorno de uma mensagem de erro genérica
      
        return jsonify({'message': 'Erro interno no servidor'}), 500



@ordersItem_bp.route('/ordersItemGroup', methods=['GET'])
def get_orders2():
    # Collect query parameters
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    cupom_vendedora = request.args.get('cupom_vendedora')
    time_colaborador = request.args.get('time')

    # Display received parameters
    # print(f'Parâmetros recebidos: start_date={start_date}, end_date={end_date}, cupom_vendedora={cupom_vendedora}, time_colaborador={time_colaborador}')

    # Obtain orders based on the provided parameters
    results = get_ordersItemGroup(start_date, end_date, cupom_vendedora, time_colaborador)

    if results and isinstance(results, list):
        # Extract all unique model codes
        modelos_codigos = list(set(order.get('modelo') for order in results if order.get('modelo')))
        # print('modelos:', modelos_codigos)

        # Function to split the list into chunks of up to 1000
        def chunked_list(iterable, size):
            iterator = iter(iterable)
            for first in iterator:
                yield [first] + list(islice(iterator, size - 1))

        detalhes_modelos = {}
        for chunk in chunked_list(modelos_codigos, 1000):
            # For each chunk, call get_modelos and update the dictionary with details
            detalhes_modelos.update(get_modelos(chunk))

        # print('Detalhes dos modelos obtidos:', detalhes_modelos)

        # Associate model details with each order
        for order in results:
            modelo_codigo = order.get('modelo')
            if modelo_codigo:
                modelo_detalhes = detalhes_modelos.get(modelo_codigo)
                if modelo_detalhes:
                    order.update(modelo_detalhes)
                else:
                    order['message'] = 'Modelo não encontrado'

    # Return the list of orders with their respective model details
    return jsonify(results), 200

