#!/usr/bin/env python
import os
import multiprocessing
from app import create_app, db
from flask_script import Manager
from flask_migrate import Migrate
from app.MyModule import py_syslog
from app.MyModule import SeqPickle, SchedulerControl
from app.MyModule import AllocateQueueWork, RequestPost
from app.common import init_path, init_mailto

__author__ = 'Koios'

app = create_app(os.getenv('FLASK_CONFIG') or 'production')
manager = Manager(app)
migrate = Migrate(app, db)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1111, debug=False)
