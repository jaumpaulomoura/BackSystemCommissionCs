from datetime import date, datetime
from decimal import Decimal
import time
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from database import db

class Colaborador(db.Model):
    __tablename__ = 'colaborador'
    
    cupom = db.Column(db.String(50), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    funcao = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    
    def __init__(self, cupom, nome, funcao, time):
         self.cupom = cupom
         self.nome = nome
         self.funcao = funcao
         self.time = time
         
    def to_dict(self):
        return {
            'id': f"{self.cupom}_{self.nome}_{self.time}",
            'cupom': self.cupom,
            'nome': self.nome,
            'funcao': self.funcao,
            'time': self.time,
        }

class Meta(db.Model):
    __tablename__ = 'meta'

    cupom = db.Column(db.String(50), ForeignKey('colaborador.cupom'), primary_key=True)
    meta = db.Column(db.String(100), primary_key=True)
    porcentagem = db.Column(db.Float, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    mes_ano = db.Column(db.String(50), primary_key=True)
    
    colaborador = relationship('Colaborador', backref='metas', lazy=True)

    def __init__(self, cupom, meta, porcentagem, valor, mes_ano):
        self.cupom = cupom
        self.meta = meta
        self.porcentagem = porcentagem
        self.valor = valor
        self.mes_ano = mes_ano

    def to_dict(self):
        return {
            'id': f"{self.cupom}_{self.mes_ano}_{self.meta}",
            'cupom': self.cupom,
            'meta': self.meta,
            'porcentagem': self.porcentagem,
            'valor': self.valor,
            'mes_ano': self.mes_ano
        }
class PremiacaoMeta(db.Model):
    __tablename__ = 'premiacao_meta'

    descricao = db.Column(db.String, primary_key=True)
    time = db.Column(db.String, primary_key=True)
    valor = db.Column(db.Float, nullable=False)

    def __init__(self, descricao, time, valor):
        self.descricao = descricao
        self.time = time
        self.valor = valor

    def to_dict(self):
        return {
            'id': f"{self.descricao}_{self.time}",
            'descricao': self.descricao,
            'time': self.time,
            'valor': self.valor
        }
class PremiacaoReconquista(db.Model):
    __tablename__ = 'premiacao_reconquista'

    descricao = db.Column(db.String, primary_key=True)
    time = db.Column(db.String, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    minimo = db.Column(db.Float, nullable=False)
    maximo = db.Column(db.Float, nullable=False)

    def __init__(self, descricao, time, valor,minimo,maximo):
        self.descricao = descricao
        self.time = time
        self.valor = valor
        self.minimo=minimo
        self.maximo=maximo

    def to_dict(self):
        return {
            'id': f"{self.descricao}_{self.time}",
            'descricao': self.descricao,
            'time': self.time,
            'valor': self.valor,
            'minimo': self.minimo,
            'maximo': self.maximo
        }

class SubmittedOrder(db.Model):
    __tablename__ = 'submitted_order'
    
    order_id = db.Column(db.String, primary_key=True)
    submitted_date = db.Column(db.Date)
    send_franchise_order_kpl = db.Column(db.Boolean)
    state = db.Column(db.String)
    occ_payload = db.Column(db.JSON)
    cs_shipping = db.Column(db.JSON)
    cs_pickup_in_store = db.Column(db.String)
    profile_id = db.Column(db.String)

    def __init__(self, order_id, submitted_date, send_franchise_order_kpl, state, occ_payload, cs_shipping, cs_pickup_in_store, profile_id):
        self.order_id = order_id
        self.submitted_date = submitted_date
        self.send_franchise_order_kpl = send_franchise_order_kpl
        self.state = state
        self.occ_payload = occ_payload
        self.cs_shipping = cs_shipping
        self.cs_pickup_in_store = cs_pickup_in_store
        self.profile_id = profile_id

    def to_dict(self):
        return {
            'pedido': self.order_id,
            'data_submissao': self.submitted_date,
            'mes': self.submitted_date.month,
            'ano': self.submitted_date.year,
            'hora_submissao': self.submitted_date.strftime('%H:%M:%S'),  
            'status': self.get_status(),
            'total_itens': self.get_total_items(),
            'envio': self.get_shipping_method(),
            'idloja': self.get_store_id(),
            'site': self.get_site(),
            'valor_bruto': self.get_raw_subtotal(),  # Aqui você está chamando o método
            'valor_desconto': self.get_valor_desconto(),
            'valor_frete': self.get_valor_frete(),
            'valor_pago': self.get_valor_pago(),
            'cupom': self.get_coupon_code(),
            'cupom_vendedora': self.get_seller_coupon_code(),
            'metodo_pagamento': self.get_payment_method(),
            'id_cliente': self.profile_id
        }


    def get_payment_method(self):
        payment_groups = self.occ_payload.get('order', {}).get('paymentGroups', [])
        if not payment_groups:
            return 'UNKNOWN'
        
        payment_method = payment_groups[0].get('paymentMethod', 'UNKNOWN')
        if payment_method == 'creditCard':
            return 'CARTAO DE CREDITO'
        elif payment_method == 'invoiceRequest':
            return 'BOLETO'
        elif payment_method == 'cash':
            return 'PIX'
        else:
            return payment_method

    def get_shipping_method(self):
        shipping_groups = self.occ_payload.get('order', {}).get('shippingGroups', [])
        if not shipping_groups:
            return 'UNKNOWN'
        
        shipping_method = shipping_groups[0].get('shippingMethod', 'UNKNOWN')
        if shipping_method == 'economic':
            return 'ECONOMICO'
        elif shipping_method == 'fast':
            return 'RAPIDO'
        elif shipping_method == '700001':
            return 'RETIRADA EM LOJA'
        else:
            return shipping_method.upper()
    
    def get_status(self):
        if self.send_franchise_order_kpl in [True, False]:
            return 'PRE-VENDA'
        
        state_map = {
            'APPROVED': 'APROVADO',
            'FAILED_APPROVAL': 'NAO AUTORIZADO',
            'REMOVED': 'CANCELADO',
            'PROCESSING': 'PENDENTE',
            'PENDING_PAYMENT': 'PENDENTE'
        }
        
        return state_map.get(self.state, self.state)

    def get_store_id(self):
        # Verificar se a coluna cs_shipping contém 'storeId'
        if self.cs_shipping:
            shipping_info = self.cs_shipping.get('shipping', [])
            if shipping_info and len(shipping_info) > 0:
                store_id = shipping_info[0].get('storeId', '')
                # Ajustar a condição para verificar se o store_id não está vazio
                if store_id:
                    return store_id
        
        # Se cs_shipping não contém storeId ou está vazio, retornar cs_pickup_in_store
        if self.cs_pickup_in_store:
            return self.cs_pickup_in_store
        
        return None

    def get_coupon_code(self):
        # Iterar sobre os itens de commerceItems e retornar o primeiro código de cupom encontrado
        commerce_items = self.occ_payload.get('order', {}).get('commerceItems', [])
        for item in commerce_items:
            price_info = item.get('priceInfo', {})
            order_discount_infos = price_info.get('orderDiscountInfos', [])
            if order_discount_infos:  # Verifica se a lista não está vazia
                coupon_codes = order_discount_infos[0].get('couponCodes', [])
                if coupon_codes:  # Verifica se a lista de códigos de cupom não está vazia
                    return coupon_codes[0]
        return None

    def get_seller_coupon_code(self):
        # Iterar sobre os itens de commerceItems e retornar o primeiro código de cupom encontrado em itemDiscountInfos
        commerce_items = self.occ_payload.get('order', {}).get('commerceItems', [])
        for item in commerce_items:
            price_info = item.get('priceInfo', {})
            item_discount_infos = price_info.get('itemDiscountInfos', [])
            if item_discount_infos:  # Verifica se a lista não está vazia
                coupon_codes = item_discount_infos[0].get('couponCodes', [])
                if coupon_codes:  # Verifica se a lista de códigos de cupom não está vazia
                    return coupon_codes[0]
        return None

    def get_parcelas(self):
        # Obtém o valor de cardInstallments e verifica se ele não está na lista de valores
        card_installments = self.occ_payload.get('order', {}).get('cardInstallments', '')
        if not card_installments or card_installments not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']:
            return '1'
        return card_installments
    def get_site(self):
        # Obtém o valor de siteName e transforma para maiúsculas
        site_name = self.occ_payload.get('site', {}).get('siteName', '')
        return site_name.upper()

    def get_valor_desconto(self):
        # Obtém o valor de discountAmount e substitui pontos por vírgulas
        discount_amount = self.occ_payload.get('order', {}).get('priceInfo', {}).get('discountAmount', '')
        if isinstance(discount_amount, str):
            return discount_amount.replace('.', ',')
        return discount_amount

    def get_valor_frete(self):
        # Obtém o valor de shipping e substitui pontos por vírgulas
        shipping = self.occ_payload.get('order', {}).get('priceInfo', {}).get('shipping', '')
        if isinstance(shipping, str):
            return shipping.replace('.', ',')
        return shipping

    def get_valor_pago(self):
        # Obtém o valor de total e substitui pontos por vírgulas
        total = self.occ_payload.get('order', {}).get('priceInfo', {}).get('total', '')
        if isinstance(total, str):
            return total.replace('.', ',')
        return total
    def get_total_items(self):
        # Obtém o valor de totalCommerceItemCount e retorna como string
        total_items = self.occ_payload.get('order', {}).get('totalCommerceItemCount', '')
        return total_items
    def get_valor_total(self):
        # Retorna o valor total da ordem
        return float(self.occ_payload.get('order', {}).get('priceInfo', {}).get('total', 0))
    def get_raw_subtotal(self):
        # Obtém o valor de rawSubtotal e substitui pontos por vírgulas
        raw_subtotal = self.occ_payload.get('order', {}).get('priceInfo', {}).get('rawSubtotal', '')
        if isinstance(raw_subtotal, str):
            return raw_subtotal.replace('.', ',')
        return raw_subtotal
    
class Ticket(db.Model):
    __tablename__ = 'ticket'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orderId = db.Column('orderid', db.String(255), nullable=False)
    octadeskId = db.Column('octadeskid', db.String(255), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.String(300))
    status = db.Column(db.String(100), nullable=False)
    cupomvendedora = db.Column(db.String(100), nullable=False)
    dateCreated = db.Column('datecreated', db.Date, default=datetime.utcnow, nullable=False)
    dateUpdated = db.Column('dateupdated', db.Date, onupdate=datetime.utcnow)

    def __init__(self, orderId, octadeskId, reason,cupomvendedora, notes=None, status='Aberto', dateCreated=None, dateUpdated=None):
        self.orderId = orderId
        self.octadeskId = octadeskId
        self.reason = reason
        self.notes = notes
        self.status = status
        self.cupomvendedora = cupomvendedora
        self.dateCreated = dateCreated if dateCreated is not None else datetime.utcnow().date()
        self.dateUpdated = dateUpdated

    def to_dict(self):
        return {
            'id': self.id,
            'orderId': self.orderId,
            'octadeskId': self.octadeskId,
            'reason': self.reason,
            'notes': self.notes,
            'status': self.status,
            'cupomvendedora': self.cupomvendedora,
            'dateCreated': self.dateCreated.isoformat() if self.dateCreated else None,
            'dateUpdated': self.dateUpdated.isoformat() if self.dateUpdated else None
        }
        
        
        
        
        
        
        
        
        
class VwcsEcomPedidosJp(db.Model):
    __tablename__ = 'VWCS_ECOM_PEDIDOS_SISTEMA'

    pedido = db.Column(db.String, primary_key=True)
    # mes= db.Column(db.Text)
    # ano= db.Column(db.Text)
    data_submissao = db.Column(db.Date)
    hora_submissao = db.Column(db.Time)
    status = db.Column(db.String)
    total_itens = db.Column(db.Text)
    envio = db.Column(db.Text)
    idloja = db.Column(db.Text)
    site = db.Column(db.Text)
    valor_bruto = db.Column(db.Text)
    valor_desconto = db.Column(db.Text)
    valor_frete = db.Column(db.Text)
    valor_pago = db.Column(db.Text)
    cupom = db.Column(db.Text)
    cupom_vendedora = db.Column(db.Text)
    metodo_pagamento = db.Column(db.Text)
    parcelas = db.Column(db.Text)
    id_cliente = db.Column(db.String)

    def __init__(self, pedido, data_submissao, hora_submissao, status, total_itens, envio, idloja, site, valor_bruto, valor_desconto, valor_frete, valor_pago, cupom, cupom_vendedora, metodo_pagamento, parcelas, id_cliente):
        self.pedido = pedido
        # self.mes=mes
        # self.ano=ano
        self.data_submissao = data_submissao
        self.hora_submissao = hora_submissao
        self.status = status
        self.total_itens = total_itens
        self.envio = envio
        self.idloja = idloja
        self.site = site
        self.valor_bruto = valor_bruto
        self.valor_desconto = valor_desconto
        self.valor_frete = valor_frete
        self.valor_pago = valor_pago
        self.cupom = cupom
        self.cupom_vendedora = cupom_vendedora
        self.metodo_pagamento = metodo_pagamento
        self.parcelas = parcelas
        self.id_cliente = id_cliente

    def to_dict(self):
        return {
            'pedido': self.pedido,
            # 'mes': self.mes,
            # 'ano': self.ano,
            'data_submissao': self.data_submissao.isoformat() if self.data_submissao else None,
            'hora_submissao': self.hora_submissao.isoformat() if self.hora_submissao else None,
            'status': self.status,
            'total_itens': self.total_itens,
            'envio': self.envio,
            'idloja': self.idloja,
            'site': self.site,
            'valor_bruto': self.valor_bruto,
            'valor_desconto': self.valor_desconto,
            'valor_frete': self.valor_frete,
            'valor_pago': self.valor_pago,
            'cupom': self.cupom,
            'cupom_vendedora': self.cupom_vendedora,
            'metodo_pagamento': self.metodo_pagamento,
            'parcelas': self.parcelas,
            'id_cliente': self.id_cliente
        }
        
      
        
class Closing(db.Model):
    __tablename__ = 'closing'

    __table_args__ = {'extend_existing': True}

    mes = db.Column(db.String, nullable=False)
    ano = db.Column(db.String, nullable=False)
    mes_ano = db.Column(db.String, nullable=False, primary_key=True)
    cupom_vendedora = db.Column(db.String, nullable=False, primary_key=True)
    total_pago = db.Column(db.Numeric, nullable=False)
    total_frete = db.Column(db.Numeric, nullable=False)
    total_comissional = db.Column(db.Numeric, nullable=False)
    meta_atingida = db.Column(db.String, nullable=False)
    porcentagem_meta = db.Column(db.Numeric, nullable=False)
    valor_comissao = db.Column(db.Numeric, nullable=False)
    premiacao_meta = db.Column(db.Numeric, nullable=True)
    qtd_reconquista = db.Column(db.Numeric, nullable=True)
    vlr_reconquista = db.Column(db.Numeric, nullable=True)
    vlr_total_reco = db.Column(db.Numeric, nullable=True)
    qtd_repagar = db.Column(db.Numeric, nullable=True)
    vlr_recon_mes_ant = db.Column(db.Numeric, nullable=True)
    vlr_total_recon_mes_ant = db.Column(db.Numeric, nullable=True)
    premiacao_reconquista = db.Column(db.Numeric, nullable=True)
    total_receber = db.Column(db.Numeric, nullable=False)
    dt_insert = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


    def __init__(self, mes, ano, mes_ano, cupom_vendedora, total_pago, total_frete, total_comissional, meta_atingida, 
                 porcentagem_meta, valor_comissao, premiacao_meta, qtd_reconquista, vlr_reconquista, vlr_total_reco, 
                 qtd_repagar, vlr_recon_mes_ant, vlr_total_recon_mes_ant, premiacao_reconquista, total_receber, dt_insert=None):
        self.mes = mes
        self.ano = ano
        self.mes_ano = mes_ano
        self.cupom_vendedora = cupom_vendedora
        self.total_pago = total_pago
        self.total_frete = total_frete
        self.total_comissional = total_comissional
        self.meta_atingida = meta_atingida
        self.porcentagem_meta = porcentagem_meta
        self.valor_comissao = valor_comissao
        self.premiacao_meta = premiacao_meta
        self.qtd_reconquista = qtd_reconquista
        self.vlr_reconquista = vlr_reconquista
        self.vlr_total_reco = vlr_total_reco
        self.qtd_repagar = qtd_repagar
        self.vlr_recon_mes_ant = vlr_recon_mes_ant
        self.vlr_total_recon_mes_ant = vlr_total_recon_mes_ant
        self.premiacao_reconquista = premiacao_reconquista
        self.total_receber = total_receber
        self.dt_insert = dt_insert if dt_insert is not None else datetime.utcnow().date()

    def to_dict(self):
        return {
            'mes': self.mes,
            'ano': self.ano,
            'mes_ano': self.mes_ano,
            'cupom_vendedora': self.cupom_vendedora,
            'total_pago': self.total_pago,
            'total_frete': self.total_frete,
            'total_comissional': self.total_comissional,
            'meta_atingida': self.meta_atingida,
            'porcentagem_meta': self.porcentagem_meta,
            'valor_comissao': self.valor_comissao,
            'premiacao_meta': self.premiacao_meta,
            'qtd_reconquista': self.qtd_reconquista,
            'vlr_reconquista': self.vlr_reconquista,
            'vlr_total_reco': self.vlr_total_reco,
            'qtd_repagar': self.qtd_repagar,
            'vlr_recon_mes_ant': self.vlr_recon_mes_ant,
            'vlr_total_recon_mes_ant': self.vlr_total_recon_mes_ant,
            'premiacao_reconquista': self.premiacao_reconquista,
            'total_receber': self.total_receber,
            'dt_insert': self.dt_insert.isoformat() if self.dt_insert else None,
        }