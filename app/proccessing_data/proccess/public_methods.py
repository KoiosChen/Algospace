from flask import jsonify, session
from app import db, logger, fdfs_client
from ...models import *
from ...validate.verify_fields import verify_fields, chain_add_validate, verify_required, verify_network, \
    verify_net_in_net
import re
import datetime
import os
import traceback


def upload_fdfs(file):
    filename = file.filename
    extension = filename.split('.')[-1] if '.' in filename else ''
    ret = fdfs_client.upload_by_buffer(file.read(), file_ext_name=extension)
    logger.info(ret)
    fdfs_store_path = ret['Remote file_id'].decode()
    session["s_upload_fdfs"] = {"filename": filename, "path": fdfs_store_path}
    return fdfs_store_path


def new_data_obj(table, **kwargs):
    """
    创建新的数据对象
    :param table: 表名
    :param kwargs: 表数据，需要对应表字段
    :return: 新增，或者已有数据的对象
    """
    logger.debug(f">>> Check the {table} for data {kwargs}")
    __obj = eval(table).query.filter_by(**kwargs).first()
    new_one = True
    if not __obj:
        logger.debug(f">>> The table {table} does not have the obj, create new one!")
        try:
            __obj = eval(table)(**kwargs)
            db.session.add(__obj)
            db.session.flush()
        except Exception as e:
            logger.error(f'create {table} fail {kwargs} {e}')
            traceback.print_exc()
            db.session.rollback()
            return False
    else:
        logger.debug(f">>> The line exist in {table} for {kwargs}")
        new_one = False
    return {'obj': __obj, 'status': new_one}
