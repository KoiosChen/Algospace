from flask import current_app
from . import db
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint
from . import login_manager
import datetime
import os
import uuid
import re
import random
import json


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


def make_uuid():
    return str(uuid.uuid4())


def make_order_id(prefix=None):
    """
    生成订单号
    :return:
    """
    date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # 生成4为随机数作为订单号的一部分
    random_str = str(random.randint(1, 9999))
    random_str = random_str.rjust(4, '0')
    rtn = '%s%s' % (date, random_str)
    return rtn if prefix is None else prefix + rtn


transfer_sendto = db.Table('transfer_sendto',
                           db.Column('transfer_order_id', db.String(64), db.ForeignKey('transfer_orders.id'),
                                     primary_key=True),
                           db.Column('user_id', db.Integer, db.ForeignKey('users.id'),
                                     primary_key=True))

apps_configs = db.Table('apps_configs',
                        db.Column('app_id', db.String(64), db.ForeignKey('apps.id'),
                                  primary_key=True),
                        db.Column('config_id', db.String(64), db.ForeignKey('config_files.id'),
                                  primary_key=True))

namespace_appgroup = db.Table('namespace_appgroup',
                              db.Column('namespace_id', db.String(64), db.ForeignKey('namespaces.id'),
                                        primary_key=True),
                              db.Column('appgroup_id', db.String(64), db.ForeignKey('app_groups.id'),
                                        primary_key=True)
                              )

apps_bundle_configs = db.Table('apps_bundle_configs',
                               db.Column('app_id', db.String(64), db.ForeignKey('apps.id'),
                                         primary_key=True),
                               db.Column('bundle_configs_id', db.String(64), db.ForeignKey('bundle_configs.id'),
                                         primary_key=True))


class Permission:
    USER = 0x01
    LEADER = 0x02
    OPERATOR = 0x20
    SUPER_OPERATOR = 0x40
    ADMINISTRATOR = 0xff


class FileTypes(db.Model):
    """
    文件类型
    """
    __tablename__ = 'file_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, index=True)
    order = db.Column(db.SmallInteger, default=1, index=True, comment='当有排序时')
    permit_value = db.Column(db.String(200), index=True)


class ApplyTypes(db.Model):
    """
    申请类型
    """
    __tablename__ = 'apply_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, index=True)
    desc = db.Column(db.String(200))
    order = db.Column(db.SmallInteger, default=1, index=True, comment='当有排序时')
    permit_value = db.Column(db.String(200), index=True)
    transfer_orders = db.relationship("TransferOrders", backref='apply_type', lazy='dynamic')


class TransferOrders(db.Model):
    __tablename__ = 'transfer_orders'
    id = db.Column(db.String(64), primary_key=True, default=make_order_id)
    filename = db.Column(db.String(100), index=True)
    apply_type_id = db.Column(db.Integer, db.ForeignKey("apply_types.id"))
    apply_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), comment='申请人')
    apply_at = db.Column(db.DateTime, default=datetime.datetime.now)
    apply_reason = db.Column(db.String(200), comment='申请理由')
    email = db.Column(db.String(50), comment='申请人邮箱')
    file_store_path = db.Column(db.String(100), index=True)
    confirm_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), comment='审核人')
    confirm_result = db.Column(db.SmallInteger, comment="0：拒绝，1：通过")
    confirm_reason = db.Column(db.String(200), comment="通过、拒绝理由")
    confirm_at = db.Column(db.DateTime)
    delete_at = db.Column(db.DateTime)

    sendto = db.relationship('Users', secondary=transfer_sendto, backref=db.backref('send_me_transfer_orders'))


class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('Users', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.USER, True),
            'Leader': (Permission.USER |
                       Permission.LEADER, False),
            'Operator': (Permission.USER |
                         Permission.LEADER |
                         Permission.OPERATOR, False),
            'SuperOperator': (Permission.USER |
                              Permission.LEADER |
                              Permission.OPERATOR |
                              Permission.SUPER_OPERATOR, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Roles.query.filter_by(name=r).first()
            if role is None:
                role = Roles(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    phoneNum = db.Column(db.String(15), unique=True)
    username = db.Column(db.String(64), index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    permit_file_type = db.Column(db.String(200), index=True)
    password_hash = db.Column(db.String(128))
    status = db.Column(db.SmallInteger)
    applied_orders = db.relationship('TransferOrders', backref='apply_user',
                                     foreign_keys='TransferOrders.apply_user_id',
                                     lazy='dynamic')
    confirmed_orders = db.relationship('TransferOrders', backref='confirm_user',
                                       foreign_keys='TransferOrders.confirm_user_id',
                                       lazy='dynamic')

    applied_bundle_config_orders = db.relationship('BundleConfigs', backref='apply_user',
                                                   foreign_keys='BundleConfigs.apply_user_id',
                                                   lazy='dynamic')

    confirmed_bundle_config_orders = db.relationship('BundleConfigs', backref='issue_user',
                                                     foreign_keys='BundleConfigs.issue_user_id',
                                                     lazy='dynamic')

    permitted_namespaces = db.relationship('PermitNamespace', backref='owner', lazy="dynamic",
                                           foreign_keys='PermitNamespace.user_id')

    permitted_app_groups = db.relationship('PermitAppGroup', backref='owner', lazy="dynamic",
                                           foreign_keys='PermitAppGroup.user_id')

    permitted_apps = db.relationship('PermitApp', backref='owner', lazy="dynamic",
                                     foreign_keys='PermitApp.user_id')
    permitted_configs = db.relationship('PermitConfig', backref='owner', lazy="dynamic",
                                        foreign_keys='PermitConfig.user_id')

    def __init__(self, **kwargs):
        super(Users, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Roles.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Roles.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTRATOR)

    def is_super_operator(self):
        return self.can(Permission.SUPER_OPERATOR)

    def is_operator(self):
        return self.can(Permission.OPERATOR)

    def is_leader(self):
        return self.can(Permission.LEADER)

    def is_user(self):
        return self.can(Permission.USER)

    def __repr__(self):
        return '<User %r>' % self.username


class TokenRecord(db.Model):
    __tablename__ = 'token_record'
    unique_id = db.Column(db.String(128), primary_key=True)
    token = db.Column(db.String(512), nullable=False)
    expire = db.Column(db.String(10))
    create_time = db.Column(db.DateTime)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return self.can(Permission.ADMINISTRATOR)

    def is_operator(self):
        return self.can(Permission.OPERATOR)


class NameSpaces(db.Model):
    __tablename__ = "namespaces"
    id = db.Column(db.String(64), primary_key=True, default=make_uuid)
    name = db.Column(db.String(128), index=True, comment="name")
    app_groups = db.relationship('AppGroups', secondary=namespace_appgroup, backref=db.backref('related_namespaces'))
    permit_namespace_id = db.relationship("PermitNamespace", backref='permitted_namespace', lazy='dynamic',
                                          foreign_keys="PermitNamespace.namespace_id")

    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    update_at = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    delete_at = db.Column(db.DateTime)

    def validate_user(self, user_id):
        if PermitNamespace.query.filter_by(user_id=user_id, namespace_id=self.id).first():
            return True
        else:
            return False


class AppGroups(db.Model):
    __tablename__ = "app_groups"
    id = db.Column(db.String(64), primary_key=True, default=make_uuid)
    name = db.Column(db.String(128), index=True, comment="应用组名称")
    desc = db.Column(db.String(500), comment="应用组描述")
    apps = db.relationship("Apps", backref="app_group", lazy="dynamic")
    local_path = db.Column(db.String(100), comment='本地挂载目录用于解压')
    dryrun_path = db.Column(db.String(100), comment='dryrun 测试的解压路径')
    permit_app_group_id = db.relationship("PermitAppGroup", backref='permitted_app_group', lazy='dynamic',
                                          foreign_keys="PermitAppGroup.app_group_id")

    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    update_at = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    delete_at = db.Column(db.DateTime)

    def validate_user(self, user_id):
        if PermitAppGroup.query.filter_by(user_id=user_id, app_group_id=self.id).first():
            return True
        else:
            return False


class Apps(db.Model):
    __tablename__ = "apps"
    id = db.Column(db.String(64), primary_key=True, default=make_uuid)
    name = db.Column(db.String(128), index=True, comment="应用名称")
    desc = db.Column(db.String(500), comment="应用描述")
    app_group_id = db.Column(db.String(64), db.ForeignKey('app_groups.id'))
    base_path = db.Column(db.String(64), comment='本地挂载路径')

    version = db.Column(db.SmallInteger, comment="应用发布的版本")
    status = db.Column(db.SmallInteger, default=0, comment='0 待发布 1 已发布  2 作废')

    configurations = db.relationship('ConfigFiles', secondary=apps_configs, backref=db.backref('related_apps'))

    bundle_configurations = db.relationship('BundleConfigs', secondary=apps_bundle_configs,
                                            backref=db.backref('related_apps'))

    permit_app_id = db.relationship("PermitApp", backref='permitted_app', lazy='dynamic',
                                    foreign_keys="PermitApp.app_id")

    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    update_at = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    delete_at = db.Column(db.DateTime)

    def validate_user(self, user_id):
        if PermitApp.query.filter_by(user_id=user_id, app_id=self.id).first():
            return True
        else:
            return False


class ConfigFiles(db.Model):
    __tablename__ = 'config_files'
    id = db.Column(db.String(64), primary_key=True, default=make_uuid)
    name = db.Column(db.String(128), index=True, comment="配置文件名称")
    desc = db.Column(db.String(500), comment="配置文件描述")
    my_keys = db.relationship("ConfigKeys", backref='config_file', lazy='dynamic')
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    update_at = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    delete_at = db.Column(db.DateTime)

    permit_config_id = db.relationship("PermitConfig", backref='permitted_config', lazy='dynamic',
                                       foreign_keys="PermitConfig.config_id")


class ConfigKeys(db.Model):
    __tablename__ = 'config_keys'
    id = db.Column(db.String(64), primary_key=True, default=make_uuid)
    name = db.Column(db.String(128), index=True, comment="主键名称")
    key_type = db.Column(db.String(10), index=True, comment="straight, list, dict, obj")
    value_type = db.Column(db.String(10), index=True, comment="str, int, float, datetime, bool, list, dict, obj")
    order = db.Column(db.SmallInteger, index=True, comment="用于将一组key放到一个dict中，不同的index不能重复，组成一个list")
    idx = db.Column(db.SmallInteger, index=True, comment="list中元素的顺序")
    is_template = db.Column(db.SmallInteger, default=0)
    required = db.Column(db.SmallInteger, default=0, comment="是否为必填")
    config_file_id = db.Column(db.String(64), db.ForeignKey('config_files.id'))
    status = db.Column(db.SmallInteger, index=True, default=1, comment='1, 已发布；2，提交未发布；3，失效可回退')
    version = db.Column(db.String(50), index=True, comment="key的版本号")
    my_values = db.relationship("ConfigValues", backref='config_key', lazy='dynamic')

    parent_id = db.Column(db.String(64), db.ForeignKey('config_keys.id'))
    parent = db.relationship('ConfigKeys', backref="children", remote_side=[id])

    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    update_at = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    delete_at = db.Column(db.DateTime)


class ConfigValues(db.Model):
    __tablename__ = 'config_values'
    id = db.Column(db.String(64), primary_key=True, default=make_uuid)
    value = db.Column(db.String(128), index=True, comment="对应的值")
    value_type = db.Column(db.String(10), index=True, comment="int, float, str, datetime")
    order = db.Column(db.SmallInteger, index=True, default=0, comment='list嵌套list时，按照order值来归类')
    status = db.Column(db.SmallInteger, index=True, comment='1, 已发布；2，提交未发布；0，失效可回退')
    version = db.Column(db.String(50), index=True, comment="值的版本号")
    config_key_id = db.Column(db.String(64), db.ForeignKey('config_keys.id'))
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    update_at = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    delete_at = db.Column(db.DateTime)


class PermitNamespace(db.Model):
    __tablename__ = "permit_namespace"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    namespace_id = db.Column(db.String(64), db.ForeignKey('namespaces.id'), primary_key=True)
    permission = db.Column(db.String(8), default='0x00', comment="0x00: None, 0x01: read, 0x02: all")


class PermitAppGroup(db.Model):
    __tablename__ = "permit_app_groups"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    app_group_id = db.Column(db.String(64), db.ForeignKey('app_groups.id'), primary_key=True)

    permission = db.Column(db.String(8), default='0x00', comment="0x00: None, 0x01: read, 0x02: all")


class PermitApp(db.Model):
    __tablename__ = "permit_app"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    app_id = db.Column(db.String(64), db.ForeignKey('apps.id'), primary_key=True)

    permission = db.Column(db.String(8), default='0x00', comment="0x00: None, 0x01: read, 0x02: all")


class PermitConfig(db.Model):
    __tablename__ = "permit_config"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    config_id = db.Column(db.String(64), db.ForeignKey('config_files.id'), primary_key=True)

    permission = db.Column(db.String(8), default='0x00', comment="0x00: None, 0x01: read, 0x02: all")


class PrepareTable(db.Model):
    __tablename__ = "prepare_table"
    id = db.Column(db.String(64), primary_key=True, default=make_uuid)
    source_config_id = db.Column(db.String(64), db.ForeignKey('config_files.id'))
    source_key_id = db.Column(db.String(64), db.ForeignKey('config_keys.id'))
    source_version = db.Column(db.SmallInteger, comment='源配置的版本')
    target_key_id = db.Column(db.String(70), comment='redis中的主键')
    action = db.Column(db.SmallInteger, comment='0: delete, 1: update 2: new one')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    update_at = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    delete_at = db.Column(db.DateTime)


class BundleConfigs(db.Model):
    __tablename__ = 'bundle_configs'
    id = db.Column(db.String(64), primary_key=True, default=make_order_id)
    filename = db.Column(db.String(100), index=True)
    version = db.Column(db.SmallInteger, index=True, comment='若生效则使用这个版本，更新到apps的version字段')
    deploy_reason = db.Column(db.String(200), comment='发布说明')
    uncompress_to = db.Column(db.String(100), comment='解压缩路径, 拼接namespace，strategy_name, instance_name')

    apply_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), comment='申请人')
    apply_at = db.Column(db.DateTime, default=datetime.datetime.now)

    file_store_path = db.Column(db.String(100), index=True, comment="更新文件存放在fdfs中")
    status = db.Column(db.SmallInteger, index=True, default=1, comment='1, 提交未发布；2，已发布；3，已过期')
    issue_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), comment='审核人')
    issue_result = db.Column(db.SmallInteger, comment="0：拒绝，1：通过")
    issue_reason = db.Column(db.String(200), comment="通过、拒绝理由")
    issue_at = db.Column(db.DateTime)

    token = db.Column(db.String(64), unique=True, comment='预留，用于API获取此配置文件')

    update_at = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    delete_at = db.Column(db.DateTime)


login_manager.anonymous_user = AnonymousUser

aes_key = 'koiosr2d2c3p0000'

PermissionIP = ['127.0.0.1']

PATH_PREFIX = os.path.abspath(os.path.dirname(__file__))

REQUEST_RETRY_TIMES = 1
REQUEST_RETRY_TIMES_PER_TIME = 1

FILE_URL = "http://fdfs.algospace.net"

BotHook = {"Transfer Notification": "http://mattermost.algospace.net/hooks/3akzy76ugbdi3esej4pgyou8ph"}

result_dict = {0: "拒绝", 1: "通过"}
