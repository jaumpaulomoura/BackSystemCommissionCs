from database import db
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
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