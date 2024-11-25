
from database import db   
        
        
class VwcsEcomPedidosJp(db.Model):
    __tablename__ = 'VWCS_ECOM_PEDIDOS_SISTEMA'

    pedido = db.Column(db.String, primary_key=True)
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
        