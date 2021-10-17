from flask import session, render_template, request, jsonify
from flask_login import login_required
from ..models import Permission, PermitNamespace, PermitApp, NameSpaces, Apps, BundleConfigs, result_dict, \
    PermitAppGroup, Users
from ..decorators import permission_required
from .. import logger, db, mailbox, socketio
from . import main
from ..proccessing_data.public_methods import upload_fdfs, new_data_obj, get_table_data_by_id, get_table_data, \
    download_from_fdfs
import datetime
from ..MyModule.SendMail import sendmail
from ..MyModule.IssueFileOperator import uncompress, delete_expired_config
from ..main.mattermost import bot_hook
import os


@main.route('/manage_config_files', methods=['GET'])
@login_required
@permission_required(Permission.USER)
def manage_config_files():
    permit_namespaces = PermitNamespace.query.filter_by(user_id=session['SELFID']).all()
    namespaces = [(p.permitted_namespace.name, p.namespace_id) for p in permit_namespaces]
    app_groups = [(pag.name, pag.id) for p in permit_namespaces for pag in p.permitted_namespace.app_groups]
    apps = [(a.name, a.id) for p in permit_namespaces for pag in p.permitted_namespace.app_groups for a in pag.apps]

    return render_template('manage_config_files.html',
                           namespaces=namespaces,
                           app_groups=app_groups,
                           apps=apps,
                           configs=[1, 2, 3])


@main.route('/manage_template', methods=['GET'])
@login_required
@permission_required(Permission.USER)
def manage_template():
    return render_template('manage_template.html')


@main.route('/strategy_bundle_deploy', methods=['GET'])
@login_required
@permission_required(Permission.USER)
def strategy_bundle_deploy():
    permit_namespaces = PermitNamespace.query.filter_by(user_id=session['SELFID']).all()
    namespaces = [(p.permitted_namespace.name, p.namespace_id) for p in permit_namespaces]
    app_groups = [(pag.name, pag.id) for p in permit_namespaces for pag in p.permitted_namespace.app_groups]
    apps = [(a.name, a.id) for p in permit_namespaces for pag in p.permitted_namespace.app_groups for a in pag.apps]
    base_path = "/data/hft/"
    return render_template('strategy_bundle_deploy.html', base_path=base_path, namespaces=namespaces,
                           app_groups=app_groups,
                           apps=apps)


@main.route('/strategy_bundle_deploy_issue', methods=['GET'])
@login_required
@permission_required(Permission.USER)
def strategy_bundle_deploy_issue():
    return render_template('strategy_bundle_deploy_issue.html')


@main.route('/submit_bundle_deploy', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.USER)
def submit_bundle_deploy():
    if not session.get('s_upload_fdfs'):
        return jsonify({'status': 'false', 'content': '未上传文件'})
    filename = session['s_upload_fdfs']['filename']
    file_store_path = session['s_upload_fdfs']['path']
    apply_user = session['SELFID']

    # 获取页面传递的参数

    transfer_json = request.get_json()
    logger.debug(f"request json {transfer_json}")

    deploy_reason = transfer_json.get('deploy_reason')
    app_id = transfer_json.get('app_id')
    uncompress_to = transfer_json.get('uncompress_to')

    app_obj = Apps.query.get(app_id)
    if app_obj.configurations:
        max_version = max([c.version for c in app_obj.configurations])
    else:
        max_version = 0

    new_order = new_data_obj(BundleConfigs, **{"filename": filename,
                                               "file_store_path": file_store_path,
                                               "version": max_version + 1,
                                               "apply_user_id": apply_user,
                                               "uncompress_to": uncompress_to,
                                               "deploy_reason": deploy_reason})
    try:
        if new_order and new_order['status']:
            app_obj.bundle_configurations.append(new_order['obj'])
            session['s_upload_fdfs'] = ""
            db.session.commit()
            # bot_hook(BotHook['Transfer Notification'], f"You have a new application from {session['LOGINUSER']}.")
            # socketio.emit('ws_flush_transfer_confirm_order', {'content': 1}, namespace='/algospace')
            return jsonify({'status': 'true', "content": "配置文件发布申请提交成功"})
        else:
            return jsonify({'status': 'false', "content": "配置文件发布申请提交失败"})
    except Exception as e:
        db.session.rollback()
        session['s_upload_fdfs'] = ""
        return jsonify({'status': 'false', "content": str(e)})


@main.route('/load_bundle_config_table', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def load_bundle_config_table():
    """
    {data: "order_id"},
            {data: "filename"},
            {data: "version"},
            {data: "uncompress_to"},
            {data: "apply_at"},
            {data: "confirm_result"},
            {data: "confirm_user"},
            {data: "confirm_at"},
    Returns:

    """
    args = dict()
    request_content = request.form
    user_obj = Users.query.get(session['SELFID'])
    namespace_list = [upn.namespace_id for upn in user_obj.permitted_namespaces]
    strategy_list = [upa.app_group_id for upa in user_obj.permitted_app_groups]

    if request_content:
        lines = get_table_data_by_id(Apps, request_content.get('strategy_id').split("_")[-1], appends=["instances"])
        result = [{"DT_RowId": "row_" + l['id'],
                   "id": l.get('id'),
                   "filename": l.get('filename', ""),
                   "version": l.get('version', ""),
                   "uncompress_to": l.get('uncompress_to', ""),
                   "apply_at": l.get("apply_at"),
                   "issue_user": l.get("issue_user"),
                   "issue_result": result_dict.get(l.get("issue_result", 0)),
                   "issue_at": l.get("issue_at"),
                   } for l in lines['instances']]
    else:
        lines = get_table_data(BundleConfigs, args,
                               appends=['issue_user',
                                        'bundle_config_related_namespace_id',
                                        'bundle_config_related_strategy_id'])
        result = [{"DT_RowId": "row_" + l['id'],
                   "id": l.get('id'),
                   "filename": l.get('filename', ""),
                   "version": l.get('version', ""),
                   "uncompress_to": l.get('uncompress_to', ""),
                   "apply_at": l.get("apply_at"),
                   "issue_user": l.get("issue_user"),
                   "issue_result": result_dict.get(l.get("issue_result", 0)),
                   "issue_at": l.get("issue_at"),
                   } for l in lines['records'] if l['bundle_config_related_strategy_id'] in strategy_list and l[
                      'bundle_config_related_namespace_id'] in namespace_list]



    logger.info('Making bundle config table')

    return jsonify({
        "draw": int(request.form.get('draw')),
        "recordsTotal": len(result),
        "recordsFiltered": len(result),
        "data": result,
        "options": [],
        "files": []
    })


@main.route('/load_bundle_config_table_issue', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def load_bundle_config_table_issue():
    """
            {data: "id"},
            {data: "filename"},
            {data: "uncompress_to"},
            {data: "version"},
            {data: "issued_version"},
            {data: "deploy_reason"},
            {data: "apply_user"},
            {data: "apply_at"}
    Returns:

    """
    args = dict()
    lines = get_table_data(BundleConfigs, args, appends=['apply_user', 'issued_version'],
                           advance_search=[{"key": "status", "operator": "__eq__", "value": 1},
                                           {"key": "issue_result", "operator": "__eq__", "value": None}])

    result = [{"DT_RowId": "row_" + l['id'],
               "id": l.get('id'),
               "filename": l.get('filename', ""),
               "version": l.get('version', ""),
               "issued_version": l.get('issued_version', ""),
               "uncompress_to": l.get('uncompress_to', ""),
               "apply_at": l.get("apply_at"),
               "apply_user": l.get("apply_user"),
               "deploy_reason": l.get("deploy_reason", 0),
               } for l in lines['records']]
    logger.info('Making bundle config table')

    return jsonify({
        "draw": int(request.form.get('draw')),
        "recordsTotal": len(result),
        "recordsFiltered": len(result),
        "data": result,
        "options": [],
        "files": []
    })


@main.route('/config_issue', methods=['POST'])
@login_required
@permission_required(Permission.OPERATOR)
def config_issue():
    try:
        args = request.get_json()
        id = args['id']
        action = args['action']
        config_obj = BundleConfigs.query.get(id)
        if action == 0:
            # deny
            config_obj.issue_result = 0
            config_obj.issue_user_id = session['SELFID']
            config_obj.issue_at = datetime.datetime.now()
            db.session.commit()
            return jsonify({"status": "OK", "content": "已拒绝发布"})
        elif action == 1:
            # accept
            config_obj.issue_result = 1
            config_obj.status = 1
            config_obj.issue_user_id = session['SELFID']
            config_obj.issue_at = datetime.datetime.now()
            target_path = os.path.join('/tmp/', config_obj.filename)
            strategy_obj = config_obj.related_apps[0].app_group
            local_path = strategy_obj.local_path
            uncompress_path = os.path.join(local_path, config_obj.uncompress_to)
            try:
                download_result = download_from_fdfs(target_path, config_obj.file_store_path)
            except Exception as e:
                raise Exception(e)
            if uncompress(target_path, uncompress_path):
                delete_obj = [os.path.join(strategy_obj.base_path, ab.uncompress_to, ab.filename) for ab in
                              strategy_obj.bundle_configurations if ab.version == strategy_obj.version]
                if delete_obj:
                    delete_expired_config(delete_obj[0])
                    db.session.commit()
                    return jsonify({"status": "OK", "content": "文件解压成功"})
                else:
                    # 删除已解压文件
                    return jsonify({"status": "FAIL", "content": "文件删除失败"})
            else:
                return jsonify({"status": "FAIL", "content": "文件解压错误"})
        elif action == 3:
            # dry_run
            pass
        else:
            return jsonify({"status": "FAIL", "content": "操作不存在"})
    except Exception as e:
        return jsonify({"status": "FAIL", "content": str(e)})
