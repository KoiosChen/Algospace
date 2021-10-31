from flask import request, jsonify, session
from flask_login import login_required
from ..models import Permission, NameSpaces, AppGroups, Apps, Users, PermitApp, PermitAppGroup, BundleConfigs
from ..decorators import permission_required
from . import main
from app import logger, redis_db, db
from app.proccessing_data.make_tables import make_table_config_files
from app.MyModule.prepare_sql import search_sql
from sqlalchemy import and_
import yaml
import json
from collections import defaultdict
from app.proccessing_data.public_methods import new_data_obj, get_table_data_by_id, get_table_data


@main.route('/bundle_config_file_table', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def bundle_config_file_table():
    logger.info('To make table')
    data = make_table_config_files(config_file_id=request.form.get('configs_select'), key_id=request.form.get('key_id'))

    return jsonify({
        "draw": int(request.form.get('draw')),
        "recordsTotal": 1,
        "recordsFiltered": 1,
        "data": data,
        "options": [],
        "files": []
    })


@main.route('/new_app', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def new_app():
    args = request.get_json()
    app_group_id = args.get('app_group_id').split("_")[-1]
    new_app_name = args.get('new_app_name')
    new_one = new_data_obj(Apps, **{"name": new_app_name, "app_group_id": app_group_id})
    new_app_permit = new_data_obj(PermitApp, **{"user_id": session['SELFID'], "app_id": new_one['obj'].id})
    result = "新增成功" if new_one.get('status') else "此实例已存在"
    db.session.commit()
    return jsonify({"status": "OK", "content": result})


@main.route('/get_app_info', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.USER)
def get_app_info():
    if request.method == ['GET']:
        content = get_table_data_by_id(Apps, request.args.get("app_id"), appends=['deploy_at'])
        return jsonify({"status": "OK", "content": content})
    else:
        args = dict()
        request_content = request.form
        strategy_group_id = request_content.get('strategy_group_id')
        length = eval(request_content.get('length'))
        if length > 0:
            args['page'] = 'true'
            args['size'] = length
            args['current'] = eval(request_content.get('start')) / length + 1
        args['search'] = {"app_group_id": strategy_group_id.split("_")[-1]}
        lines = get_table_data(Apps, args)
        result = [{"DT_RowId": "row_" + l['id'],
                   "id": l.get('id'),
                   "instance_name": l.get('name'),
                   "latest_version": l.get('version', ""),
                   } for l in lines['records']]
        logger.info('Making bundle config table')

        return jsonify({
            "draw": int(request.form.get('draw')),
            "recordsTotal": lines['total'],
            "recordsFiltered": lines['total'],
            "data": result,
            "options": [],
            "files": []
        })


@main.route('/get_user_list', methods=['GET'])
@login_required
@permission_required(Permission.USER)
def get_user_list():
    try:
        users = Users.query.all()
        result = list()
        for u in users:
            result.append({"id": u.id, "text": u.username})
        return jsonify({"status": "OK", "content": result})
    except Exception as e:
        return jsonify({"status": "OK", "content": []})


@main.route('/get_namespaces', methods=['GET'])
@login_required
@permission_required(Permission.SUPER_OPERATOR)
def get_namespaces():
    try:
        users = NameSpaces.query.all()
        result = list()
        for u in users:
            result.append({"id": u.id, "text": u.name})
        return jsonify({"status": "OK", "content": result})
    except Exception as e:
        return jsonify({"status": "OK", "content": []})


@main.route('/delete_strategy', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def delete_strategy():
    args = request.get_json()
    raise_list = list()
    for arg in args:
        app_group_id = arg.get('DT_RowId').split("_")[-1]
        app_group_obj = AppGroups.query.get(app_group_id)
        if not app_group_obj:
            raise_list.append(f'{arg["strategy_name"]}不存在')
            continue
        if app_group_obj.apps.all():
            raise_list.append(f'{arg["strategy_name"]}存在实例不可删除')
            continue

        permit_obj = PermitAppGroup.query.filter_by(app_group_id=app_group_id).all()
        for po in permit_obj:
            db.session.delete(po)
        db.session.delete(app_group_obj)
        db.session.commit()

    return jsonify({"status": "OK", "content": ";<br>".join(raise_list) if raise_list else "删除成功"})


@main.route('/delete_instance', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def delete_instance():
    args = request.get_json()
    raise_list = list()
    for arg in args:
        app_id = arg.get('DT_RowId').split("_")[-1]
        app_obj = Apps.query.get(app_id)
        if not app_obj:
            raise_list.append(f'{arg["instance_name"]}不存在')
            continue
        if app_obj.bundle_configurations:
            raise_list.append(f'{arg["instance_name"]}存在关联配置文件不可删除')
            continue

        permit_obj = PermitApp.query.filter_by(app_id=app_id).all()
        for po in permit_obj:
            db.session.delete(po)
        db.session.delete(app_obj)
        db.session.commit()

    return jsonify({"status": "OK", "content": ";<br>".join(raise_list) if raise_list else "删除成功"})


@main.route('/delete_file', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def delete_file():
    args = request.get_json()
    raise_list = list()
    for arg in args:
        bundle_config_file_id = arg.get('DT_RowId').split("_")[-1]
        bundle_config_obj = BundleConfigs.query.get(bundle_config_file_id)
        if not bundle_config_obj:
            raise_list.append(f'{arg["instance_name"]}不存在')
            continue

        db.session.delete(bundle_config_obj)
        db.session.commit()

    return jsonify({"status": "OK", "content": ";<br>".join(raise_list) if raise_list else "删除成功"})
