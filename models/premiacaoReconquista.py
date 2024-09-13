from database import db
        
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
