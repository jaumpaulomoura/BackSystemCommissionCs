from collections import defaultdict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask import Blueprint, jsonify, request
import pytz
from sqlalchemy import Numeric, String, and_, cast, func, or_
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import aliased
from flask_jwt_extended import get_jwt_identity, jwt_required
from models.colaborador import Colaborador


from models.vwcsEcomPedidosJp import VwcsEcomPedidosJp
from database import db


sales_bp = Blueprint('sales_bp', __name__)

colaborador_alias = aliased(Colaborador)
    
    
 
@sales_bp.route('/ordersByDay', methods=['GET'])
@jwt_required()
def get_orders_by_day():
    current_user = get_jwt_identity()
    cupom_vendedora = request.args.get('cupom_vendedora')
    team_name = request.args.get('team_name')
    month = request.args.get('month')
    year = request.args.get('year')
    local_tz = pytz.timezone('America/Sao_Paulo')
    colaborador_alias = aliased(Colaborador)
    if not month or not year:
        return jsonify({"error": "Parameters 'month' and 'year' are required."}), 400

    try:
        month = int(month)
        year = int(year)
    except ValueError:
        return jsonify({"error": "Invalid 'month' or 'year' format."}), 400

    start_date = datetime(year=year, month=month, day=1)
    end_date = (start_date + relativedelta(months=1)).replace(day=1)
    start_date_local = local_tz.localize(start_date)
    end_date_local = local_tz.localize(end_date)
    
    start_date_utc = start_date_local.astimezone(pytz.utc)
    end_date_utc = end_date_local.astimezone(pytz.utc)
    response_data = []
    if cupom_vendedora:
        results = (
            db.session.query(
                VwcsEcomPedidosJp.cupom_vendedora,
                func.to_char(VwcsEcomPedidosJp.data_submissao, 'YYYY-MM-DD').label('day'),
                 (
                        func.sum(
                            cast(
                                func.regexp_replace(VwcsEcomPedidosJp.valor_pago, ',', '.', 'g'),
                                Numeric
                            )
                        ) - func.sum(
                            cast(
                                func.regexp_replace(VwcsEcomPedidosJp.valor_frete, ',', '.', 'g'),
                                Numeric
                            )
                        )
                    ).label('total_valor_bruto'),
                 colaborador_alias.nome.label('nome')
            )
            .join(colaborador_alias, colaborador_alias.cupom == VwcsEcomPedidosJp.cupom_vendedora)
            .filter(
                and_(
                    VwcsEcomPedidosJp.data_submissao >= start_date_utc,
                    VwcsEcomPedidosJp.data_submissao < end_date_utc,
                    VwcsEcomPedidosJp.cupom_vendedora == cupom_vendedora,
                    VwcsEcomPedidosJp.status == 'APROVADO'
                )
            )
            .group_by(VwcsEcomPedidosJp.cupom_vendedora, func.to_char(VwcsEcomPedidosJp.data_submissao, 'YYYY-MM-DD'),colaborador_alias.nome)
            .all()
        )

    elif team_name:
        try:
            collaborators = Colaborador.query.filter_by(time=team_name).all()
            cupons = [colaborador.cupom for colaborador in collaborators]

            if not cupons:
                return jsonify({"error": "No coupons found for the specified team."}), 404

            results = (
                db.session.query(
                    VwcsEcomPedidosJp.cupom_vendedora,
                    func.to_char(VwcsEcomPedidosJp.data_submissao, 'YYYY-MM-DD').label('day'),
                     (
                        func.sum(
                            cast(
                                func.regexp_replace(VwcsEcomPedidosJp.valor_pago, ',', '.', 'g'),
                                Numeric
                            )
                        ) - func.sum(
                            cast(
                                func.regexp_replace(VwcsEcomPedidosJp.valor_frete, ',', '.', 'g'),
                                Numeric
                            )
                        )
                    ).label('total_valor_bruto'),
                     colaborador_alias.nome.label('nome')
                     
                )
                .join(colaborador_alias, colaborador_alias.cupom == VwcsEcomPedidosJp.cupom_vendedora)
                .filter(
                    and_(
                        VwcsEcomPedidosJp.data_submissao >= start_date_utc,
                        VwcsEcomPedidosJp.data_submissao < end_date_utc,
                        VwcsEcomPedidosJp.cupom_vendedora.in_(cupons),
                        VwcsEcomPedidosJp.status == 'APROVADO'
                    )
                )
                .group_by(VwcsEcomPedidosJp.cupom_vendedora, func.to_char(VwcsEcomPedidosJp.data_submissao, 'YYYY-MM-DD'),colaborador_alias.nome)
                .all()
            )
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
            
            results = (
                db.session.query(
                    VwcsEcomPedidosJp.cupom_vendedora,
                    func.to_char(VwcsEcomPedidosJp.data_submissao, 'YYYY-MM-DD').label('day'),
                     (
                        func.sum(
                            cast(
                                func.regexp_replace(VwcsEcomPedidosJp.valor_pago, ',', '.', 'g'),
                                Numeric
                            )
                        ) - func.sum(
                            cast(
                                func.regexp_replace(VwcsEcomPedidosJp.valor_frete, ',', '.', 'g'),
                                Numeric
                            )
                        )
                    ).label('total_valor_bruto'),
                     colaborador_alias.nome.label('nome')
                     
                )
                .join(colaborador_alias, colaborador_alias.cupom == VwcsEcomPedidosJp.cupom_vendedora)
                .filter(
                    and_(
                        VwcsEcomPedidosJp.data_submissao >= start_date_utc,
                        VwcsEcomPedidosJp.data_submissao < end_date_utc,
                        VwcsEcomPedidosJp.status == 'APROVADO'
                    )
                )
                .group_by(VwcsEcomPedidosJp.cupom_vendedora, func.to_char(VwcsEcomPedidosJp.data_submissao, 'YYYY-MM-DD'),colaborador_alias.nome)
                .all()
            )

    response_data = [
        {"nome":row.nome,
            "cupom_vendedora": row.cupom_vendedora,
            "day_month_year": row.day,
            "valor_bruto": row.total_valor_bruto
        }
        for row in results
    ]

    return jsonify(response_data), 200
@sales_bp.route('/ordersByMonth', methods=['GET'])
@jwt_required()
def get_orders_by_month():
    cupom_vendedora = request.args.get('cupom_vendedora')
    team_name = request.args.get('team_name')
    month = request.args.get('month')
    year = request.args.get('year')
    
    local_tz = pytz.timezone('America/Sao_Paulo')
    colaborador_alias = aliased(Colaborador)
    if not month or not year:
        return jsonify({"error": "Parameters 'month' and 'year' are required."}), 400

    try:
        month = int(month)
        year = int(year)
    except ValueError:
        return jsonify({"error": "Invalid 'month' or 'year' format."}), 400

    start_date = datetime(year=year, month=month, day=1)
    end_date = (start_date + relativedelta(months=1)).replace(day=1)
    start_date_local = local_tz.localize(start_date)
    end_date_local = local_tz.localize(end_date)
    
    start_date_utc = start_date_local.astimezone(pytz.utc)
    end_date_utc = end_date_local.astimezone(pytz.utc)
    response_data = []

    if cupom_vendedora:
        results = (
            db.session.query(
                VwcsEcomPedidosJp.cupom_vendedora,
                func.to_char(VwcsEcomPedidosJp.data_submissao, 'YYYY-MM').label('month_year'),
                 (
                        func.sum(
                            cast(
                                func.regexp_replace(VwcsEcomPedidosJp.valor_pago, ',', '.', 'g'),
                                Numeric
                            )
                        ) - func.sum(
                            cast(
                                func.regexp_replace(VwcsEcomPedidosJp.valor_frete, ',', '.', 'g'),
                                Numeric
                            )
                        )
                    ).label('total_valor_bruto'),
                     colaborador_alias.nome.label('nome')
            )
            .join(colaborador_alias, colaborador_alias.cupom == VwcsEcomPedidosJp.cupom_vendedora)
            .filter(
                and_(
                    VwcsEcomPedidosJp.data_submissao >= start_date_utc,
                    VwcsEcomPedidosJp.data_submissao < end_date_utc,
                    VwcsEcomPedidosJp.cupom_vendedora == cupom_vendedora,
                    VwcsEcomPedidosJp.status == 'APROVADO'
                )
            )
            .group_by(VwcsEcomPedidosJp.cupom_vendedora, func.to_char(VwcsEcomPedidosJp.data_submissao, 'YYYY-MM'),colaborador_alias.nome)
            .all()
        )

    elif team_name:
        try:
            collaborators = Colaborador.query.filter_by(time=team_name).all()
            cupons = [colaborador.cupom for colaborador in collaborators]

            if not cupons:
                return jsonify({"error": "No coupons found for the specified team."}), 404

            results = (
                db.session.query(
                    VwcsEcomPedidosJp.cupom_vendedora,
                    func.to_char(VwcsEcomPedidosJp.data_submissao, 'YYYY-MM').label('month_year'),
                     (
                        func.sum(
                            cast(
                                func.regexp_replace(VwcsEcomPedidosJp.valor_pago, ',', '.', 'g'),
                                Numeric
                            )
                        ) - func.sum(
                            cast(
                                func.regexp_replace(VwcsEcomPedidosJp.valor_frete, ',', '.', 'g'),
                                Numeric
                            )
                        )
                    ).label('total_valor_bruto'),
                     colaborador_alias.nome.label('nome')
                )
                .join(colaborador_alias, colaborador_alias.cupom == VwcsEcomPedidosJp.cupom_vendedora)
                .filter(
                    and_(
                        VwcsEcomPedidosJp.data_submissao >= start_date_utc,
                        VwcsEcomPedidosJp.data_submissao < end_date_utc,
                        VwcsEcomPedidosJp.cupom_vendedora.in_(cupons),
                        VwcsEcomPedidosJp.status == 'APROVADO'
                    )
                )
                .group_by(VwcsEcomPedidosJp.cupom_vendedora, func.to_char(VwcsEcomPedidosJp.data_submissao, 'YYYY-MM'),colaborador_alias.nome)
                .all()
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        results = (
                db.session.query(
                    VwcsEcomPedidosJp.cupom_vendedora,
                    func.to_char(VwcsEcomPedidosJp.data_submissao, 'YYYY-MM').label('month_year'),
                     (
                        func.sum(
                            cast(
                                func.regexp_replace(VwcsEcomPedidosJp.valor_pago, ',', '.', 'g'),
                                Numeric
                            )
                        ) - func.sum(
                            cast(
                                func.regexp_replace(VwcsEcomPedidosJp.valor_frete, ',', '.', 'g'),
                                Numeric
                            )
                        )
                    ).label('total_valor_bruto'),
                     colaborador_alias.nome.label('nome')
                )
                .join(colaborador_alias, colaborador_alias.cupom == VwcsEcomPedidosJp.cupom_vendedora)
                .filter(
                    and_(
                        VwcsEcomPedidosJp.data_submissao >= start_date_utc,
                        VwcsEcomPedidosJp.data_submissao < end_date_utc,
                        VwcsEcomPedidosJp.status == 'APROVADO'
                    )
                )
                .group_by(VwcsEcomPedidosJp.cupom_vendedora, func.to_char(VwcsEcomPedidosJp.data_submissao, 'YYYY-MM'),colaborador_alias.nome)
                .all()
            )

    response_data = [
        {"nome":row.nome,
            "cupom_vendedora": row.cupom_vendedora,
            "month_year": row.month_year,
            "valor_bruto": row.total_valor_bruto
        }
        for row in results
    ]

    return jsonify(response_data), 200


