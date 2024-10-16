from database import db
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class Meta(db.Model):
    __tablename__ = 'meta'

    cupom = db.Column(db.String(50), ForeignKey('colaborador.cupom'), primary_key=True)
    nome = db.Column(db.String(50), ForeignKey('colaborador.nome'), primary_key=True)
    meta = db.Column(db.String(100), primary_key=True)
    porcentagem = db.Column(db.Float, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    mes_ano = db.Column(db.String(50), primary_key=True)

    # Specify the foreign keys explicitly to resolve the ambiguity
    colaborador = relationship(
        'Colaborador',
        backref='metas',
        lazy=True,
        foreign_keys=[cupom]  # Specify only the appropriate foreign key for the relationship
    )

    def __init__(self, cupom, nome, meta, porcentagem, valor, mes_ano):
        self.cupom = cupom
        self.nome = nome
        self.meta = meta
        self.porcentagem = porcentagem
        self.valor = valor
        self.mes_ano = mes_ano

    def to_dict(self):
        return {
            'id': f"{self.cupom}_{self.nome}_{self.mes_ano}_{self.meta}",
            'cupom': self.cupom,
            'nome': self.nome,
            'meta': self.meta,
            'porcentagem': self.porcentagem,
            'valor': self.valor,
            'mes_ano': self.mes_ano
        }
