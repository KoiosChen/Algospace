from flask import jsonify, session
from app import db, logger, fdfs_client
from app.models import *
from app.validate.verify_fields import verify_fields, chain_add_validate, verify_required, verify_network, \
    verify_net_in_net
import re
import datetime
import os
import traceback
from sqlalchemy import and_
from collections import defaultdict


def upload_fdfs(file, session_name="s_upload_fdfs"):
    filename = file.filename
    extension = filename.split('.')[-1] if '.' in filename else ''
    ret = fdfs_client.upload_by_buffer(file.read(), file_ext_name=extension)
    logger.info(ret)
    fdfs_store_path = ret['Remote file_id'].decode()
    session[session_name] = {"filename": filename, "path": fdfs_store_path}
    return fdfs_store_path


def download_from_fdfs(local_filename, file_id):
    fdfs_client.timeout = 900
    return fdfs_client.download_to_file(local_filename, file_id.encode())


def new_data_obj(table, **kwargs):
    """
    创建新的数据对象
    :param table: 表名
    :param kwargs: 表数据，需要对应表字段
    :return: 新增，或者已有数据的对象
    """
    force_create = kwargs.pop('force_create') if "force_create" in kwargs.keys() else True
    logger.debug(f">>> Check the {table} for data {kwargs}")
    if isinstance(table, str):
        table_obj = eval(table)
    else:
        table_obj = table

    if kwargs.get('version') is None or (kwargs.get("version") and kwargs.get("version") != "latest"):
        __obj = table_obj.query.filter_by(**kwargs).first()
    else:
        __obj = table_obj.query.filter_by(**kwargs).order_by(table_obj.version.desc()).first()

    new_one = True
    if not __obj and force_create:
        logger.debug(f">>> The table {table.__class__.__name__} does not have the obj, create new one!")
        try:
            __obj = table(**kwargs)
            db.session.add(__obj)
            db.session.flush()
        except Exception as e:
            logger.error(f'create {table.__class__.__name__} fail {kwargs} {e}')
            traceback.print_exc()
            db.session.rollback()
            return False
    else:
        logger.debug(f">>> The line exist in {table} for {kwargs}")
        new_one = False
    return {'obj': __obj, 'status': new_one}


def table_fields(table, appends=[], removes=[]):
    original_fields = getattr(getattr(table, '__table__'), 'columns').keys()
    for a in appends:
        original_fields.append(a)
    for r in removes:
        if r in original_fields:
            original_fields.remove(r)
    return original_fields


def __make_table(fields, table, strainer=None):
    tmp = dict()
    for f in fields:
        if f == 'roles':
            tmp[f] = [get_table_data_by_id(eval(role.__class__.__name__), role.id, ['elements']) for role in
                      table.roles]
        elif f == 'role':
            try:
                tmp[f] = {"id": table.role.id, "name": table.role.name}
            except Exception as e:
                logger.error(f"get role fail {e}")
                tmp[f] = {}
        elif f == 'my_values':
            if not table.children:
                all_my_values = table.my_values.all()
                _tmp = defaultdict(list)
                for v in all_my_values:
                    _tmp[v.order].append(v)
                key_counts = set([k for k in _tmp.keys()])
                list_tmp = list()
                if len(key_counts) > 1:
                    for k in key_counts:
                        tmp_ = list()
                        for x in _tmp[k]:
                            # 去掉数值的引号
                            try:
                                xv = eval(x.value)
                                tmp_.append(xv)
                            except Exception as e:
                                print(e)
                                tmp_.append(x.value)
                        list_tmp.append(tmp_)
                else:
                    for _, value_list in _tmp.items():
                        for x in value_list:
                            # 去掉数值的引号
                            try:
                                xv = eval(x.value)
                                list_tmp = [xv]
                            except Exception as e:
                                print(e)
                                list_tmp = [x.value]
                if list_tmp:
                    tmp[f] = list_tmp if len(list_tmp) > 1 else list_tmp.pop()
                else:
                    tmp[f] = ""
            else:
                tmp[f] = {}
        elif f == 'children':
            if table.children:
                child_tmp = list()
                for child in table.children:
                    if strainer is not None:
                        if child.type == strainer[0] and child.id in strainer[1]:
                            child_tmp.extend(_make_data([child], fields, strainer))
                    else:
                        child_tmp.extend(_make_data([child], fields, strainer))
                tmp[f] = child_tmp
        elif f == 'deploy_at':
            tmp[f] = table.create_at if not table.update_at else table.update_at
        elif f == 'issue_user':
            tmp[f] = table.issue_user.username if table.issue_user_id else ""
        elif f == 'apply_user':
            tmp[f] = table.apply_user.username if table.apply_user_id else ""
        elif f == 'issued_version':
            tmp[f] = table.related_apps[0].version
        elif f == 'owner':
            if table.__class__.__name__ == 'NameSpaces':
                tmp[f] = [pn.owner.username for pn in PermitNamespace.query.filter_by(namespace_id=table.id).all()]
            elif table.__class__.__name__ == 'AppGroups':
                tmp[f] = [pn.owner.username for pn in PermitAppGroup.query.filter_by(app_group_id=table.id).all()]
        elif f == 'owner_id':
            if table.__class__.__name__ == 'NameSpaces':
                tmp[f] = [pn.owner.id for pn in PermitNamespace.query.filter_by(namespace_id=table.id).all()]
            elif table.__class__.__name__ == 'AppGroups':
                tmp[f] = [pn.owner.id for pn in PermitAppGroup.query.filter_by(app_group_id=table.id).all()]
        elif f == 'related_strategies':
            tmp[f] = [ag.name for ag in table.app_groups]
        elif f == 'related_namespace_id':
            tmp[f] = [n.id for n in table.related_namespaces]
        elif f == 'related_namespaces':
            tmp[f] = [n.name for n in table.related_namespaces]
        elif f == 'objects':
            tmp1 = list()
            t1 = getattr(table, f)
            for value in t1:
                if value.thumbnails:
                    tmp1.append({'id': value.id, 'url': value.url, 'obj_type': value.obj_type,
                                 'thumbnail': {'id': value.thumbnails[0].id,
                                               'url': value.thumbnails[0].url,
                                               'obj_type': value.thumbnails[0].obj_type}})
                else:
                    tmp1.append({'id': value.id, 'url': value.url, 'obj_type': value.obj_type})
            tmp1.sort(key=lambda x: x["obj_type"], reverse=True)
            tmp[f] = tmp1
        else:
            r = getattr(table, f)
            if isinstance(r, int) or isinstance(r, float):
                tmp[f] = r
            elif r is None:
                tmp[f] = ''
            else:
                tmp[f] = str(r)
    return tmp


def _make_data(data, fields, strainer=None):
    rr = list()
    for t in data:
        rr.append(__make_table(fields, t, strainer))
    return rr


def _search(table, fields, search):
    and_fields_list = list()
    for k, v in search.items():
        if k in fields:
            if k in ('delete_at', 'used_at') and v is None:
                and_fields_list.append(getattr(getattr(table, k), '__eq__')(v))
            elif k in ('manager_customer_id', 'owner_id') and v:
                and_fields_list.append(getattr(getattr(table, k), '__eq__')(v))
            elif k in ('validity_at', 'end_at') and v is not None:
                and_fields_list.append(getattr(getattr(table, k), '__ge__')(v))
            elif k == 'start_at' and v is not None:
                and_fields_list.append(getattr(getattr(table, k), '__le__')(v))
            elif k == 'pay_at' and v == 'not None':
                and_fields_list.append(getattr(getattr(table, k), '__ne__')(None))
            else:
                and_fields_list.append(getattr(getattr(table, k), 'contains')(v))
    return and_fields_list


def _advance_search(table, fields, advance_search):
    and_fields_list = list()

    for search in advance_search:
        keys = search['key'].split('.')
        tmp_table = table
        for k in keys:
            if hasattr(tmp_table, k):
                tmp_table = getattr(tmp_table, k)
            else:
                logger.error(f"{tmp_table} has no attribute {k}")
        attr_key = tmp_table
        and_fields_list.append(getattr(attr_key, search['operator'])(search['value']))
    return and_fields_list


def get_table_data(table, args, appends=[], removes=[], advance_search=None, order_by=None):
    page = args.get('page')
    current = args.get('current')
    size = args.get('size')
    search = args.get('search')
    fields = table_fields(table, appends, removes)
    table_name = table.__name__
    if 'parent_id' in fields and table_name == 'Elements':
        base_sql = table.query.filter(table.parent_id.__eq__(None))
    else:
        base_sql = table.query

    if isinstance(current, int) and current <= 0:
        return False

    filter_args = list()
    if search:
        filter_args.extend(_search(table, fields, search))
        if advance_search is not None:
            filter_args.extend(_advance_search(table, fields, advance_search))
        search_sql = base_sql.filter(and_(*filter_args))
    else:
        if advance_search is not None:
            filter_args.extend(_advance_search(table, fields, advance_search))
            search_sql = base_sql.filter(and_(*filter_args))
        else:
            search_sql = base_sql

    if order_by is not None:
        search_sql = search_sql.order_by(getattr(getattr(table, order_by), "desc")())

    page_len = search_sql.count()
    if page != 'true':
        table_data = search_sql.all()
    else:
        if page_len < (current - 1) * size:
            current = 1
        table_data = search_sql.offset((current - 1) * size).limit(size).all()

    # if page != 'true':
    #     if search:
    #         filter_args = list()
    #         filter_args.extend(_search(table, fields, search))
    #         if advance_search is not None:
    #             filter_args.extend(_advance_search(table, fields, advance_search))
    #         table_data = base_sql.filter(and_(*filter_args)).all()
    #         page_len = len(table_data)
    #     else:
    #         table_data = base_sql.all()
    # else:
    #     if search:
    #         filter_args = list()
    #         filter_args.extend(_search(table, fields, search))
    #         if advance_search is not None:
    #             filter_args.extend(_advance_search(table, fields, advance_search))
    #         table_data = base_sql.filter(and_(*filter_args)).offset((current - 1) * size).limit(size).all()
    #         page_len = base_sql.filter(and_(*filter_args)).count()
    #     else:
    #         if current > 0:
    #             table_data = base_sql.offset((current - 1) * size).limit(size).all()
    #         else:
    #             return False

    r = _make_data(table_data, fields)

    if table.__name__ == 'Elements':
        pop_list = list()
        for record in r:
            if record.get('parent_id'):
                pop_list.append(record)
        for p in pop_list:
            r.remove(p)

    return {"records": r, "total": page_len, "size": size, "current": current} if page == 'true' else {"records": r}


def get_table_data_by_id(table, key_id, appends=[], removes=[], strainer=None, search=None, advance_search=None):
    fields = table_fields(table, appends, removes)
    base_sql = table.query
    if search is None and advance_search is None:
        t = base_sql.get(key_id)
    elif advance_search is not None:
        filter_args = _advance_search(table, fields, advance_search)
        filter_args.append(getattr(getattr(table, 'id'), '__eq__')(key_id))
        t = base_sql.filter(and_(*filter_args)).first()
    else:
        filter_args = _search(table, fields, search)
        filter_args.append(getattr(getattr(table, 'id'), '__eq__')(key_id))
        t = base_sql.filter(and_(*filter_args)).first()
    if t:
        return __make_table(fields, t, strainer)
    else:
        return {}
