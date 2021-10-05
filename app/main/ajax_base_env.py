from flask import request, jsonify, session
from flask_login import login_required
from ..models import Permission, NameSpaces, AppGroups, Apps, Users, PermitApp
from ..decorators import permission_required
from . import main
from app import logger, redis_db
from app.proccessing_data.make_tables import make_table_config_files
from app.MyModule.prepare_sql import search_sql
from sqlalchemy import and_
import yaml
import json
from collections import defaultdict
from app.proccessing_data.public_methods import new_data_obj, get_table_data_by_id


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
    app_group_id = args.get('app_group_id')
    new_app_name = args.get('new_app_name')
    new_one = new_data_obj(Apps, **{"name": new_app_name, "app_group_id": app_group_id})
    new_data_obj(PermitApp, **{"user_id": session['SELFID'], "app_id": new_one['obj'].id})
    result = "新增成功" if new_one.get('status') else "此实例已存在"
    return jsonify({"status": "OK", "content": result})


@main.route('/get_app_info', methods=['GET'])
@login_required
@permission_required(Permission.USER)
def get_app_info():
    args = request.args.get("app_id")
    content = get_table_data_by_id(Apps, args, appends=['deploy_at'])
    return jsonify({"status": "OK", "content": content})


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