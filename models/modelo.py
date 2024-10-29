from flask_sqlalchemy import SQLAlchemy
from database import db
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

db = SQLAlchemy()

# Modelo para tabela Cor
class Cor(db.Model):
    __tablename__ = 'PC10T'
    __bind_key__ = 'oracle'
    PC10CODIGO = db.Column('PC10CODIGO', db.String(50), primary_key=True)
    PC10DESCR = db.Column('PC10DESCR', db.String(100))

    def __init__(self, PC10CODIGO, PC10DESCR):
        self.PC10CODIGO = PC10CODIGO
        self.PC10DESCR = PC10DESCR

    def to_dict(self):
        return {
            'codCor': self.PC10CODIGO,
            'descCor': self.PC10DESCR
        }

# Modelo para tabela ClassModelo
class ClassModelo(db.Model):
    __tablename__ = 'PC04T'
    __bind_key__ = 'oracle'
    PC04CODIGO = db.Column('PC04CODIGO', db.String(50), primary_key=True)
    PC04DESCR = db.Column('PC04DESCR', db.String(100))

    def __init__(self, PC04CODIGO, PC04DESCR):
        self.PC04CODIGO = PC04CODIGO
        self.PC04DESCR = PC04DESCR

    def to_dict(self):
        return {
            'codClassModelo': self.PC04CODIGO,
            'descClassModelo': self.PC04DESCR
        }

# Modelo para tabela GrupoGestor
class GrupoGestor(db.Model):
    __tablename__ = 'PCALT'
    __bind_key__ = 'oracle'
    PCALCODEMP = db.Column('PCALCODEMP', db.String(50))
    PCALCODIGO = db.Column('PCALCODIGO', db.String(50), primary_key=True)
    PCALDESCR = db.Column('PCALDESCR', db.String(100))

    def __init__(self, PCALCODEMP, PCALCODIGO, PCALDESCR):
        self.PCALCODEMP = PCALCODEMP
        self.PCALCODIGO = PCALCODIGO
        self.PCALDESCR = PCALDESCR

    def to_dict(self):
        return {
            'empresa': self.PCALCODEMP,
            'codGrupoGestor': self.PCALCODIGO,
            'descGrupoGestor': self.PCALDESCR
        }

# Modelo para tabela Colecao
class Colecao(db.Model):
    __tablename__ = 'PCAIT'
    __bind_key__ = 'oracle'
    PCAICODEMP = db.Column('PCAICODEMP', db.String(50))
    PCAICODIGO = db.Column('PCAICODIGO', db.String(50), primary_key=True)
    PCAIDESC = db.Column('PCAIDESC', db.String(100))

    def __init__(self, PCAICODEMP, PCAICODIGO, PCAIDESC):
        self.PCAICODEMP = PCAICODEMP
        self.PCAICODIGO = PCAICODIGO
        self.PCAIDESC = PCAIDESC

    def to_dict(self):
        return {
            'empresa': self.PCAICODEMP,
            'codCol': self.PCAICODIGO,
            'descCol': self.PCAIDESC
        }

# Modelo para tabela Lancamento
class Lancamento(db.Model):
    __tablename__ = 'PCBMT'
    __bind_key__ = 'oracle'
    PCBMCODEMP = db.Column('PCBMCODEMP', db.String(50))
    PCBMCODIGO = db.Column('PCBMCODIGO', db.String(50), primary_key=True)
    PCBMDESCR = db.Column('PCBMDESCR', db.String(100))

    def __init__(self, PCBMCODEMP, PCBMCODIGO, PCBMDESCR):
        self.PCBMCODEMP = PCBMCODEMP
        self.PCBMCODIGO = PCBMCODIGO
        self.PCBMDESCR = PCBMDESCR

    def to_dict(self):
        return {
            'empresa': self.PCBMCODEMP,
            'codLan': self.PCBMCODIGO,
            'descLan': self.PCBMDESCR
        }

# Modelo para tabela CategoriaGestor
class CategoriaGestor(db.Model):
    __tablename__ = 'PCBJT'
    __bind_key__ = 'oracle'
    PCBJCODEMP = db.Column('PCBJCODEMP', db.String(50))
    PCBJCODIGO = db.Column('PCBJCODIGO', db.String(50), primary_key=True)
    PCBJDESCR = db.Column('PCBJDESCR', db.String(100))

    def __init__(self, PCBJCODEMP, PCBJCODIGO, PCBJDESCR):
        self.PCBJCODEMP = PCBJCODEMP
        self.PCBJCODIGO = PCBJCODIGO
        self.PCBJDESCR = PCBJDESCR

    def to_dict(self):
        return {
            'empresa': self.PCBJCODEMP,
            'codCatGestor': self.PCBJCODIGO,
            'descCatGestor': self.PCBJDESCR
        }

# Modelo para tabela CorGestor
class CorGestor(db.Model):
    __tablename__ = 'PCDRT'
    __bind_key__ = 'oracle'
    PCDRCODIGO = db.Column('PCDRCODIGO', db.String(50), primary_key=True)
    PCDRDESCR = db.Column('PCDRDESCR', db.String(100))

    def __init__(self, PCDRCODIGO, PCDRDESCR):
        self.PCDRCODIGO = PCDRCODIGO
        self.PCDRDESCR = PCDRDESCR

    def to_dict(self):
        return {
            'codCorGestor': self.PCDRCODIGO,
            'descCorGestor': self.PCDRDESCR
        }

# Modelo para tabela ClassGestor
class ClassGestor(db.Model):
    __tablename__ = 'PCBKT'
    __bind_key__ = 'oracle'
    PCBKCODEMP = db.Column('PCBKCODEMP', db.String(50))
    PCBKCODIGO = db.Column('PCBKCODIGO', db.String(50), primary_key=True)
    PCBKDESCR = db.Column('PCBKDESCR', db.String(100))

    def __init__(self, PCBKCODEMP, PCBKCODIGO, PCBKDESCR):
        self.PCBKCODEMP = PCBKCODEMP
        self.PCBKCODIGO = PCBKCODIGO
        self.PCBKDESCR = PCBKDESCR

    def to_dict(self):
        return {
            'empresa': self.PCBKCODEMP,
            'codClassGestor': self.PCBKCODIGO,
            'descClassGestor': self.PCBKDESCR
        }

# Modelo para tabela SubClassifGestor
class SubClassifGestor(db.Model):
    __tablename__ = 'PCBKT1'
    __bind_key__ = 'oracle'
    PCBKCODEMP = db.Column('PCBKCODEMP', db.String(50))
    PCBKCODIGO = db.Column('PCBKCODIGO', db.String(50))
    PCBKSUBCLA = db.Column('PCBKSUBCLA', db.String(50), primary_key=True)
    PCBKDESSUB = db.Column('PCBKDESSUB', db.String(100))

    def __init__(self, PCBKCODEMP, PCBKCODIGO, PCBKSUBCLA, PCBKDESSUB):
        self.PCBKCODEMP = PCBKCODEMP
        self.PCBKCODIGO = PCBKCODIGO
        self.PCBKSUBCLA = PCBKSUBCLA
        self.PCBKDESSUB = PCBKDESSUB

    def to_dict(self):
        return {
            'empresa': self.PCBKCODEMP,
            'codClassGestor': self.PCBKCODIGO,
            'codDubClassGestor': self.PCBKSUBCLA,
            'descSubClassGestor': self.PCBKDESSUB
        }

# Modelo para tabela Linha
class Linha(db.Model):
    __tablename__ = 'PC03T'
    __bind_key__ = 'oracle'
    
    PC03CODEMP = db.Column('PC03CODEMP', db.String(50))
    PC03CODIGO = db.Column('PC03CODIGO', db.String(50), primary_key=True)
    PC03DESCR = db.Column('PC03DESCR', db.String(100))

    def __init__(self, PC03CODEMP, PC03CODIGO, PC03DESCR):
        self.PC03CODEMP = PC03CODEMP
        self.PC03CODIGO = PC03CODIGO
        self.PC03DESCR = PC03DESCR

    def to_dict(self):
        return {
            'empresa': self.PC03CODEMP,
            'codLinha': self.PC03CODIGO,
            'descLinha': self.PC03DESCR
        }

# Modelo para tabela ClasItem
class ClasItem(db.Model):
    __tablename__ = 'PC16T'
    __bind_key__ = 'oracle'
    PC16CODIGO = db.Column('PC16CODIGO', db.String(50), primary_key=True)
    PC16DESCR = db.Column('PC16DESCR', db.String(100))

    def __init__(self, PC16CODIGO, PC16DESCR):
        self.PC16CODIGO = PC16CODIGO
        self.PC16DESCR = PC16DESCR

    def to_dict(self):
        return {
            'codClasItem': self.PC16CODIGO,
            'descClasItem': self.PC16DESCR
        }

# Modelo para tabela Montagem
class Montagem(db.Model):
    __tablename__ = 'PCDOT'
    __bind_key__ = 'oracle'
    PCDOCODEMP = db.Column('PCDOCODEMP', db.String(50))
    PCDOCODIGO = db.Column('PCDOCODIGO', db.String(50), primary_key=True)
    PCDODESCRI = db.Column('PCDODESCRI', db.String(100))

    def __init__(self, PCDOCODEMP, PCDOCODIGO, PCDODESCRI):
        self.PCDOCODEMP = PCDOCODEMP
        self.PCDOCODIGO = PCDOCODIGO
        self.PCDODESCRI = PCDODESCRI

    def to_dict(self):
        return {
            'empresa': self.PCDOCODEMP,
            'codMontagem': self.PCDOCODIGO,
            'descMontagem': self.PCDODESCRI
        }
        
        
class Modelo(db.Model):
    __tablename__ = 'PC13T'
    __bind_key__ = 'oracle'
    
    PC13EMP08 = db.Column('PC13EMP08', db.Integer, primary_key=True)
    PC13CODIGO = db.Column('PC13CODIGO', db.String(50), primary_key=True)
    PC13ANOPED = db.Column('PC13ANOPED', db.String(50)) 
    PC13CODPED = db.Column('PC13CODPED', db.String(50)) 
    PC13COR = db.Column('PC13COR', db.String(50), db.ForeignKey('PC10T.PC10CODIGO')) 
    PC13CODCOL = db.Column('PC13CODCOL', db.String(50), db.ForeignKey('PCAIT.PCAICODIGO')) 
    PC13CODLAN = db.Column('PC13CODLAN', db.String(50), db.ForeignKey('PCBMT.PCBMCODIGO')) 
    PC13CLAITE = db.Column('PC13CLAITE', db.String(50), db.ForeignKey('PC16T.PC16CODIGO')) 
    PC13CLAIPA = db.Column('PC13CLAIPA', db.String(50))
    PC13CODCTG = db.Column('PC13CODCTG',db.Integer, db.ForeignKey('PCBJT.PCBJCODIGO')) 
    PC13CODGMD = db.Column('PC13CODGMD',db.Integer, db.ForeignKey('PCALT.PCALCODIGO')) 
    PC13CODCGE = db.Column('PC13CODCGE',db.Integer, db.ForeignKey('PCBKT.PCBKCODIGO'))  
    PC13CODSCL = db.Column('PC13CODSCL',db.Integer, db.ForeignKey('PCBKT1.PCBKSUBCLA')) 
    PC13GESCOR = db.Column('PC13GESCOR',db.Integer, db.ForeignKey('PCDRT.PCDRCODIGO')) 
    PC13CLASS = db.Column('PC13CLASS', db.Integer, db.ForeignKey('PC04T.PC04CODIGO')) 
    PC13DESPLA = db.Column('PC13DESPLA', db.String(100))
    PC13DESFAT = db.Column('PC13DESFAT', db.String(100))
    PC13GRADE = db.Column('PC13GRADE', db.String(50))
    PC13FORMA = db.Column('PC13FORMA', db.String(50))
   
    PC13NBM = db.Column('PC13NBM', db.Integer)
    PC13LINHA=db.Column('PC13LINHA', db.String(50),db.ForeignKey('PC03T.PC03CODIGO')) 
    PC13PESBRU = db.Column('PC13PESBRU', db.Float)
    PC13PESLIQ = db.Column('PC13PESLIQ', db.Float)
    PC13ALTSAL = db.Column('PC13ALTSAL', db.String(50))
    PC13COMMOD = db.Column('PC13COMMOD', db.Float)
    PC13ALTMOD = db.Column('PC13ALTMOD', db.Float)
    PC13LARMOD = db.Column('PC13LARMOD', db.Float)
    PC13VRUNIT = db.Column('PC13VRUNIT', db.Float)
    PC13ALTSLN = db.Column('PC13ALTSLN', db.Float)
    PC13TIPMON = db.Column('PC13TIPMON', db.String(50),db.ForeignKey('PCDOT.PCDOCODIGO')) 

    
    cor = db.relationship('Cor', backref='modelos_cor', lazy=True)
    colecao = db.relationship('Colecao',  backref='modelos_colecao', lazy=True)
    lancamento = db.relationship('Lancamento',  backref='modelos_lancamento', lazy=True)
    classe_item = db.relationship('ClasItem', backref='modelos_classe', lazy=True)
    categoria = db.relationship('CategoriaGestor', backref='modelos_categoria', lazy=True)
    grupo_marca = db.relationship('GrupoGestor', backref='modelos_grupo', lazy=True)
    categoria_gestor = db.relationship('ClassGestor', backref='modelos_categoria', lazy=True)
    sub_categoria_gestor = db.relationship('SubClassifGestor', backref='modelos_subcategoria', lazy=True)
    gestor_cor = db.relationship('CorGestor', backref='modelos_gestor', lazy=True)
    class_modelo = db.relationship('ClassModelo', backref='modelos_class', lazy=True)
    linha = db.relationship('Linha', backref='modelos_linha', lazy=True)
    tipo_moeda = db.relationship('Montagem', backref='modelos_tipo_moeda', lazy=True)
    
    def __init__(self, PC13CODIGO,PC13ANOPED,PC13CODPED, PC13COR, PC13EMP08, PC13CODCOL, PC13CODLAN, PC13CLAITE, PC13CLAIPA, 
                 PC13CODCTG, PC13CODGMD, PC13CODCGE, PC13CODSCL, PC13GESCOR, PC13CLASS, 
                 PC13DESPLA, PC13DESFAT, PC13GRADE, PC13FORMA, PC13TIPMON, PC13NBM, 
                 PC13PESBRU, PC13PESLIQ, PC13ALTSAL, PC13COMMOD, PC13ALTMOD, PC13LARMOD, 
                 PC13VRUNIT, PC13ALTSLN):
        
        self.PC13CODIGO = PC13CODIGO
        self.PC13ANOPED = PC13ANOPED
        self.PC13CODPED = PC13CODPED
        self.PC13COR = PC13COR
        self.PC13EMP08 = PC13EMP08
        self.PC13CODCOL = PC13CODCOL
        self.PC13CODLAN = PC13CODLAN
        self.PC13CLAITE = PC13CLAITE
        self.PC13CLAIPA = PC13CLAIPA
        self.PC13CODCTG = PC13CODCTG
        self.PC13CODGMD = PC13CODGMD
        self.PC13CODCGE = PC13CODCGE
        self.PC13CODSCL = PC13CODSCL
        self.PC13GESCOR = PC13GESCOR
        self.PC13CLASS = PC13CLASS
        self.PC13DESPLA = PC13DESPLA
        self.PC13DESFAT = PC13DESFAT
        self.PC13GRADE = PC13GRADE
        self.PC13FORMA = PC13FORMA
        self.PC13TIPMON = PC13TIPMON
        self.PC13NBM = PC13NBM
        self.PC13PESBRU = PC13PESBRU
        self.PC13PESLIQ = PC13PESLIQ
        self.PC13ALTSAL = PC13ALTSAL
        self.PC13COMMOD = PC13COMMOD
        self.PC13ALTMOD = PC13ALTMOD
        self.PC13LARMOD = PC13LARMOD
        self.PC13VRUNIT = PC13VRUNIT
        self.PC13ALTSLN = PC13ALTSLN

    def to_dict(self):
        return {
            'codModelo': self.PC13CODIGO,
            'modAnoPed':self.PC13ANOPED,
            'modPed': self.PC13CODPED,
            'codCor': self.PC13COR,
            'empresa': self.PC13EMP08,
            'codCol': self.PC13CODCOL,
            'codLan': self.PC13CODLAN,
            'codClassItem': self.PC13CLAITE,
            'codClasItemPA': self.PC13CLAIPA,
            'codCategoriaGestor': self.PC13CODCTG,
            'codGrupoGestor': self.PC13CODGMD,
            'codClasGestor': self.PC13CODCGE,
            'codSubClassifGestor': self.PC13CODSCL,
            'codCorGestor': self.PC13GESCOR,
            'codClassDeModelo': self.PC13CLASS,
            'descPlanejamento': self.PC13DESPLA,
            'descFaturamento': self.PC13DESFAT,
            'codGrade': self.PC13GRADE,
            'forma': self.PC13FORMA,
            'marca': self.PC13TIPMON,
            'NCM': self.PC13NBM,
            'classificacao': self.PC13CLASS,
            'pesoBruto': self.PC13PESBRU,
            'pesoLiquido': self.PC13PESLIQ,
            'alturaSalto': self.PC13ALTSAL,
            'comprimento': self.PC13COMMOD,
            'altura': self.PC13ALTMOD,
            'largura': self.PC13LARMOD,
            'vrCusto': self.PC13VRUNIT,
            'alturaNovo': self.PC13ALTSLN,
            'tipMontagem': self.PC13TIPMON
        }










