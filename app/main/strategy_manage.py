from flask import session, render_template, request, jsonify
from flask_login import login_required
from ..models import Permission, PermitNamespace, PermitApp, NameSpaces, Apps, PermitAppGroup, result_dict, AppGroups
from ..decorators import permission_required
from .. import logger, db, mailbox, socketio
from . import main
from ..proccessing_data.public_methods import upload_fdfs, new_data_obj, get_table_data_by_id, get_table_data
import datetime
from collections import defaultdict
import os


@main.route('/strategy_manage', methods=['GET'])
@login_required
@permission_required(Permission.USER)
def strategy_manage():
    return render_template('strategy_manage.html')


@main.route('/load_strategy_table', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def load_strategy_table():
    """
        {data: "strategy_name"},
        {data: "namespace"},
        {data: "version"},
        {data: "local_path"},
        {data: "owner"}

    """
    args = defaultdict(dict)
    if request.form.get('strategy_id'):
        args['search']['id'] = request.form.get('strategy_id')

    lines = get_table_data(AppGroups, args, appends=['owner', 'related_namespaces'])

    result = [{"DT_RowId": "row_" + l['id'],
               "strategy_name": l.get('name'),
               "namespace": l.get('related_namespaces', ""),
               "local_path": l.get('local_path', ""),
               "dryrun_path": l.get('dryrun_path', ""),
               "strategy_desc": l.get("desc", ""),
               "owner": l.get('owner', ""),
               } for l in lines['records']]

    logger.info('Making strategy table')

    return jsonify({
        "draw": int(request.form.get('draw')),
        "recordsTotal": len(result),
        "recordsFiltered": len(result),
        "data": result,
        "options": [],
        "files": []
    })


@main.route('/load_strategy', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def load_strategy():
    args = defaultdict(dict)
    request_json = request.get_json()

    lines = get_table_data(AppGroups, args, appends=['owner_id', 'related_namespace_id'], advance_search=[
        {"key": "id", "operator": "__eq__", "value": request_json.get('strategy_id').split('_')[-1]}])

    logger.info(f'got strategy data {lines}')

    return jsonify({"status": "OK", "content": lines})


@main.route('/update_strategy', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def update_strategy():
    """
    let name = $("#new_strategy_name").val()
    let owners = $("#m_select2_owners").val()
    let strategy_id = $("#tmp_strategy_id").val()
    let desc = $("#desc").val()
    let local_path = $("#local_path").val()
    Returns:

    """
    args = request.get_json()
    strategy_id = args.get('strategy_id').split('_')[-1]
    new_strategy_name = args.get('name')
    owner_ids = args.get('owners')
    desc = args.get('desc')
    local_path = args.get('local_path')
    dryrun_path = args.get('dryrun_path')
    namespace_id = args.get('namespace_id')

    namespace = NameSpaces.query.get(namespace_id)

    if strategy_id:
        strategy_obj = AppGroups.query.get(strategy_id)
        if new_strategy_name != strategy_obj.name:
            strategy_obj.name = new_strategy_name

        if strategy_obj.related_namespaces and strategy_obj.related_namespaces[0] != namespace:
            strategy_obj.related_namespaces.remove(strategy_obj.related_namespaces[0])
            namespace.app_groups.append(strategy_obj)
        elif not strategy_obj.related_namespaces:
            namespace.app_groups.append(strategy_obj)
        strategy_obj.desc = desc
        if not os.path.exists(local_path):
            return jsonify({"status": "FAIL", "content": "Local path 不存在"})

        strategy_obj.local_path = local_path
        strategy_obj.dryrun_path = dryrun_path
    else:
        strategy_obj = new_data_obj(AppGroups, **{"name": new_strategy_name})
        if not strategy_obj['status']:
            return jsonify({"status": "FAIL", "content": "Strategy 已存在"})
        strategy_id = strategy_obj['obj'].id
        strategy_obj['obj'].desc = desc
        strategy_obj['obj'].local_path = local_path
        strategy_obj['obj'].dryrun_path = dryrun_path
        namespace.app_groups.append(strategy_obj['obj'])

    present_permit_list = PermitAppGroup.query.filter_by(app_group_id=strategy_id).all()
    for p in present_permit_list:
        db.session.delete(p)

    for user_id in owner_ids:
        new_data_obj(PermitAppGroup,
                     **{"user_id": user_id,
                        "app_group_id": strategy_id,
                        "permission": "0x02"})

    result = "更新成功"
    db.session.commit()

    return jsonify({"status": "OK", "content": result})
