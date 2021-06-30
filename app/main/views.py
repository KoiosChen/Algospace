from flask import redirect, session, url_for, render_template, flash, request, jsonify, send_from_directory
from flask_login import login_required
from ..models import *
from ..decorators import permission_required
from .. import db, logger, scheduler
from .forms import AreaConfigForm, AreaModal
from . import main
import time
from ..MyModule import OperateDutyArrange
from ..MyModule.UploadFile import uploadfile
from werkzeug.utils import secure_filename
import json
from bs4 import BeautifulSoup
import datetime
import os
import re
import requests


def get_device_info(machine_room_id):
    """
    :param machine_room_id:
    :return:
    """
    device_info = Device.query.filter_by(machine_room_id=machine_room_id).all()
    logger.debug('device list: {} '.format(device_info))
    return device_info if device_info else False


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def gen_file_name(filename, path=UPLOAD_FOLDER):
    """
    If file was exist already, rename it and return a new name
    """

    i = 1
    while os.path.exists(os.path.join(path, filename)):
        name, extension = os.path.splitext(filename)
        filename = '%s_%s%s' % (name, str(i), extension)
        i += 1

    return filename


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


@main.route('/gps_location', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.NETWORK_MANAGER)
def gps_location():
    return render_template('GPS.html')

