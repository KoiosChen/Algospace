from flask import session, render_template, request, jsonify
from flask_login import login_required
from ..models import Permission, TransferOrders, FILE_URL, Users, ApplyTypes, Roles, BotHook
from ..decorators import permission_required
from .. import logger, db, mailbox, socketio
from . import main
from ..proccessing_data.public_methods import upload_fdfs, new_data_obj
import datetime
from ..MyModule.SendMail import sendmail
from ..main.mattermost import bot_hook

Search_Fields = [['文件名称', 'filename'],
                 ['申请人', 'apply_user'],
                 ['申请类型', 'apply_type'],
                 ['审核结果', 'confirm_result'],
                 ['审核人', 'confirm_user'],
                 ]


@main.route('/transfer', methods=['GET'])
@login_required
@permission_required(Permission.USER)
def transfer():
    users = Users.query.filter(Users.id.__ne__(session['SELFID'])).all()
    sendto = [[u.username, u.id] for u in users]
    apply_type = [[a.name, a.id] for a in ApplyTypes.query.all()]
    return render_template('transfer.html', sendto_users=sendto, apply_type=apply_type)


@main.route('/transfer_confirm', methods=['GET'])
@login_required
@permission_required(Permission.OPERATOR)
def transfer_confirm():
    return render_template('transfer_confirm.html', search_fields=Search_Fields)


@main.route('/transfer_confirmed', methods=['GET'])
@login_required
@permission_required(Permission.OPERATOR)
def transfer_confirmed():
    return render_template('transfer_confirmed.html', search_fields=Search_Fields)


@main.route('/transfer_confirm_action', methods=['POST'])
@login_required
@permission_required(Permission.OPERATOR)
def transfer_confirm_action():
    data = request.json
    id_ = data.get('sc_id')
    action = data.get('action')
    order = TransferOrders.query.get(id_)
    logger.debug(f'User {session["LOGINNAME"]} action{action} an apply order {id_} from inside to outside.')

    try:
        # 0 means deny
        if Roles.query.get(Users.query.get(session['SELFID']).role_id).name != 'Administrator' \
                and order.apply_user_id == session['SELFID']:
            logger.debug(str(session['ROLE']) + ' ' + str(session['SELFID']))
            return jsonify({'status': 'fail', 'content': '非管理员，不可审核自己的申请'})

        order.confirm_result = action
        order.confirm_user_id = session['SELFID']
        order.confirm_at = datetime.datetime.now()
        db.session.add(order)
        db.session.commit()
        logger.info(f'{order.id} is set to {action}')

        # 若通过， 则发送邮件
        if action == 1:
            download_url = FILE_URL + '/' + order.file_store_path
            mail_content = f"Hello, {order.apply_user.username}:\nFilename:\t{order.filename}\nDownload URL:\t{download_url}"
            send_list = list()
            send_list.append(order.email)
            for share in order.sendto:
                logger.debug(share.email)
                send_list.append(share.email)
            subject = "[Transfer]" + order.filename + "_" + order.id
            mailbox.put({"mail_to": send_list, "subject": subject, "content": mail_content})
        return jsonify({'status': 'OK', 'content': '操作成功'})
    except Exception as e:
        logger.error(f'confirm order {order.id} fail:{str(e)}')
        return jsonify({'status': 'fail', 'content': '操作失败'})


@main.route('/upload_inside_fdfs', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def upload_inside_fdfs():
    return upload_fdfs(request.files.get('file'))


@main.route('/apply_transfer', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.USER)
def apply_transfer():
    if not session.get('s_upload_fdfs'):
        return jsonify({'status': 'false', 'content': '未上传文件'})
    filename = session['s_upload_fdfs']['filename']
    file_store_path = session['s_upload_fdfs']['path']
    apply_user = session['SELFID']
    email = session['SELFEMAIL']

    # 获取页面传递的参数

    transfer_json = request.get_json()
    logger.debug(f"request json {transfer_json}")

    new_order = new_data_obj("TransferOrders", **{"filename": filename,
                                                  "file_store_path": file_store_path,
                                                  "apply_user_id": apply_user,
                                                  "apply_type_id": transfer_json.get('apply_type'),
                                                  "apply_reason": transfer_json.get('apply_reason'),
                                                  "email": email})
    try:
        if new_order and new_order['status']:
            if transfer_json.get('share_to'):
                for id in transfer_json['share_to']:
                    new_order['obj'].sendto.append(Users.query.get(id))
            session['s_upload_fdfs'] = ""
            db.session.commit()
            bot_hook(BotHook['Transfer Notification'], f"You have a new application from {session['LOGINUSER']}.")
            socketio.emit('ws_flush_transfer_confirm_order', {'content': 1}, namespace='/algospace')
            return jsonify({'status': 'true', "content": "文件传输申请提交成功"})
        else:
            return jsonify({'status': 'false', "content": "文件传输申请提交失败"})
    except Exception as e:
        db.session.rollback()
        session['s_upload_fdfs'] = ""
        return jsonify({'status': 'false', "content": str(e)})
