from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors, transfer, ajax_transfer, namespace_manage, manage_config, ajax_load_config, ajax_base_env, \
    strategy_manage
