from datetime import datetime
from flask import Blueprint, request, jsonify, session
import pytz
from sqlalchemy import Numeric, cast, func
from models import Colaborador, Meta, PremiacaoMeta, VwcsEcomPedidosJp, db, Closing
import time

closing_bp = Blueprint('closing_bp', __name__)



@closing_bp.route('/closing', methods=['GET'], strict_slashes=False)
def get_closing():
    start_time = time.time()

    # Retrieve the query parameters
    mes_ano = request.args.get('mes_ano')
    cupom_vendedora = request.args.get('cupomvendedora')
    time_colaborador = request.args.get('time')

    try:
        # Initialize the query with a join between Closing and Colaborador
        query = (
            db.session.query(
                Closing,
                Colaborador.time.label('colaborador_time'),  # Renomeia o campo para evitar conflitos
                Colaborador.nome
            )
            .join(Colaborador, Colaborador.cupom == Closing.cupom_vendedora)
        )
        
        # Apply filters based on parameters
        if cupom_vendedora:
            query = query.filter(Closing.cupom_vendedora == cupom_vendedora)
        
        if time_colaborador:
            query = query.filter(Colaborador.time == time_colaborador)
        
        if mes_ano:
            query = query.filter(Closing.mes_ano == mes_ano)
        
        # Execute the query
        results = query.all()

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Convert the query result to a list of dictionaries
    formatted_results = []
    for closing, colaborador_time, nome in results:
        closing_dict = closing.to_dict()
        closing_dict['time'] = colaborador_time  # Usa o nome atualizado da label
        closing_dict['nome'] = nome
        formatted_results.append(closing_dict)

    elapsed_time = time.time() - start_time
    print(f"Tempo de execução: {elapsed_time:.4f} segundos")

    # Return the results as a JSON response
    return jsonify(formatted_results) if formatted_results else jsonify([])




@closing_bp.route('/closingGroup', methods=['GET'], strict_slashes=False)
def get_closing_grouped():
    start_time = time.time()
    time_param = request.args.get('time')
    try:
        # Montar a consulta
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

        # Aplicar filtro por tempo se o parâmetro estiver presente
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

    # Convert the list of grouped results to a list of dictionaries
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

    # Return the grouped results as a JSON response
    return jsonify(results) if results else jsonify([])

# Define o fuso horário local
local_tz = pytz.timezone('America/Sao_Paulo')

def ajustar_para_fuso_horario_local(data_utc):
    """
    Converte a data do UTC para o fuso horário de São Paulo.
    """
    if data_utc is None:
        return None
    # Converte do UTC para o fuso horário local
    return data_utc.astimezone(local_tz)
@closing_bp.route('/closingOrder', methods=['GET'], strict_slashes=False)
def get_orders():
    start_time = time.time()
    start_date_str = request.args.get('startDate')
    end_date_str = request.args.get('endDate')
    cupom_vendedora = request.args.get('cupomvendedora')
    time_colaborador = request.args.get('time') 
    local_tz = pytz.timezone('America/Sao_Paulo')
    query = db.session.query(VwcsEcomPedidosJp).filter(VwcsEcomPedidosJp.status == 'APROVADO')

    if start_date_str:
        try:
            start_date_local = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=local_tz)
            start_date_utc = start_date_local.astimezone(pytz.utc)
            query = query.filter(VwcsEcomPedidosJp.data_submissao >= start_date_utc)
        except Exception:
            return jsonify({'error': 'Formato de start_date inválido. Use o formato YYYY-MM-DD.'}), 400

    if end_date_str:
        try:
            end_date_local = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=local_tz)
            end_date_utc = end_date_local.astimezone(pytz.utc)
            query = query.filter(VwcsEcomPedidosJp.data_submissao <= end_date_utc)
        except Exception:
            return jsonify({'error': 'Formato de end_date inválido. Use o formato YYYY-MM-DD.'}), 400

    # Filtra por cupom_vendedora
    if cupom_vendedora:
        query = query.filter(VwcsEcomPedidosJp.cupom_vendedora.ilike(f'%{cupom_vendedora}%'))

    # Filtra por time_colaborador
    if time_colaborador:
        colaboradores = Colaborador.query.filter_by(time=time_colaborador).all()
        cupoms = [colaborador.cupom for colaborador in colaboradores]
        query = query.filter(VwcsEcomPedidosJp.cupom_vendedora.in_(cupoms))

    try:
        grouped_data = (
            query.with_entities(
                VwcsEcomPedidosJp.cupom_vendedora,
                func.min(VwcsEcomPedidosJp.data_submissao).label('min_date'),
                func.sum(cast(func.replace(VwcsEcomPedidosJp.valor_pago, ',', '.'), Numeric)).label('total_valor_pago'),
                func.sum(cast(func.replace(VwcsEcomPedidosJp.valor_frete, ',', '.'), Numeric)).label('total_valor_frete')
            )
            .group_by(
                VwcsEcomPedidosJp.cupom_vendedora
            )
        ).all()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    results = []
    for data in grouped_data:

        total_comissao = (
            (float(data.total_valor_pago) if data.total_valor_pago is not None else 0.0) -
            (float(data.total_valor_frete) if data.total_valor_frete is not None else 0.0)
        )

        # Garantir que mes e ano sejam inteiros e formatar mes_ano corretamente
        # mes = int(data.min_date) if data.min_date is not None else 0
        # ano = int(data.min_date) if data.min_date is not None else 0
        # Extrai mês e ano da data ajustada
        # mes = data_inicio_mes_local.month
        # ano = data_inicio_mes_local.year
         # Garantir que min_date seja um objeto datetime
        if data.min_date is not None:
            mes = data.min_date.month
            ano = data.min_date.year
        else:
            mes = 0
            ano = 0
        mes_formatado = f"{mes:02d}"
        mes_ano = f"{mes_formatado}-{ano}"
        print(mes_ano)


        # Inicializa as variáveis com valores padrão
        selected_meta = 'Não atingiu a meta'
        porcentagem = 0
        valor_meta = 0
        premiacao_meta = 0 

        # Busca a meta correspondente ordenada por valor de forma decrescente
        metas = db.session.query(Meta).filter(
            Meta.cupom == data.cupom_vendedora,
            Meta.mes_ano == mes_ano
        ).order_by(Meta.valor.desc()).all()

        

        # Verifica qual meta se aplica
        for meta in metas:
            if total_comissao >= meta.valor:
                selected_meta = meta.meta
                porcentagem = meta.porcentagem
                valor_meta = meta.valor
                break

        # Busca o time do colaborador
        colaborador = db.session.query(Colaborador).filter(
            Colaborador.cupom == data.cupom_vendedora
        ).first()

        if colaborador:
            # Busca a premiacao correspondente
            premiacao = db.session.query(PremiacaoMeta).filter(
                PremiacaoMeta.descricao == selected_meta,
                PremiacaoMeta.time == colaborador.time
            ).first()
            
            if premiacao:
                premiacao_meta = premiacao.valor
            else:
                # Se não houver premiacao, pode deixar premiacao_meta como 0, ou definir um valor padrão
                premiacao_meta = 0
        results.append({
            'cupom_vendedora': data.cupom_vendedora,
            'mes': mes,
            'ano': ano,
            'total_valor_pago': float(data.total_valor_pago) if data.total_valor_pago is not None else 0.0,
            'total_valor_frete': float(data.total_valor_frete) if data.total_valor_frete is not None else 0.0,
            'total_comissional': total_comissao,
            'meta': selected_meta,
            'porcentagem': porcentagem,
            'premiacao_meta': premiacao_meta,
            'Valor_comisao':total_comissao*porcentagem
        })

    elapsed_time = time.time() - start_time
    print(f"Tempo de execução: {elapsed_time:.4f} segundos")

    return jsonify(results)

@closing_bp.route('/closing', methods=['POST'])
def create_colaborador():
    data_list = request.get_json()
    
    if not isinstance(data_list, list):
        return jsonify({'error': 'O formato dos dados está incorreto. Espera-se uma lista de objetos.'}), 400

    try:
        for data in data_list:
            if not isinstance(data, dict):
                return jsonify({'error': 'Os itens da lista devem ser dicionários.'}), 400
            
            # Imprimir dados recebidos
            print(f"Dados recebidos: {data}")

            mes = data.get('mes')
            ano = data.get('ano')
            mes_ano = data.get('mes_ano')
            cupom_vendedora = data.get('cupom_vendedora')
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
            
            # Imprimir dados convertidos
            print(f"Mes: {mes}, Ano: {ano}")

            # Certificar-se de que 'mes' e 'ano' são tratados corretamente
            if isinstance(mes, int):
                mes = str(mes)
            if isinstance(ano, int):
                ano = str(ano)

            # Imprimir dados convertidos
            print(f"Mes convertido: {mes}, Ano convertido: {ano}")

            # Verificar duplicidade
            # Verificar duplicidade baseada em cupom_vendedora, mes e ano
            existing_closing = Closing.query.filter(
                (Closing.cupom_vendedora == cupom_vendedora) &
                (Closing.mes == mes) &
                (Closing.ano == ano)
            ).all()


            # Imprimir registros existentes
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
                mes=mes, ano=ano, mes_ano=mes_ano, cupom_vendedora=cupom_vendedora, total_pago=total_pago,
                total_frete=total_frete, total_comissional=total_comissional, meta_atingida=meta_atingida,
                porcentagem_meta=porcentagem_meta, valor_comissao=valor_comissao, premiacao_meta=premiacao_meta,
                qtd_reconquista=qtd_reconquista, vlr_reconquista=vlr_reconquista, vlr_total_reco=vlr_total_reco,
                qtd_repagar=qtd_repagar, vlr_recon_mes_ant=vlr_recon_mes_ant, vlr_total_recon_mes_ant=vlr_total_recon_mes_ant,
                premiacao_reconquista=premiacao_reconquista, total_receber=total_receber
            )
            
            # Imprimir novo registro
            print(f"Novo registro: {new_closing}")

            db.session.add(new_closing)

        db.session.commit()
        return jsonify({'message': 'Closings criados com sucesso'}), 201
    except Exception as e:
        print(f"Erro ao criar closing: {e}")
        return jsonify({'error': 'Erro ao criar closing'}), 500