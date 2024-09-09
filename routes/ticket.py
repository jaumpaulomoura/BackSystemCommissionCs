from cgitb import text
from flask import Blueprint, jsonify, request, abort
from models import Colaborador, Ticket
from database import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text


ticket_bp = Blueprint('ticket_bp', __name__)

@ticket_bp.route('/ticket', methods=['GET'], strict_slashes=False)
def consultar_ticket():
    try:
        # Obter o valor do cupomvendedora e time do parâmetro de consulta, se presentes
        cupom_vendedora = request.args.get('cupomvendedora')
        time_colaborador = request.args.get('time')

        query = Ticket.query

        # Filtrar por cupomvendedora se fornecido
        if cupom_vendedora:
            query = query.filter_by(cupomvendedora=cupom_vendedora)

        # Se um filtro de time for fornecido, filtra os colaboradores e usa os cupoms filtrados
        if time_colaborador:
            colaboradores = Colaborador.query.filter_by(time=time_colaborador).all()
            cupoms = [colaborador.cupom for colaborador in colaboradores]
            query = query.filter(Ticket.cupomvendedora.in_(cupoms))

        # Obter todos os tickets com os filtros aplicados
        tickets = query.all()

        # Converter os tickets para dicionários
        results_col = [ticket.to_dict() for ticket in tickets]
        response = jsonify(results_col)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    except Exception as e:
        print(f"Erro na consulta SQL: {e}")
        return jsonify({'error': 'Erro na consulta SQL'}), 500


@ticket_bp.route('/ticket', methods=['POST'])
def create_ticket():
    data = request.get_json()

    order_id = data.get('orderId')
    octadesk_id = data.get('octadeskId')
    reason = data.get('reason')
    notes = data.get('notes')
    status = data.get('status', 'Aberto')  # Default to 'Aberto' if not provided
    cupomvendedora=  data.get('cupomvendedora')

    try:
        # # Verificar duplicidade
        # existing_ticket = Ticket.query.filter(
        #     (Ticket.id == id) & (Ticket.octadeskId == octadesk_id)
        # ).first()

        # if existing_ticket:
        #     return jsonify({'error': 'Ticket já existe para esse pedido e atendimento'}), 409

        # Inserir novo ticket
        new_ticket = Ticket(
            orderId=order_id,
            octadeskId=octadesk_id,
            reason=reason,
            notes=notes,
            status=status,
            cupomvendedora=cupomvendedora
            # dateCreated e dateUpdated são definidos automaticamente
        )
        db.session.add(new_ticket)
        db.session.commit()
        return jsonify({'message': 'Ticket criado com sucesso'}), 200
    except Exception as e:
        print(f"Erro ao criar ticket: {e}")
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar ticket'}), 500

@ticket_bp.route('/ticket', methods=['DELETE'])
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
def update_ticket(id):
    data = request.get_json()

    order_id = data.get('orderId')
    octadesk_id = data.get('octadeskId')
    reason = data.get('reason')
    notes = data.get('notes')
    status = data.get('status')
    cupomvendedora = data.get('cupomvendedora')

    try:
        # Fetch the existing ticket
        ticket = Ticket.query.filter_by(id=id).first()

        if not ticket:
            return jsonify({'error': 'Ticket não encontrado'}), 404

        # Update fields only if provided
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

        # Always update the dateUpdated field
        ticket.dateUpdated = datetime.utcnow()

        db.session.commit()

        return jsonify({'message': 'Ticket atualizado com sucesso'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar ticket: {e}")
        return jsonify({'error': 'Erro ao atualizar ticket'}), 500



@ticket_bp.route('/ticket/update-coupon', methods=['PUT'])
def update_coupon():
    data = request.get_json()

    # Print the received data to the console
    print('Dados recebidos:', data)

    order_id = data.get('order_id')
    novo_cupom = data.get('novo_cupom')

    if not order_id or not novo_cupom:
        return jsonify({'error': 'order_id e novo_cupom são obrigatórios'}), 400

    try:
        # Define the SQL to call the stored procedure
        sql = text(
            "CALL vwcs_ecom_atualizar_pedido_vendedora(:order_id, :novo_cupom)"
        )

        # Execute the stored procedure
        db.session.execute(sql, {'order_id': order_id, 'novo_cupom': novo_cupom})
        db.session.commit()
        
        return jsonify({'message': 'Atualização bem-sucedida'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        error_msg = str(e._dict_.get('orig', str(e)))
        return jsonify({'error': f'Erro ao atualizar ticket: {error_msg}'}), 500
