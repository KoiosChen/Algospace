from flask import request, jsonify, session
from flask_login import login_required
from ..models import Permission, NameSpaces, AppGroups, Apps, ConfigFiles, ConfigKeys, PrepareTable, make_uuid
from ..decorators import permission_required
from . import main
from app import logger, redis_db
from app.proccessing_data.make_tables import make_table_config_files
from app.MyModule.prepare_sql import search_sql
from sqlalchemy import and_
import yaml
import json
from collections import defaultdict
from app.proccessing_data.public_methods import new_data_obj


def prepare_update(config_file_id, config_json, key_id=None, order=0, parent_id=None):
    data = make_table_config_files(config_file_id=config_file_id, key_id=key_id, raw=True)
    source_json = dict()
    for d in data:
        source_json[d['key']] = d['value']

    if config_json == source_json:
        print("no change")
        return "No Changes"

    logger.info("changing the file")
    if key_id:
        # 修改指定key_id的值
        for k, v in config_json.items():
            source_key_obj = new_data_obj(ConfigKeys, **{"id": key_id})['obj']
            if source_key_obj.name != k:
                # 主键名修改，删除source，新增k
                # delete source
                new_data_obj(PrepareTable, **{"source_config_id": config_file_id,
                                              "source_key_id": key_id,
                                              "source_version": source_key_obj.version,
                                              "action": 0,
                                              "user_id": session['SELFID']})
                # create new one
                target_key_id = f"update_key_{make_uuid()}"
                redis_db.set(target_key_id, json.dumps(config_json))
                redis_db.expire(target_key_id, 7200)
                new_data_obj(PrepareTable, **{"source_config_id": config_file_id,
                                              "target_key_id": target_key_id,
                                              "action": 2,
                                              "user_id": session['SELFID']})


            else:
                # 更新当前主键对应的value
                target_key_id = f"update_key_{make_uuid()}"
                redis_db.set(target_key_id, json.dumps(config_json))
                redis_db.expire(target_key_id, 7200)
                new_data_obj(PrepareTable, **{"source_config_id": config_file_id,
                                              "source_key_id": key_id,
                                              "source_version": source_key_obj.version,
                                              "target_key_id": target_key_id,
                                              "action": 1,
                                              "user_id": session['SELFID']})
    else:
        # 修改config整体
        for k, v in config_json.items():
            source_key_obj = new_data_obj(ConfigKeys, **{"config_file_id": config_file_id,
                                                         "name": k,
                                                         "order": order,
                                                         "status": 1,
                                                         "version": "latest",
                                                         "force_create": False})['obj']
            if source_key_obj and v != source_key_obj[k]:
                # 更新当前主键对应的value
                target_key_id = f"update_key_{make_uuid()}"
                redis_db.set(target_key_id, json.dumps(config_json))
                redis_db.expire(target_key_id, 7200)
                new_data_obj(PrepareTable, **{"source_config_id": config_file_id,
                                              "source_key_id": source_key_obj.id,
                                              "source_version": source_key_obj.version,
                                              "target_key_id": target_key_id,
                                              "action": 1,
                                              "user_id": session['SELFID']})
            else:
                # create new one
                target_key_id = f"update_key_{make_uuid()}"
                redis_db.set(target_key_id, json.dumps(config_json))
                redis_db.expire(target_key_id, 7200)
                new_data_obj(PrepareTable, **{"source_config_id": config_file_id,
                                              "target_key_id": target_key_id,
                                              "action": 2,
                                              "user_id": session['SELFID']})
            prepare_delete_keys = set(data) - set(config_json)
            for pdk in prepare_delete_keys:
                # delete source
                source_key_obj = new_data_obj(ConfigKeys, **{"config_file_id": config_file_id,
                                                             "name": pdk,
                                                             "order": order,
                                                             "status": 1,
                                                             "version": "latest",
                                                             "force_create": False})['obj']
                new_data_obj(PrepareTable, **{"source_config_id": config_file_id,
                                              "source_key_id": key_id,
                                              "source_version": source_key_obj.version,
                                              "action": 0,
                                              "user_id": session['SELFID']})


@main.route('/delete_config', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def delete_config():
    pass


@main.route('/update_config', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def update_config():
    try:
        content = request.get_json().get('content')
        config_file_id = request.get_json().get('configs_select')
        config_file_id = config_file_id.split(":")[-1].strip() if config_file_id else config_file_id
        key_id = request.get_json().get('key_id')
        key_id = key_id.split(":")[-1].strip() if key_id else key_id
        print(content, key_id)
        y = yaml.load(content)
        return_result = {"status": "OK",
                         "content": prepare_update(config_file_id=config_file_id, key_id=key_id, config_json=y)}
        return jsonify(return_result)
    except Exception as e:
        return jsonify({"status": "FAIL", "content": str(e)})


@main.route('/config_file_table', methods=['POST'])
@login_required
@permission_required(Permission.USER)
def config_file_table():
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


@main.route('/get_config_file', methods=['GET'])
@login_required
@permission_required(Permission.USER)
def get_config_file():
    key_id = request.args.get('sc_id')
    data = make_table_config_files(config_file_id=1, key_id=key_id, raw=True)
    result = dict()
    for d in data:
        result[d.get('key')] = d.get('value')
    print(result)
    result = yaml.dump(result)
    return jsonify({"status": "OK", "content": result})


def role_permission(valid_target, user_id, target_id, rights):
    pass


@main.route('/config_related', methods=['GET'])
@login_required
@permission_required(Permission.USER)
def get_config_related():
    permit_map_dict = {"NameSpaces": "PermitNamespace", "AppGroups": "PermitAppGroup", "Apps": "PermitApps"}
    try:
        id_ = request.args.get('content')
        table_name = request.args.get('table_name')
        foreign_obj = request.args.get('foreign_obj')
        obj = eval(table_name).query.get(eval(id_))
        result = [{"id": 0, "text": "请选择"}]
        for a in getattr(obj, foreign_obj):
            if getattr(a, 'validate_user')(session['SELFID']):
                result.append({"id": a.id, "text": a.name})
        return jsonify({"status": "OK", "content": result})
    except Exception as e:
        return jsonify({"status": "OK", "content": []})
