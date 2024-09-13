from database import db
from datetime import  datetime


        
        
        
        
        
      
        
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