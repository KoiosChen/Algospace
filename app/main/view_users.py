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


@main.route('/users_manager', methods=['GET'])
@login_required
@permission_required(Permission.USER)
def users_manager():
    return render_template('users_manager.html')