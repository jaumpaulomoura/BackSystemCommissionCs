from cgitb import text
from flask import Blueprint, jsonify, request, abort
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, text
from models.colaborador import Colaborador
from flask_jwt_extended import jwt_required
from models.ticket import Ticket
from database import db

ticket_bp = Blueprint('ticket_bp', __name__)

@ticket_bp.route('/ticket', methods=['GET'], strict_slashes=False)
# @jwt_required() 
def consultar_ticket():
    try:
        cupom_vendedora = request.args.get('cupomvendedora')
        time_colaborador = request.args.get('time')

        query = db.session.query(Ticket, Colaborador.nome).outerjoin(
            Colaborador, 
            and_(
                Ticket.cupomvendedora == Colaborador.cupom,
                Colaborador.dtadmissao <= Ticket.dateCreated,
                Colaborador.dtdemissao >= Ticket.dateCreated
            )
        )


        if cupom_vendedora:
            query = query.filter(Ticket.cupomvendedora == cupom_vendedora)

        if time_colaborador:
            colaboradores = Colaborador.query.filter_by(time=time_colaborador).all()
            cupoms = [colaborador.cupom for colaborador in colaboradores]
            query = query.filter(Ticket.cupomvendedora.in_(cupoms))

        tickets = query.all()

        results_col = []
        for ticket, nome in tickets:
            results_col.append({
                'id': ticket.id,
                'orderId': ticket.orderId,
                'octadeskId': ticket.octadeskId,
                'reason': ticket.reason,
                'notes': ticket.notes,
                'status': ticket.status,
                'cupomvendedora': ticket.cupomvendedora,
                'dateCreated': ticket.dateCreated.isoformat() if ticket.dateCreated else None,
                'dateUpdated': ticket.dateUpdated.isoformat() if ticket.dateUpdated else None,
                'nome': nome 
            })

        response = jsonify(results_col)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except Exception as e:
        print(f"Error occurred: {str(e)}")  
        return jsonify({'error': 'Erro na consulta SQL', 'details': str(e)}), 500

@ticket_bp.route('/ticket', methods=['POST'])
@jwt_required()
def create_ticket():
    data = request.get_json()

    order_id = data.get('orderId')
    octadesk_id = data.get('octadeskId')
    reason = data.get('reason')
    notes = data.get('notes')
    status = data.get('status', 'Aberto') 
    cupomvendedora = data.get('cupomvendedora')

    try:
        new_ticket = Ticket(
            orderId=order_id,
            octadeskId=octadesk_id,
            reason=reason,
            notes=notes,
            status=status,
            cupomvendedora=cupomvendedora
        )
        db.session.add(new_ticket)
        db.session.commit()
        return jsonify({'message': 'Ticket criado com sucesso'}), 200
    except Exception as e:
        print(f"Erro ao criar ticket: {e}")
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar ticket'}), 500



@ticket_bp.route('/ticket', methods=['DELETE'])
@jwt_required()
def delete_ticket():
    ticket_id = request.args.get('id')

    if not ticket_id:
        return jsonify({'error': 'ID do ticket é necessário'}), 400

    try:
        ticket = Ticket.query.filter_by(id=ticket_id).first()

        if not ticket:
            return jsonify({'error': 'Ticket não encontrado'}), 404

        db.session.delete(ticket)
        db.session.commit()
        return jsonify({'message': 'Ticket deletado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao deletar ticket: {e}")
        return jsonify({'error': 'Erro ao deletar ticket'}), 500

@ticket_bp.route('/ticket/<int:id>', methods=['PUT'])
@jwt_required()
def update_ticket(id):
    data = request.get_json()

    order_id = data.get('orderId')
    octadesk_id = data.get('octadeskId')
    reason = data.get('reason')
    notes = data.get('notes')
    status = data.get('status')
    cupomvendedora = data.get('cupomvendedora')

    try:
        ticket = Ticket.query.filter_by(id=id).first()

        if not ticket:
            return jsonify({'error': 'Ticket não encontrado'}), 404

        if order_id is not None:
            ticket.orderId = order_id
        if octadesk_id is not None:
            ticket.octadeskId = octadesk_id
        if reason is not None:
            ticket.reason = reason
        if notes is not None:
            ticket.notes = notes
        if status is not None:
            ticket.status = status
        if cupomvendedora is not None:
            ticket.cupomvendedora = cupomvendedora

        ticket.dateUpdated = datetime.utcnow()

        db.session.commit()

        return jsonify({'message': 'Ticket atualizado com sucesso'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar ticket: {e}")
        return jsonify({'error': 'Erro ao atualizar ticket'}), 500



@ticket_bp.route('/ticket/update-cupom', methods=['PUT'])
@jwt_required()
def update_coupon():
    data = request.get_json()


    order_id = data.get('order_id')
    novo_cupom = data.get('novo_cupom')

    if not order_id or not novo_cupom:
        return jsonify({'error': 'order_id e novo_cupom são obrigatórios'}), 400

    try:
        sql = text(
            "CALL vwcs_ecom_atualizar_pedido_vendedora(:order_id, :novo_cupom)"
        )

        db.session.execute(sql, {'order_id': order_id, 'novo_cupom': novo_cupom})
        db.session.commit()
        
        return jsonify({'message': 'Atualização bem-sucedida'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        error_msg = str(e._dict_.get('orig', str(e)))
        return jsonify({'error': f'Erro ao atualizar ticket: {error_msg}'}), 500


@ticket_bp.route('/ticket/update-status', methods=['PUT'])
@jwt_required()
def update_status():
    data = request.get_json()


    order_id = data.get('order_id')
    novo_status = data.get('novo_status')

    if not order_id or not novo_status:
        return jsonify({'error': 'order_id e novo_status são obrigatórios'}), 400

    try:
        sql = text(
            "CALL vwcs_ecom_atualizar_status_pedido_vendedora(:order_id, :novo_status)"
        )

        db.session.execute(sql, {'order_id': order_id, 'novo_status': novo_status})
        db.session.commit()
        
        return jsonify({'message': 'Atualização bem-sucedida'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        error_msg = str(e._dict_.get('orig', str(e)))
        return jsonify({'error': f'Erro ao atualizar ticket: {error_msg}'}), 500
