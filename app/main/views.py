from flask import session, render_template, jsonify
from flask_login import login_required
from ..models import *
from ..decorators import permission_required
from .. import logger
from . import main
import json


@main.route('/', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.USER)
def index():
    return render_template("/dashboard.html")
