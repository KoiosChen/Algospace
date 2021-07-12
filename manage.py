#!/usr/bin/env python
import os
from app import create_app, db
from flask_script import Manager
from flask_migrate import Migrate
from app.MyModule import PostOffice

__author__ = 'Koios'

app = create_app(os.getenv('FLASK_CONFIG') or 'development')
manager = Manager(app)
migrate = Migrate(app, db)

PostOffice.postman(thread_num=1)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1111, debug=False)
