from flask import session, render_template, request, jsonify
from flask_login import login_required
from ..models import Permission, Role, Customer, MailTemplet, MailTemplet_Path, MailTemplet_Path_Temp, \
    Cutover_Path_Temp, TransferOrders, FILE_URL
from ..decorators import permission_required, permission
from .. import logger, db
from . import main
from app.proccessing_data.proccess.public_methods import upload_fdfs, new_data_obj
import datetime
from app.MyModule.SendMail import sendmail


@main.route('/transfer', methods=['GET'])
@login_required
@permission_required(Permission.REGION_SUPPORT)
def transfer():
    return render_template('transfer.html')


@main.route('/transfer_confirm', methods=['GET'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def transfer_confirm():
    return render_template('transfer_confirm.html')


@main.route('/transfer_confirmed', methods=['GET'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def transfer_confirmed():
    return render_template('transfer_confirmed.html')


@main.route('/transfer_confirm_action', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def transfer_confirm_action():
    data = request.json
    id_ = data.get('sc_id')
    action = data.get('action')
    order = TransferOrders.query.get(id_)
    logger.debug(f'User {session["LOGINNAME"]} is deny an apply order {id_} from inside to outside.')

    try:
        # 0 means deny
        order.confirm_result = action
        order.confirm_user_id = session['SELFID']
        order.confirm_at = datetime.datetime.now()
        db.session.add(order)
        db.session.commit()
        logger.info(f'{order.id} is set to {action}')
        download_url = FILE_URL + '/' + order.file_store_path
        mail_content = f"Hello, {session['LOGINUSER']}:\nFilename:\t{order.filename}\nDownload URL:\t{download_url}"
        if action == 1:
            SM = sendmail(subject=order.id + "_" + order.filename, mail_to=order.email)
            SM.send(content=mail_content)
        return jsonify({'status': 'OK', 'content': '操作成功'})
    except Exception as e:
        logger.error('Delete user fail:{}'.format(e))
        return jsonify({'status': 'fail', 'content': '操作失败'})


@main.route('/upload_inside_fdfs', methods=['POST'])
@login_required
@permission_required(Permission.REGION_SUPPORT)
def upload_inside_fdfs():
    return upload_fdfs(request.files.get('file'))


@main.route('/apply_transfer', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.REGION_SUPPORT)
def apply_transfer():
    if not session.get('s_upload_fdfs'):
        return jsonify({'status': 'false', 'content': '未上传文件'})
    filename = session['s_upload_fdfs']['filename']
    file_store_path = session['s_upload_fdfs']['path']
    apply_user = session['SELFID']
    email = session['SELFEMAIL']

    # 获取页面传递的参数
    logger.debug(request.get_json())
    transfer_json = request.get_json()

    new_order = new_data_obj("TransferOrders", **{"filename": filename,
                                                  "file_store_path": file_store_path,
                                                  "apply_user_id": apply_user,
                                                  "apply_reason": transfer_json.get('apply_reason'),
                                                  "email": email})
    try:
        db.session.commit()
        if new_order and new_order['status']:
            session['s_upload_fdfs'] = ""
            return jsonify({'status': 'true', "content": "文件传输申请提交成功"})
        else:
            return jsonify({'status': 'false', "content": "文件传输申请提交失败"})
    except Exception as e:
        db.session.rollback()
        session['s_upload_fdfs'] = ""
        return jsonify({'status': 'false', "content": str(e)})
