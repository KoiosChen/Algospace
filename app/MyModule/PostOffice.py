import threading
from .. import logger, mailbox, redis_db
from .SendMail import sendmail
import traceback
import json
import time


class StartThread(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.queue = q

    def run(self):
        while True:
            __mail = self.queue.get()
            try:
                str_mail = json.dumps(__mail)
                if not redis_db.exists(str_mail):
                    redis_db.set(str_mail, 0)
                    redis_db.expire(str_mail, 3600)

                count = redis_db.get(str_mail)

                if count > 3:
                    redis_db.delete(str_mail)
                else:
                    # 若为重复发送，则罚停 n*20秒
                    time.sleep(count * 20)
                    logger.debug(f">>> Trying to send mail {__mail} in the thread")
                    distribution = sendmail(subject=__mail['subject'], mail_to=__mail['mail_to'])
                    if not distribution.send(content=__mail['content']):
                        redis_db.set(str_mail, count + 1)
                        redis_db.expire(str_mail, 3600)
                        self.queue.put(__mail)
                    else:
                        logger.debug(f'Mail sent!')
                        redis_db.delete(str_mail)
            except Exception as e:
                traceback.print_exc()
                logger.error(str(e))
            finally:
                self.queue.task_done()


def postman(thread_num=100):
    """
    用来处理邮件
    :return:
    """

    for threads_pool in range(thread_num):
        t = StartThread(mailbox)
        t.setDaemon(True)
        t.start()
