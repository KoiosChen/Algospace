from flask import current_app
from . import db
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint
from . import login_manager
import datetime
import os
import bleach
import uuid
import re
import random


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    REGION_SUPPORT = 0x10
    MAN_ON_DUTY = 0x20
    NETWORK_MANAGER = 0x40
    ADMINISTER = 0x80


class TransferOrders(db.Model):
    __tablename__ = 'transfer_orders'
    id = db.Column(db.String(64), primary_key=True, default=make_order_id)
    filename = db.Column(db.String(100), index=True)
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


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'REGION': (Permission.FOLLOW |
                       Permission.COMMENT |
                       Permission.WRITE_ARTICLES |
                       Permission.MODERATE_COMMENTS |
                       Permission.REGION_SUPPORT, False),
            'MAN_ON_DUTY': (Permission.FOLLOW |
                            Permission.COMMENT |
                            Permission.WRITE_ARTICLES |
                            Permission.MODERATE_COMMENTS |
                            Permission.REGION_SUPPORT |
                            Permission.MAN_ON_DUTY, False),
            'SNOC': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES |
                     Permission.MODERATE_COMMENTS |
                     Permission.REGION_SUPPORT |
                     Permission.MAN_ON_DUTY |
                     Permission.NETWORK_MANAGER, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    alarm_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)
    line_id = db.Column(db.Integer, db.ForeignKey('line_data_bank.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']
        attrs = {
            '*': ['class'],
            'a': ['href', 'rel'],
            'img': ['src', 'alt', 'width', 'height'],
        }
        target.body_html = bleach.clean(value, tags=allowed_tags, attributes=attrs, strip=True)


db.event.listen(Post.body, 'set', Post.on_changed_body)


class ApiConfigure(db.Model):
    __tablename__ = 'api_configure'
    id = db.Column(db.Integer, primary_key=True)
    api_name = db.Column(db.String(20), nullable=False)
    api_params = db.Column(db.String(100), nullable=False)
    api_params_value = db.Column(db.String(200))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    phoneNum = db.Column(db.String(15), unique=True)
    username = db.Column(db.String(64), index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    area = db.Column(db.Integer, db.ForeignKey('area.id'))
    duty = db.Column(db.Integer, db.ForeignKey('job_desc.job_id'))
    permit_machine_room = db.Column(db.String(200), index=True)
    password_hash = db.Column(db.String(128))
    status = db.Column(db.SmallInteger)
    post = db.relationship('Post', backref='author', lazy='dynamic')
    lines = db.relationship('LineDataBank', backref='operator', lazy='dynamic')
    supplier = db.relationship('IPSupplier', backref='supplier_operator', lazy='dynamic')
    sms_order = db.relationship('SMSOrder', backref='sms_sender', lazy='dynamic')
    applied_orders = db.relationship('TransferOrders', backref='apply_user',
                                     foreign_keys='TransferOrders.apply_user_id',
                                     lazy='dynamic')
    confirmed_orders = db.relationship('TransferOrders', backref='confirm_user',
                                       foreign_keys='TransferOrders.confirm_user_id',
                                       lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

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
        return self.can(Permission.ADMINISTER)

    def is_moderate(self):
        return self.can(Permission.MODERATE_COMMENTS)

    def is_region(self):
        return self.can(Permission.REGION_SUPPORT)

    def is_manonduty(self):
        return self.can(Permission.MAN_ON_DUTY)

    def is_snoc(self):
        return self.can(Permission.NETWORK_MANAGER)

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
