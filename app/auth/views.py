from flask import render_template, redirect, request, url_for, flash, session, jsonify, json
from flask_login import login_user, logout_user, login_required
from ..models import User, Area
from . import auth
from .. import logger
from ldap3 import Server, Connection, SUBTREE, SAFE_SYNC
from ldap3.extend.microsoft.addMembersToGroups import ad_add_members_to_groups as addUsersInGroups

ldap_host = '10.21.90.10'  # ldap服务器地址
ldap_port = 389  # 默认389
ldap_base_search = 'ou=Users,ou=Office,dc=algospace,dc=org'  # 查询域


def ldap_auth(username, password):
    '''
    ldap验证方法
    :param username: 用户名
    :param password: 密码
    :return:
    '''

    server = Server(ldap_host, port=ldap_port, use_ssl=False)
    ldapz_admin_connection = Connection(server, user='ALGOSPACE\\ldap_bind', password='Tmp12345', auto_bind=True, authentication='NTLM')
    print(ldapz_admin_connection)

    # 这个是为了查询你输入的用户名的入口搜索地址
    res = ldapz_admin_connection.search(search_base=ldap_base_search,
                                        search_filter='(sAMAccountName={})'.format(username),
                                        search_scope=SUBTREE,
                                        attributes=['cn', 'givenName', 'mail', 'sAMAccountName'],
                                        )

    try:
        if res:
            entry = ldapz_admin_connection.response[0]
            logger.info(entry)
            dn = entry['dn']
            attr_dict = entry['attributes']
            logger.info('attr_dic:%s' % attr_dict)

            try:
                # 这个connect是通过你的用户名和密码还有上面搜到的入口搜索来查询的
                conn2 = Connection(server, user=dn, password=password, check_names=True, lazy=False, raise_exceptions=False)
                conn2.bind()
                # logger.info(conn2.result["description"])

                # 正确-success 不正确-invalidCredentials
                if conn2.result["description"] == "success":
                    logger.info("ldap auth pass!")
                    logger.info(attr_dict)
                    return attr_dict
                else:
                    logger.info("username or password error!")
                    return False
            except Exception as e:
                logger.info("username or password error!")
                logger.info(e)
                return False
    except KeyError as e:
        logger.info("username or password error!")
        logger.info(e)
        return False


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')
        logger.warning('Somebody is trying to login as {}'.format(fullname))
        user = User.query.filter_by(username=fullname, status=1).first()
        result = ldap_auth(fullname, password)
        if result:
            session.permanent = True
            logger.warning('Username is {}'.format(user.username))
            session['LOGINUSER'] = result['sAMAccountName']
            session['LOGINNAME'] = result['givenName']
            session['SELFEMAIL'] = result['mail']
            session['ROLE'] = user.role_id
            session['DUTY'] = user.duty
            session['SELFID'] = user.id
            login_user(user, remember_me)
            return redirect(request.args.get('next') or url_for('main.index'))
        logger.warning('This email is not existed')
        flash('用户名密码错误')
        return jsonify({'status': 'ok', 'content': 'got files'})
    elif request.method == 'GET':
        return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    logger.warning('User {} logout'.format(session.get('LOGINNAME')))
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('.login'))
