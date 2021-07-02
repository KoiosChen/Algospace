from . import db, logger, redis_db


def success_return(data="", msg=""):
    return {"code": "success", "data": data, "msg": msg}


def false_return(data="", msg=""):
    return {"code": "false", "data": data, "msg": msg}


def exp_return(data="", msg=""):
    return {"code": "exp", "data": data, "msg": msg}


def db_commit():
    try:
        db.session.commit()
        return success_return("", "db commit success")
    except Exception as e:
        logger.error(f"db commit error for {e}")
        db.session.rollback()
        return false_return("", f"db commit fail for {e}")


def init_mailto():
    """
    默认mail_to whnoc@nbl.net.cn，mail_bcc: chenjinzhang@nbl.net.cn
    """
    if not redis_db.exists('mail_to'):
        redis_db.lpush("mail_to", "whnoc@nbl.net.cn")
    if not redis_db.exists('mail_bcc'):
        redis_db.lpush("mail_bcc", "chenjinzhang@nbl.net.cn")
