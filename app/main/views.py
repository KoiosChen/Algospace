from flask import session, render_template, jsonify
from flask_login import login_required
from ..models import *
from ..decorators import permission_required
from .. import logger
from . import main
import json
import os



IGNORED_FILES = set(['.gitignore'])


@main.route('/', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.FOLLOW)
def index():
    return render_template("/dashboard.html")


@main.route('/all_user', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def all_user():
    logger.info('User {} is getting all user dictionary'.format(session['LOGINNAME']))
    all_user = User.query.filter(User.status.__eq__(1), User.phoneNum.__ne__(None)).all()
    all_user_dict = {}
    for user in all_user:
        all_user_dict[user.id] = {'username': user.username, 'phoneNum': user.phoneNum}

    return jsonify(json.dumps(all_user_dict))
