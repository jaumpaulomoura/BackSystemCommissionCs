from database import db
from datetime import  datetime
class Ticket(db.Model):
    __tablename__ = 'ticket'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orderId = db.Column('orderid', db.String(255), nullable=False)
    octadeskId = db.Column('octadeskid', db.String(255), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.String(300))
    status = db.Column(db.String(100), nullable=False)
    cupomvendedora = db.Column(db.String(100), nullable=False)
    dateCreated = db.Column('datecreated', db.Date, default=datetime.utcnow, nullable=False)
    dateUpdated = db.Column('dateupdated', db.Date, onupdate=datetime.utcnow)

    def __init__(self, orderId, octadeskId, reason,cupomvendedora, notes=None, status='Aberto', dateCreated=None, dateUpdated=None):
        self.orderId = orderId
        self.octadeskId = octadeskId
        self.reason = reason
        self.notes = notes
        self.status = status
        self.cupomvendedora = cupomvendedora
        self.dateCreated = dateCreated if dateCreated is not None else datetime.utcnow().date()
        self.dateUpdated = dateUpdated

    def to_dict(self):
        return {
            'id': self.id,
            'orderId': self.orderId,
            'octadeskId': self.octadeskId,
            'reason': self.reason,
            'notes': self.notes,
            'status': self.status,
            'cupomvendedora': self.cupomvendedora,
            'dateCreated': self.dateCreated.isoformat() if self.dateCreated else None,
            'dateUpdated': self.dateUpdated.isoformat() if self.dateUpdated else None
        }
        