import threading
import traceback

from .. import logger, mailbox, redis_db
import json
import uuid
import os
from .SendMail import sendmail
impor traceback


class StartThread(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.queue = q

    def run(self):
        while True:
            __mail = self.queue.get()
            try:
                logger.debug(f">>> Trying to send mail {__mail} in the thread")

                distribution = sendmail(subject=__mail['subject'], mail_to=__mail['mail_to'])
                distribution.send(content=__mail['content'])

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
