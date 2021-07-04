from flask import request, jsonify, session
from flask_login import login_required
from ..models import Permission, TransferOrders, FILE_URL, Roles, Users
from ..decorators import permission_required
from . import main
from app import logger
from app.proccessing_data.make_tables import make_table_transfer_orders, make_table_confirm_transfer_orders
from app.MyModule.prepare_sql import search_sql
from sqlalchemy import and_


@main.route('/transfer_orders', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def transfer_orders():
    records_total, search_result = search_sql(request.form, TransferOrders.apply_user_id.__eq__(session['SELFID']))
    logger.info('Making transfer_orders table')
    data = make_table_transfer_orders(lines=search_result)

    return jsonify({
        "draw": int(request.form.get('draw')),
        "recordsTotal": records_total,
        "recordsFiltered": records_total,
        "data": data,
        "options": [],
        "files": []
    })


@main.route('/transfer_confirm_orders', methods=['POST'])
@login_required
@permission_required(Permission.OPERATOR)
def transfer_confirm_orders():
    if Roles.query.get(Users.query.get(session['SELFID']).role_id).name != 'Administrator':
        advance = and_(TransferOrders.confirm_result.__eq__(None), TransferOrders.apply_user_id.__ne__(session['SELFID']))
    else:
        advance = TransferOrders.confirm_result.__eq__(None)
    records_total, search_result = search_sql(request.form, advance)
    logger.info('To make table')
    data = make_table_confirm_transfer_orders(lines=search_result)

    return jsonify({
        "draw": int(request.form.get('draw')),
        "recordsTotal": records_total,
        "recordsFiltered": records_total,
        "data": data,
        "options": [],
        "files": []
    })


@main.route('/transfer_confirmed_orders', methods=['POST'])
@login_required
@permission_required(Permission.OPERATOR)
def transfer_confirmed_orders():
    if Roles.query.get(Users.query.get(session['SELFID']).role_id).name != 'Administrator':
        advance = and_(TransferOrders.confirm_result.__ne__(None), TransferOrders.apply_user_id.__ne__(session['SELFID']))
    else:
        advance = TransferOrders.confirm_result.__ne__(None)
    records_total, search_result = search_sql(request.form, advance)
    data = make_table_confirm_transfer_orders(lines=search_result)

    return jsonify({
        "draw": int(request.form.get('draw')),
        "recordsTotal": records_total,
        "recordsFiltered": records_total,
        "data": data,
        "options": [],
        "files": []
    })
