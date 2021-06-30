from flask import request, jsonify, session
from flask_login import login_required
from ..models import Permission, TransferOrders, FILE_URL
from ..decorators import permission_required
from . import main
from sqlalchemy import or_


@main.route('/transfer_orders', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.REGION_SUPPORT)
def transfer_orders():
    if request.method == 'POST':
        page_start = (int(request.form.get('datatable[pagination][page]', '0')) - 1) * 10
        length = int(request.form.get('datatable[pagination][perpage]'))

        data = [{'id': order.id,
                 'filename': order.filename,
                 'apply_user': order.apply_user.username if order.apply_user else '',
                 'apply_reason': order.apply_reason,
                 'file_store_path': FILE_URL + '/' + order.file_store_path,
                 'email': order.email,
                 'apply_at': order.apply_at,
                 'confirm_user': order.confirm_user.username if order.confirm_user else '',
                 'confirm_result': order.confirm_result,
                 'confirm_reason': order.confirm_reason,
                 'confirm_at': order.confirm_at
                 }
                for order in
                TransferOrders.query.filter(TransferOrders.apply_user_id.__eq__(session['SELFID'])).order_by(
                    TransferOrders.apply_at.desc()).offset(page_start).limit(length)]

        recordsTotal = TransferOrders.query.count()

        rest = {
            "meta": {
                "page": int(request.form.get('datatable[pagination][page]')),
                "pages": int(recordsTotal) / int(length),
                "perpage": int(length),
                "total": int(recordsTotal),
                "sort": "asc",
                "field": "ShipDate"
            },
            "data": data
        }
        return jsonify(rest)


@main.route('/transfer_confirm_orders', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def transfer_confirm_orders():
    if request.method == 'POST':
        page_start = (int(request.form.get('datatable[pagination][page]', '0')) - 1) * 10
        length = int(request.form.get('datatable[pagination][perpage]'))

        data = [{'id': order.id,
                 'filename': order.filename,
                 'apply_user': order.apply_user.username if order.apply_user else '',
                 'apply_reason': order.apply_reason,
                 'file_store_path': FILE_URL + '/' + order.file_store_path,
                 'email': order.email,
                 'apply_at': order.apply_at,
                 'confirm_user': order.confirm_user.username if order.confirm_user else '',
                 'confirm_result': order.confirm_result,
                 'confirm_reason': order.confirm_reason,
                 'confirm_at': order.confirm_at
                 }
                for order in
                TransferOrders.query.filter(TransferOrders.confirm_result.__eq__(None)).order_by(
                    TransferOrders.apply_at.desc()).offset(page_start).limit(length)]

        recordsTotal = TransferOrders.query.count()

        rest = {
            "meta": {
                "page": int(request.form.get('datatable[pagination][page]')),
                "pages": int(recordsTotal) / int(length),
                "perpage": int(length),
                "total": int(recordsTotal),
                "sort": "asc",
                "field": "ShipDate"
            },
            "data": data
        }
        return jsonify(rest)
