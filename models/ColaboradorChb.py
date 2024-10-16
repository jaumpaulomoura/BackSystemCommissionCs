from database import db
class Funcionario(db.Model):
    __tablename__ = 'FP02T3'
    __bind_key__ = 'oracle'
    
    pe01codemp = db.Column(db.String, primary_key=True)
    fp02cod = db.Column(db.String,primary_key=True)
    fp02matric = db.Column(db.String,primary_key=True)
    fp02nom = db.Column(db.String)
    fp03depto = db.Column(db.String)
    fp02situ = db.Column(db.String)
    fp02dtadmi = db.Column(db.Date)

    def to_dict(self):
        return {
            "pe01codemp": self.pe01codemp,
            "fp02cod": self.fp02cod,
            "fp02matric": self.fp02matric,
            "fp02nom": self.fp02nom,
            "fp03depto": self.fp03depto,
            "fp02situ": self.fp02situ,
            "fp02dtadmi": self.fp02dtadmi,
        }

class Departamento(db.Model):
    __tablename__ = 'FP03T1'
    __bind_key__ = 'oracle'
    
    pe01codemp = db.Column(db.String, primary_key=True)
    fp03depto = db.Column(db.String, primary_key=True)
    fp03descri = db.Column(db.String)

    def to_dict(self):
        return {
            "pe01codemp": self.pe01codemp,
            "fp03depto": self.fp03depto,
            "fp03descri": self.fp03descri,
        }

class Rescisao(db.Model):
    __tablename__ = 'FP74T'
    __bind_key__ = 'oracle'
    
    pe01codemp = db.Column(db.String, primary_key=True)
    fp02cod = db.Column(db.String, primary_key=True)
    fp74dtresc = db.Column(db.Date)

    def to_dict(self):
        return {
            "pe01codemp": self.pe01codemp,
            "fp02cod": self.fp02cod,
            "fp74dtresc": self.fp74dtresc,
        }
