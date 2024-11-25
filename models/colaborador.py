from database import db
class Colaborador(db.Model):
    __tablename__ = 'colaborador'
    
    cupom = db.Column(db.String(50), primary_key=True)
    nome = db.Column(db.String(100), primary_key=True)
    funcao = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), primary_key=True)  
    password = db.Column(db.String(255), nullable=False)
    dt_insert = db.Column(db.DateTime, default=db.func.current_timestamp())
    dtadmissao=db.Column(db.DateTime, nullable=False)
    dtdemissao=db.Column(db.DateTime, nullable=False)
    
    def __init__(self, cupom, nome,  funcao, time, email, password,dtadmissao,dtdemissao):
        self.cupom = cupom
        self.nome = nome
        self.funcao = funcao
        self.time = time
        self.email = email
        self.password = password
        self.dtadmissao=dtadmissao
        self.dtdemissao=dtdemissao
        
    def to_dict(self):
        return {
            'id': f"{self.cupom}_{self.nome}_{self.time}",
            'cupom': self.cupom,
            'nome': self.nome,
            'funcao': self.funcao,
            'time': self.time,
            'email': self.email,
            'password': self.password,
            'dt_insert': self.dt_insert.isoformat() if self.dt_insert else None,
            'dtadmissao': self.dtadmissao.isoformat() if self.dtadmissao else None,
            'dtdemissao': self.dtdemissao.isoformat() if self.dtdemissao else None,
        }
