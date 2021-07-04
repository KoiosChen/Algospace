from flask import current_app
from . import db
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager
import datetime
import os
import uuid
import re
import random


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


class Permission:
    USER = 0x01
    LEADER = 0x02
    OPERATOR = 0x20
    SUPER_OPERATOR = 0x40
    ADMINISTRATOR = 0x80


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
        return False


login_manager.anonymous_user = AnonymousUser

aes_key = 'koiosr2d2c3p0000'
max_ont_down_in_sametime = 4

temp_threshold = {'min': 20, 'max': 30}
humi_threshold = {'min': 15, 'max': 70}

PermissionIP = ['127.0.0.1']

machineroom_level = {'1': '自建', '2': '缆信', '3': '第三方', '4': '城网'}

machineroom_type = {'1': '业务站', '2': '光放站'}

protect_desc_special_company = ['优刻得', '云朴']

company_regex = re.compile('|'.join(protect_desc_special_company))

PATH_PREFIX = os.path.abspath(os.path.dirname(__file__))

REQUEST_RETRY_TIMES = 1
REQUEST_RETRY_TIMES_PER_TIME = 1

FILE_URL = "http://fdfs.algospace.net"

BotHook = {"Transfer Notification": "http://mattermost.algospace.net/hooks/3akzy76ugbdi3esej4pgyou8ph"}
