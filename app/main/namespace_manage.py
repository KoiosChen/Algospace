from flask import session, render_template, request, jsonify
from flask_login import login_required
from ..models import Permission, PermitNamespace, PermitApp, NameSpaces, Apps, BundleConfigs, result_dict, Users
from ..decorators import permission_required
from .. import logger, db, mailbox, socketio
from . import main
from ..proccessing_data.public_methods import upload_fdfs, new_data_obj, get_table_data_by_id, get_table_data
import datetime
from ..MyModule.SendMail import sendmail
from ..main.mattermost import bot_hook
from collections import defaultdict


@main.route('/namespace_manage', methods=['GET'])
@login_required
@permission_required(Permission.USER)
def namespace_manage():
    return render_template('namespace_manage.html')


@main.route('/load_namespace_table', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def load_namespace_table():
    """
                {data: "namespace"},
                {data: "owner"},
                {data: "related_strategies"}
        Returns:

        """
    args = defaultdict(dict)
    if request.form.get('namespace_id'):
        args['search']['id'] = request.form.get('namespace_id')

    lines = get_table_data(NameSpaces, args, appends=['owner', 'related_strategies'])

    result = [{"DT_RowId": "row_" + l['id'],
               "namespace": l.get('name'),
               "owner": l.get('owner', ""),
               "related_strategies": l.get('related_strategies', ""),
               } for l in lines['records']]

    logger.info('Making namespace table')

    return jsonify({
        "draw": int(request.form.get('draw')),
        "recordsTotal": len(result),
        "recordsFiltered": len(result),
        "data": result,
        "options": [],
        "files": []
    })


@main.route('/load_namespace', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def load_namespace():
    args = defaultdict(dict)
    request_json = request.get_json()

    lines = get_table_data(NameSpaces, args, appends=['owner_id', 'related_strategies'], advance_search=[
        {"key": "id", "operator": "__eq__", "value": request_json.get('namespace_id').split('_')[-1]}])

    logger.info('got namespace data')

    return jsonify({"status": "OK", "content": lines})


@main.route('/update_namespace', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def update_namespace():
    args = request.get_json()
    namespace_id = args.get('namespace_id').split('_')[-1]
    new_namespace_name = args.get('name')
    owner_ids = args.get('owners')
    if namespace_id:
        namespace_obj = NameSpaces.query.get(namespace_id)
        if new_namespace_name != namespace_obj.name:
            namespace_obj.name = new_namespace_name
    else:
        namespace_obj = new_data_obj(NameSpaces, **{"name": new_namespace_name})
        if not namespace_obj['status']:
            return jsonify({"status": "FAIL", "content": "Namespace 已存在"})
        namespace_id = namespace_obj['obj'].id

    present_permit_list = PermitNamespace.query.filter_by(namespace_id=namespace_id).all()
    for p in present_permit_list:
        db.session.delete(p)

    for user_id in owner_ids:
        new_data_obj(PermitNamespace,
                     **{"user_id": user_id,
                        "namespace_id": namespace_id,
                        "permission": "0x02"})

    result = "更新成功"

    return jsonify({"status": "OK", "content": result})
