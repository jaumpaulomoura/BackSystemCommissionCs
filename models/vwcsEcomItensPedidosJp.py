from sqlalchemy import Numeric

from database import db   
class VwcsEcomItensPedidosJp(db.Model):
    __tablename__ = 'VWCS_ECOM_ITENSPEDIDOS_SISTEMA'

    id_pedido = db.Column(db.String(255), db.ForeignKey('VWCS_ECOM_PEDIDOS.pedido'), primary_key=True)
    referencia = db.Column(db.String)  # Correspondente a character varying
    tamanho = db.Column(db.String)      # Correspondente a character varying
    quantidade = db.Column(db.Integer)  # Correspondente a integer
    valor_venda_unitario = db.Column(db.Text)    # Use Numeric para valores monetários
    valor_desconto = db.Column(db.Text)         # Use Numeric para valores monetários
    valor_pago = db.Column(db.Text)           # Use Numeric para valores monetários
    link = db.Column(db.Text)                   # Correspondente a text
    nome_site = db.Column(db.String(255))       # Correspondente a character varying

    def __init__(self, id_pedido, referencia, tamanho, quantidade, valor_venda_unitario, valor_desconto, valor_pago, link, nome_site):
        self.id_pedido = id_pedido
        self.referencia = referencia
        self.tamanho = tamanho
        self.quantidade = quantidade
        self.valor_venda_unitario = valor_venda_unitario
        self.valor_desconto = valor_desconto
        self.valor_pago = valor_pago
        self.link = link
        self.nome_site = nome_site

    def to_dict(self):
        return {
            'pedido': self.id_pedido,
            'modelo': self.referencia,
            'tamanho': self.tamanho,
            'quantidade': self.quantidade,
            'valorVendaUnit': self.valor_venda_unitario,
            'valorDesc': self.valor_desconto,
            'valorPago': self.valor_pago,
            'link': self.link,
            'nomeSite': self.nome_site,
        }
