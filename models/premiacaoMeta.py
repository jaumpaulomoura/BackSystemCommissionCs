
from database import db
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
            'valor': self.valor}